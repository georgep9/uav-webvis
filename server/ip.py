import boto3
from boto3.dynamodb.conditions import Key
import simplejson as json
import time
import queue


save_queue = queue.Queue()

db_ttl_min = 10 # minutes
cache_ttl = 100 # milliseconds

live_ts_n = 30 # max live timestamps to keep
live_data_ttl = 1 # ttl in seconds for each live frame


def get_live_frame(after_ts, cache, route):
    if after_ts is None: return cache.get(route + '/latest')

    live_timestamps_c = cache.get(route)
    if live_timestamps_c is None: return None 
    live_timestamps = live_timestamps_c.decode('utf-8').split(',')

    ts_to_get = None
    for idx, live_ts in enumerate(live_timestamps):
        if after_ts == live_ts:
            next_idx = idx + 1
            if next_idx != len(live_timestamps):
                ts_to_get = live_timestamps[next_idx]
                break
    if ts_to_get == None: return cache.get(route + '/latest')

    live_key = route + '/' + str(ts_to_get)
    live_frame = cache.get(live_key)
    if live_frame is not None: return live_frame
    else: return cache.get(route + '/latest')


def update_live_frames(data, cache, route):

    live_timestamps_c = cache.get(route)
    if live_timestamps_c is None: live_timestamps = []
    else: live_timestamps = live_timestamps_c.decode('utf-8').split(',')

    while len(live_timestamps) >= live_ts_n:
        live_ts_to_del = live_timestamps.pop(0)
        live_key_to_del = route + '/' + str(live_ts_to_del)
        cache.delete(live_key_to_del)
    
    new_ts = data["ts"]
    new_key = route + '/' + str(new_ts)
    new_value = json.dumps(data)
    cache.set(new_key, new_value, ex=live_data_ttl)
    cache.set(route + '/latest', new_value)

    live_timestamps.append(new_ts)
    live_timestamps_c = ','.join(str(ts) for ts in live_timestamps)
    cache.set(route, live_timestamps_c)


def get_live(after_ts, cache, route):
    live_frame = get_live_frame(after_ts, cache, route)
    if live_frame is not None: 
        print('[GET '+ route +'] Live frame cache hit! Returning data.')
        return live_frame
    else: 
        print('[GET '+ route +'] No live frame in cache. Returning empty string.')
        return json.dumps("")


def save_detected(ts, image, detected):
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

        print('[IP] Item put in S3 and DDB.')
    except Exception as e:
        print('[IP ERR] Execption caught while creating item in database.')
        print(e)


def save_detected_worker():
    while True:
        ip_data = save_queue.get()
        ts = ip_data[0]
        image = ip_data[1]
        detected = ip_data[2]
        save_detected(ts, image, detected)
        save_queue.task_done()


def post_live(data, cache, route):
    try:
        ts = data["ts"]
        image = data["image"]
        detected = data["detected"]
        if (type(ts) is not int and
            type(image) is not str and
            type(detected) is not list):
            raise Exception
    except:
        msg = "[ERR] Bad format."
        print(msg)
        return json.dumps(msg)

    start_t = round(time.time() * 1000)

    update_live_frames(data, cache, route)
    if (len(detected) != 0): 
        ip_data = [ts, image, detected]
        save_queue.put(ip_data)

    end_t = round(time.time() * 1000)
    query_dur = end_t - start_t
    print('[POST '+ route +']  Post time: '+ str(query_dur) +
            ' ms with ' + str(len(detected)) + " detected.")
    return json.dumps("Success")


def check_hist_cache(cache, full_path, route):
    data = cache.get(full_path)
    if (data): 
        print('[GET '+ route +'] Cache hit! Returning response')
        return data


def update_hist_cache(cache, full_path, data):
    cache.set(full_path, data, px=cache_ttl, nx=True)


def get_hist_db_items(before_ts, n_frames, route):
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
        query_dur = end_t - start_t

        db_items = db_res["Items"]
        
        print('[GET '+ route +'] DDB Query time: '+ str(query_dur) +
            ' ms for ' + str(len(db_items)) + " items.")
        return db_items

    except Exception as e:
        msg = "[ERR] Execption caught while querying database."
        print(msg)
        print(e)
        return json.dumps(msg)


def get_hist_frames(db_items, route):
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

        print('[GET '+ route +'] S3 Object reads: '+ str(s3_get_dur) +
            ' ms for ' + str(len(frames)) + " images.")
        return json.dumps(frames)

    except Exception as e:
        msg = "[ERR] Execption caught while processing IP history."
        print(msg)
        print(e)
        return json.dumps(msg)


def get_history(before_ts, n_frames, route):
    try:
        before_ts = int(before_ts)
        n_frames = int(n_frames)
        if (before_ts < 0 or n_frames < 0): raise Exception
    except Exception:
        msg = "[ERR] Must provide 'beforeTs' and 'nFrames' " + \
        "arguments as positive integers."
        print(msg)
        return json.dumps(msg)

    res = get_hist_db_items(before_ts, n_frames, route)
    if (type(res) is not list): return res
    else: db_items = res

    return get_hist_frames(db_items, route)

