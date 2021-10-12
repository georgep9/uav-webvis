from flask import Flask, request
from flask_cors import CORS
from waitress import serve
import boto3
from boto3.dynamodb.conditions import Key
import simplejson as json
import logging
import time
import redis

import aq

app = Flask(__name__)
CORS(app)

logger = logging.getLogger('waitress')
logger.setLevel(logging.DEBUG)

cache = redis.Redis(host="localhost", port=6379)
cache_ttl = 100 # time to live in milliseconds

aq_live_route = '/api/aq/live'
aq_sen_route = '/api/aq/sen'
aq_post_route = '/api/aq'

ip_live_route = '/api/ip/live'
ip_hist_route = '/api/ip/hist'

@app.route('/')
def hw():
    return "<h1>Hello, world</h1>"


@app.route(aq_live_route, methods=['GET'])
def get_aq_live():
    ts = request.args.get('from_ts')
    cache_res = aq.check_cache(cache, ts, aq_live_route)
    if cache_res: return cache_res
    else: return aq.get_live(ts, aq_live_route)


@app.route(aq_sen_route, methods=['GET'])
def get_aq_sen():
    sensor = request.args.get('sensor')
    samples = request.args.get('samples')
    return aq.get_sen(aq_sen_route, sensor, samples)


@app.route(aq_post_route, methods=["POST"])
def post_aq():
    data = json.loads(request.get_json())
    return aq.post(data)


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

        try:

            s3 = boto3.resource('s3')
            new_s3_object_fname = str(ts) + '.txt'
            new_s3_object_body = bytes(image, 'utf-8')
            new_s3_object = s3.Object('uav-wvi-ip-detected', new_s3_object_fname)
            new_s3_object.put(Body=new_s3_object_body)

            dynamodb = boto3.resource('dynamodb')
            table = dynamodb.Table("uav_wvi")
            new_db_item = {
                "data_type": "image_processing",
                "timestamp": ts,
                "s3_image_fname": new_s3_object_fname,
                "detected": detected,
                "ttl": int(time.time()) + (60 * db_ttl_min)
            }
            table.put_item(Item=new_db_item)

            print("item put")
            return json.dumps("Success")
        except Exception as e:
            print(e)
            return json.dumps("[ERR] Execption caught while creating item in database.")

@app.route(ip_hist_route, methods=["GET"])
def get_ip_history():

    try:
        before_ts = int(request.args.get("beforeTs"))
        n_frames = int(request.args.get("nFrames"))
        if (before_ts < 0 or n_frames < 0): raise Exception
    except Exception as e:
        return json.dumps("[ERR] Must provide 'beforeTs' and 'nFrames' " +
        "arguments as positive integers.")

    cached_response = cache.get(request.full_path)
    if (cached_response): 
        print('[GET '+ ip_hist_route +'] Cache hit! Returning response')
        return cached_response

    try:
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table("uav_wvi")
        start_t = round(time.time() * 1000)
        db_res = table.query(
            KeyConditionExpression=
                Key('data_type').eq("image_processing") &
                Key('timestamp').lt(before_ts),
            ScanIndexForward=False,
            Limit=n_frames)
        end_t = round(time.time() * 1000)

        db_items = db_res["Items"]
        
        query_dur = end_t - start_t
        print('[GET '+ ip_hist_route +'] DDB Query time: '+ str(query_dur) +
            ' ms for ' + str(len(db_items)) + " items.")

    except Exception as e:
        print(e)
        return json.dumps("[ERR] Execption caught while querying database.")

    try:
        s3 = boto3.resource('s3')

        start_t = round(time.time() * 1000)
        frames = []
        for item in db_items:
            timestamp = item["timestamp"]
            detected = item["detected"]
            s3_image_fname = item["s3_image_fname"]
            s3_image_object = s3.Object("uav-wvi-ip-detected", s3_image_fname)
            image = s3_image_object.get()['Body'].read().decode('utf-8')

            frames.append({
                "timestamp": timestamp, 
                "detected": detected, 
                "image": image
            })
        end_t = round(time.time() * 1000)
        s3_get_dur = end_t - start_t
        print('[GET '+ ip_hist_route +'] S3 Object reads: '+ str(s3_get_dur) +
            ' ms for ' + str(len(frames)) + " images.")

        json_res = json.dumps(frames)
        cache.set(request.full_path, json_res, px=cache_ttl, nx=True)

        return json_res

    except Exception as e:
        print(e)
        return json.dumps("[ERR] Execption caught while processing IP history.")


if __name__ == "__main__":
    #app.run(host='0.0.0.0')
    serve(app, host="0.0.0.0", port=5000)
