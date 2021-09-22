from flask import Flask, jsonify, request

import random
import time

app = Flask(__name__)

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
        norm_val = round(random.uniform(0, 1), 2)
        scal_val = int(norm_val * 100)
        aq_sens[sen] = {'norm': norm_val, 'scal': scal_val}

    live_aq = {'ts': ts, 'data': aq_sens}

    return jsonify(live_aq)

@app.route('/api/aq/sen', methods=['GET'])
def serve_aq_sen():

    ts = round(time.time() * 1000)

    if request.args.get('from') and request.args.get('to'):
        # TODO
        pass

    norm_val = round(random.uniform(0, 1), 2)

    sen_data = {'ts': ts, 'data': norm_val}

    return jsonify(sen_data)

