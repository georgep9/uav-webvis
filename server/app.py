from flask import Flask, jsonify, request
from flask_cors import CORS
from waitress import serve
import boto3
from boto3.dynamodb.conditions import Key
import simplejson as json
from decimal import Decimal
import logging
import random
import time

app = Flask(__name__)
CORS(app)

logger = logging.getLogger('waitress')
logger.setLevel(logging.DEBUG)

ttl_min = 5 # time to live in minutes
query_lim_max = 100 # max db items to query


@app.route('/')
def hw():
    return "<h1>Hello, world</h1>"


# convert db items list to 
# json response for front-end
def process_json_res(db_items):
    samples = []
    for item in db_items:
        ts = item["timestamp"]
        sensors = {}
        for sensor in item.keys():
            if sensor != "timestamp" \
            and sensor != "data_type" \
            and sensor != "ttl":
                sensors[sensor] = {'val': item[sensor]} 
        sample = {'ts': ts, 'sensors': sensors}
        samples.append(sample)

    response = json.dumps(samples)
    length = len(samples)
    return (response, length)


@app.route('/api/aq/live', methods=['GET'])
def get_aq_live():
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table("uav_wvi")

    try:
        query_limit = 1
        from_ts = 0

        from_ts_arg = request.args.get('from_ts')
        if from_ts_arg is not None:
            from_ts = int(from_ts_arg)
            query_limit = query_lim_max
        
        db_res = table.query(
            KeyConditionExpression=
                Key('data_type').eq("air_quality") &
                Key('timestamp').gt(from_ts),
            ScanIndexForward=False,
            Limit=query_limit)
        db_items = reversed(db_res["Items"])
        
        json_res, length = process_json_res(db_items)
        print('[GET /api/aq/live] Serving ' + str(length) + " samples.")
        return json_res

    except ValueError as e:
        print(e)
        return json.dumps("[ERR] Argument 'from_ts' must be an integer of unix time.")

    except Exception as e:
        print(e)
        return json.dumps("[ERR] Execption caught while querying database.")


@app.route('/api/aq/sen', methods=['GET'])
def get_aq_sen():
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table("uav_wvi")

    sensor = request.args.get('sensor')
    samples = request.args.get('samples')

    if samples is None or sensor is None:
        return json.dumps("[ERR] Must provide 'sensor' and 'samples' argument.")

    try:
        samples = int(samples)
        if samples < 1 or samples > 500: raise Exception
    except:
        return json.dumps("[ERR] Argument 'samples' must be an integer between 1 and 500.")

    try:
        db_res = table.query(
            ProjectionExpression="#ts, #sen",
            ExpressionAttributeNames={"#ts": "timestamp", "#sen": sensor},
            KeyConditionExpression=Key('data_type').eq("air_quality"),
            ScanIndexForward=False,
            Limit=samples)
        db_items = reversed(db_res["Items"])

        json_res, length = process_json_res(db_items)
        print('[GET /api/aq/sen] Serving ' + str(length) + " samples for " + sensor + ".")
        return json_res

    except Exception as e:
        print(e)
        return json.dumps("[ERR] Execption caught while querying database.")


@app.route('/api/aq', methods=["POST"])
def post_aq():

    post_json = json.loads(request.get_json())

    if "ts" not in post_json and "data" not in post_json:
        return json.dumps("[ERR] Bad format.")

    ts = post_json["ts"]
    sensors = post_json["data"]
    ttl = {'ttl': int(time.time()) + 60 * ttl_min}

    new_db_item = {"data_type": "air_quality", "timestamp": ts}
    new_db_item.update(sensors)
    new_db_item.update(ttl)
    new_db_item = json.loads(json.dumps(new_db_item), use_decimal=True)

    try:
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table("uav_wvi")
        table.put_item(Item=new_db_item)
        return "Success"

    except Exception as e:
        print(e)
        return json.dumps("[ERR] Execption caught while creating item in database.")


if __name__ == "__main__":
    #app.run(host='0.0.0.0')
    serve(app, host="0.0.0.0", port=5000)
