import boto3
from boto3.dynamodb.conditions import Key
import simplejson as json
import time


cache_ttl = 100 # milliseconds
db_ttl_min = 5 # minutes
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
      return json.dumps("[ERR] Argument 'from_ts' must be an integer of unix time.")

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
        print(e)
        return json.dumps("[ERR] Execption caught while querying database.")


def get_sen(route, sensor, samples):
    if samples is None or sensor is None:
        return json.dumps("[ERR] Must provide 'sensor' and 'samples' argument.")

    try:
        samples = int(samples)
        if samples < 1 or samples > 500: raise Exception
    except:
        return json.dumps("[ERR] Argument 'samples' must be an integer between 1 and 500.")

    try:
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table("uav_wvi")

        start_t = round(time.time() * 1000)

        db_res = table.query(
            ProjectionExpression="#ts, #sen",
            ExpressionAttributeNames={"#ts": "timestamp", "#sen": sensor},
            KeyConditionExpression=Key('data_type').eq("air_quality"),
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
        print(e)
        return json.dumps("[ERR] Execption caught while querying database.")


def post(data):
    try:
        ts = data["ts"]
        sensors = data["data"]
    except Exception as e:
        print(e)
        return json.dumps("[ERR] Bad format.")
    
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