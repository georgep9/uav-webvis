import boto3
from boto3.dynamodb.conditions import Key
import simplejson as json
import time
import sys


cache_ttl = 100 # milliseconds
db_ttl_min = 20 # minutes
query_lim_max = 100 # max db items to query


def check_live_cache(cache, ts, route):
    if (ts is not None):
        data = cache.get(route+'/'+ts)
        if data is not None:
            print("[GET " + route + "] Cache hit! Returning data.")
            return data


def update_live_cache(cache, ts, route, data):
    if (ts is not None and
        type(json.loads(data)) is list):
      new_key = route+'/'+ts
      cache.set(new_key, data, px=cache_ttl, nx=True)


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


def get_live(ts, route):
    try:
        query_limit = 1
        from_ts = int(ts)
        if from_ts != 0: query_limit = query_lim_max
        if from_ts < 0: raise Exception
    except Exception as e:
        msg = "[ERR] Argument 'from_ts' must be an integer of unix time."
        print(msg)
        return json.dumps(msg)

    try:
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table("uav_wvi")
        
        start_t = round(time.time() * 1000)

        db_res = table.query(
            KeyConditionExpression=
                Key('data_type').eq("air_quality") &
                Key('timestamp').gt(from_ts),
            ScanIndexForward=False,
            Limit=query_limit)

        end_t = round(time.time() * 1000)
        query_dur = end_t - start_t

        db_items = reversed(db_res["Items"])
        json_res, length = process_json_res(db_items)

        print('[GET ' + route + '] DDB Query time: ' + str(query_dur) + ' ms. ' + \
            'Serving ' + str(length) + ' samples.')
        return json_res

    except Exception as e:
        msg = "[ERR] Execption caught while querying database."
        print(msg)
        print(e)
        return json.dumps(msg)


def get_sen(route, sensor, samples, from_ts, before_ts):
    if samples is None or sensor is None:
        msg = "[ERR] Must provide 'sensor', 'samples', 'from_ts', and 'before_ts' argument."
        print(msg)
        return json.dumps(msg)

    print(from_ts)
    print(before_ts)

    try:
        samples = int(samples)
        from_ts = int(from_ts)
        before_ts = int(before_ts)
        if (samples < 1 or samples > 500 or 
            from_ts < 0 or before_ts < 0): raise Exception
    except Exception as e:
        msg = "[ERR] Argument 'samples', 'from_ts', and 'before_ts' must be a positive integer."
        print(e)
        print(msg)
        return json.dumps(msg)

    if from_ts is None: from_ts = 0
    if before_ts is None: before_ts = sys.maxsize

    try:
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table("uav_wvi")

        start_t = round(time.time() * 1000)

        db_res = table.query(
            ProjectionExpression="#ts, #sen",
            ExpressionAttributeNames={"#ts": "timestamp", "#sen": sensor},
            KeyConditionExpression=Key('data_type').eq("air_quality") &
                Key('timestamp').lte(before_ts),
            ScanIndexForward=False,
            Limit=samples)

        end_t = round(time.time() * 1000)
        query_dur = end_t - start_t

        db_items = reversed(db_res["Items"])
        json_res, length = process_json_res(db_items)
        
        print('[GET ' + route + '] DDB Query time: '  + str(query_dur) + ' ms. ' + \
            'Serving ' + str(length) + " samples for " + sensor + ".")
        return json_res

    except Exception as e:
        msg = "[ERR] Execption caught while querying database."
        print(msg)
        print(e)
        return json.dumps(msg)


def post(data, route):
    try:
        ts = data["ts"]
        sensors = data["data"]
    except Exception as e:
        msg = "[ERR] Bad format."
        print(msg)
        return json.dumps(msg)
    
    start_t = round(time.time() * 1000)

    ttl = {'ttl': int(time.time()) + 60 * db_ttl_min}

    new_db_item = {"data_type": "air_quality", "timestamp": ts}
    new_db_item.update(sensors)
    new_db_item.update(ttl)
    new_db_item = json.loads(json.dumps(new_db_item), use_decimal=True)

    try:
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table("uav_wvi")
        table.put_item(Item=new_db_item)

        end_t = round(time.time() * 1000)
        query_dur = end_t - start_t
        print('[POST '+ route +']  Post time: '+ str(query_dur) +' ms.')
        return json.dumps("Success")
    except Exception as e:
        msg = "[ERR] Execption caught while creating item in database."
        print(msg)
        print(e)
        return json.dumps(msg)