from flask import Flask, jsonify, request
from flask_cors import CORS
from waitress import serve
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

    ts = round(time.time() * 1000)

    aq_sens = {
        "temp": {},
        "press": {},
        "hum": {},
        "light": {},
        "noise": {},
        "ox": {},
        "red": {},
        "nh3": {}
    }
    for sen in aq_sens:
        val = round(random.uniform(0, 1), 2)
        aq_sens[sen] = {'val': val}

    live_aq = {'ts': ts, 'sensors': aq_sens}

    return jsonify(live_aq)

@app.route('/api/aq/sen', methods=['GET'])
def serve_aq_sen():

    ts = round(time.time() * 1000)

    if request.args.get('from') and request.args.get('to'):
        # TODO
        pass

    norm_val = round(random.uniform(0, 1), 2)

    sen_data = {'ts': ts, 'val': norm_val}

    return jsonify(sen_data)

if __name__ == "__main__":
    #app.run(host='0.0.0.0')
    serve(app, host="0.0.0.0", port=5000)
