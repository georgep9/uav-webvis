import boto3
from boto3.dynamodb.conditions import Key
import simplejson as json
import time


db_ttl_min = 5 # minutes
cache_ttl = 100 # milliseconds


def check_hist_cache(cache, full_path, route):
    data = cache.get(full_path)
    if (data): 
        print('[GET '+ route +'] Cache hit! Returning response')
        return data


def update_hist_cache(cache, full_path, data):
    cache.set(full_path, data, px=cache_ttl, nx=True)


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

        print("item put")
        return json.dumps("Success")
    except Exception as e:
        print(e)
        return json.dumps("[ERR] Execption caught while creating item in database.")


def get_live(cache, route):
    last_frame = cache.get(route)
    if last_frame is not None: return last_frame
    else: return json.dumps("")


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
        return json.dumps("[ERR] Bad format.")

    cache.set(route, json.dumps(data))

    if (len(detected) == 0): return json.dumps("Success")
    else: return save_detected(ts, image, detected)


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
        print(e)
        return json.dumps("[ERR] Execption caught while querying database.")


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
        print(e)
        return json.dumps("[ERR] Execption caught while processing IP history.")


def get_history(before_ts, n_frames, route):
    try:
        before_ts = int(before_ts)
        n_frames = int(n_frames)
        if (before_ts < 0 or n_frames < 0): raise Exception
    except Exception as e:
        return json.dumps("[ERR] Must provide 'beforeTs' and 'nFrames' " +
        "arguments as positive integers.")

    res = get_hist_db_items(before_ts, n_frames, route)
    if (type(res) is not list): return res
    else: db_items = res

    return get_hist_frames(db_items, route)
