from flask import Flask, request
from flask_cors import CORS
from waitress import serve
import boto3
from boto3.dynamodb.conditions import Key
import simplejson as json
import logging
import time
import redis

app = Flask(__name__)
CORS(app)

logger = logging.getLogger('waitress')
logger.setLevel(logging.DEBUG)

db_ttl_min = 5 # time to live in minutes
query_lim_max = 100 # max db items to query

cache = redis.Redis(host="localhost", port=6379)
cache_ttl = 100 # time to live in milliseconds

aq_live_route = '/api/aq/live'
aq_sen_route = '/api/aq/sen'
aq_post_route = '/api/aq'
ip_live_route = '/api/ip/live'

@app.route('/')
def hw():
    return "<h1>Hello, world</h1>"

@app.before_request
def check_cache():
    method = request.method
    path = request.path
    ts = request.args.get('from_ts')

    if (method == "GET" and 
        path == aq_live_route and
        ts is not None):
        data = cache.get(aq_live_route+'/'+ts)
        if data is not None:
            print("[GET " + aq_live_route + "] Cache hit! Returning data.")
            return data

@app.after_request
def update_cache(res):
    method = request.method
    path = request.path
    ts = request.args.get('from_ts')
    data = res.get_data()
    
    if (method == "GET" and 
        path == aq_live_route and
        ts is not None and
        type(json.loads(data)) is list):

        new_key = aq_live_route+'/'+ts
        cache.set(new_key, data, px=cache_ttl, nx=True)

    return res

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


@app.route(aq_live_route, methods=['GET'])
def get_aq_live():
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table("uav_wvi")

    try:
        query_limit = 1
        from_ts = 0

        from_ts_arg = request.args.get('from_ts')
        if from_ts_arg is not None:
            from_ts = int(from_ts_arg)
            if from_ts != 0: query_limit = query_lim_max
        
        start_t = round(time.time() * 1000)
        db_res = table.query(
            KeyConditionExpression=
                Key('data_type').eq("air_quality") &
                Key('timestamp').gt(from_ts),
            ScanIndexForward=False,
            Limit=query_limit)
        db_items = reversed(db_res["Items"])
        
        json_res, length = process_json_res(db_items)
        end_t = round(time.time() * 1000)
        query_dur = end_t - start_t
        print('[GET ' + aq_live_route + '] DDB Query time: ' + str(query_dur) + ' ms. ' + \
            'Serving ' + str(length) + ' samples.')
        return json_res

    except ValueError as e:
        print(e)
        return json.dumps("[ERR] Argument 'from_ts' must be an integer of unix time.")

    except Exception as e:
        print(e)
        return json.dumps("[ERR] Execption caught while querying database.")


@app.route(aq_sen_route, methods=['GET'])
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
        start_t = round(time.time() * 1000)
        db_res = table.query(
            ProjectionExpression="#ts, #sen",
            ExpressionAttributeNames={"#ts": "timestamp", "#sen": sensor},
            KeyConditionExpression=Key('data_type').eq("air_quality"),
            ScanIndexForward=False,
            Limit=samples)
        db_items = reversed(db_res["Items"])
        json_res, length = process_json_res(db_items)

        end_t = round(time.time() * 1000)
        query_dur = end_t - start_t
        print('[GET ' + aq_live_route + '] DDB Query time: '  + str(query_dur) + ' ms. ' + \
            'Serving ' + str(length) + " samples for " + sensor + ".")
        return json_res

    except Exception as e:
        print(e)
        return json.dumps("[ERR] Execption caught while querying database.")


@app.route(aq_post_route, methods=["POST"])
def post_aq():

    post_json = json.loads(request.get_json())

    if "ts" not in post_json and "data" not in post_json:
        return json.dumps("[ERR] Bad format.")

    ts = post_json["ts"]
    sensors = post_json["data"]
    ttl = {'ttl': int(time.time()) + 60 * db_ttl_min}

    new_db_item = {"data_type": "air_quality", "timestamp": ts}
    new_db_item.update(sensors)
    new_db_item.update(ttl)
    new_db_item = json.loads(json.dumps(new_db_item), use_decimal=True)

    try:
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table("uav_wvi")
        table.put_item(Item=new_db_item)
        return json.dumps("Success")

    except Exception as e:
        print(e)
        return json.dumps("[ERR] Execption caught while creating item in database.")


@app.route(ip_live_route , methods=["GET", "POST"])
def handle_ip_live():

    if request.method == "GET":
        last_frame = cache.get("live_ip_frame")
        if last_frame is not None: 
            return last_frame
        else: return json.dumps("")

    elif request.method == "POST":

        post_json = json.loads(request.get_json())

        try:
            ts = post_json["ts"]
            image = post_json["image"]
            detected = post_json["detected"]
            if (type(ts) is not int and
                type(image) is not str and
                type(detected) is not list):
                raise Exception
        except:
            return json.dumps("[ERR] Bad format.")

        cache.set("live_ip_frame", json.dumps(post_json))

        if (len(detected) == 0): return json.dumps("Success")

        new_db_item = {
            "data_type": "image_processing",
            "timestamp": ts,
            "image": image,
            "detected": detected,
            "ttl": int(time.time()) + (60 * db_ttl_min)
        }

        try:
            dynamodb = boto3.resource('dynamodb')
            table = dynamodb.Table("uav_wvi")
            table.put_item(Item=new_db_item)
            print("item put")
            return json.dumps("Success")
        except Exception as e:
            print(e)
            return json.dumps("[ERR] Execption caught while creating item in database.")


if __name__ == "__main__":
    #app.run(host='0.0.0.0')
    serve(app, host="0.0.0.0", port=5000)
