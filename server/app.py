from flask import Flask, jsonify, request
from flask_cors import CORS
from waitress import serve
import boto3
from boto3.dynamodb.conditions import Key
import simplejson as json
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
def serve_aq_live():
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
        return "something went wrong"

@app.route('/api/aq/sen', methods=['GET'])
def serve_aq_sen():

    ts = round(time.time() * 1000)

    if request.args.get('from') and request.args.get('to'):
        # TODO
        pass

    norm_val = round(random.uniform(0, 1), 2)

    sen_data = {'ts': ts, 'val': norm_val}

    return json.dumps(sen_data)

if __name__ == "__main__":
    #app.run(host='0.0.0.0')
    serve(app, host="0.0.0.0", port=5000)
