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

@app.route('/')
def hw():
    return "<h1>Hello, world</h1>"

@app.route('/api/aq/live', methods=['GET'])
def get_aq_live():
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table("uav_wvi")

    try:
        response = table.query(
            KeyConditionExpression=Key('data_type').eq("air_quality"),
            ScanIndexForward=True,
            Limit=1
        )
        item = response["Items"][0]

        ts = item["timestamp"]
        sensors = {}
        for sensor in item.keys():
            if sensor != "timestamp" and sensor != "data_type":
                sensors[sensor] = {'val': item[sensor]}
                
        aq_live = {'ts': ts, 'sensors': sensors}
        return json.dumps(aq_live)

    except Exception as e:
        print(e)
        return str("[ERR] Execption caught while querying database:\n", e)

@app.route('/api/aq/sen', methods=['GET'])
def get_aq_sen():

    ts = round(time.time() * 1000)

    if request.args.get('from') and request.args.get('to'):
        # TODO
        pass

    norm_val = round(random.uniform(0, 1), 2)

    sen_data = {'ts': ts, 'val': norm_val}

    return json.dumps(sen_data)



@app.route('/api/aq', methods=["POST"])
def post_aq():

    post_json = json.loads(request.get_json())

    if "ts" not in post_json and "data" not in post_json:
        return "[ERR] Bad format."

    ts = post_json["ts"]
    sensors = post_json["data"]

    new_db_item = {"data_type": "air_quality", "timestamp": ts}
    new_db_item.update(sensors)
    new_db_item = json.loads(json.dumps(new_db_item), use_decimal=True)

    try:
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table("uav_wvi")
        table.put_item(Item=new_db_item)
        return "Success"
    except Exception as e:
        print(e)
        return str("[ERR] Execption caught while creating item in database:\n", e)


if __name__ == "__main__":
    #app.run(host='0.0.0.0')
    serve(app, host="0.0.0.0", port=5000)
