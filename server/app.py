from flask import Flask, request
from flask_cors import CORS
from waitress import serve
import simplejson as json
import logging
import redis
import threading

import aq
import ip

app = Flask(__name__)
CORS(app)

logger = logging.getLogger('waitress')
logger.setLevel(logging.DEBUG)

cache = redis.Redis(host="wvi-redis", port=6379, charset="utf-8")

threading.Thread(target=ip.save_detected_worker, daemon=True).start()

aq_live_route = '/api/aq/live'
aq_sen_route = '/api/aq/sen'
aq_post_route = '/api/aq'

ip_live_route = '/api/ip/live'
ip_hist_route = '/api/ip/hist'


@app.before_request
def print_address(): print(' ' + request.remote_addr, end=' ')

@app.route('/')
def hw():
    print("Hello, world")
    return "<h1>Hello, world</h1>"

@app.route(aq_live_route, methods=['GET'])
def get_aq_live():
    ts = request.args.get('from_ts')
    cache_data = aq.check_live_cache(cache, ts, aq_live_route)
    if cache_data: return cache_data
    else: 
        data = aq.get_live(ts, aq_live_route)
        aq.update_live_cache(cache,ts, aq_live_route, data)
        return data

@app.route(aq_sen_route, methods=['GET'])
def get_aq_sen():
    sensor = request.args.get('sensor')
    samples = request.args.get('samples')
    from_ts = request.args.get('from_ts')
    before_ts = request.args.get('before_ts')
    return aq.get_sen(aq_sen_route, sensor, samples, from_ts, before_ts)

@app.route(aq_post_route, methods=["POST"])
def post_aq():
    data = json.loads(request.get_json())
    return aq.post(data, aq_post_route)

@app.route(ip_live_route , methods=["GET", "POST"])
def ip_live():
    if request.method == "GET": 
        after_ts = request.args.get("afterTs")
        return ip.get_live(after_ts, cache, ip_live_route)
    elif request.method == "POST": 
        data = json.loads(request.get_json())
        return ip.post_live(data, cache, ip_live_route)

@app.route(ip_hist_route, methods=["GET"])
def get_ip_history():
    before_ts = request.args.get("beforeTs")
    n_frames = request.args.get("nFrames")
    full_path = request.full_path

    cache_data = ip.check_hist_cache(cache, full_path, ip_hist_route)
    if cache_data: return cache_data
    else:
        data = ip.get_history(before_ts, n_frames, ip_hist_route)
        ip.update_hist_cache(cache, full_path, data)
        return data

if __name__ == "__main__":
    #app.run(host='0.0.0.0')
    serve(app, host="0.0.0.0", port=5000)
