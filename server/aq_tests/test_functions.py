import requests
import json
import time
import random

api_url = "http://127.0.0.1:5000"
aq_post_route = "/api/aq"
aq_live_route = "/api/aq/live"
aq_hist_route = "/api/aq/sen"


def get_aq_live(last_ts=None, from_to_arg=""):
  req_url = api_url + aq_live_route
  if last_ts is not None: 
    req_url = req_url + str(from_to_arg)

  response = requests.get(req_url)
  return response.json()


def get_aq_sen(sensor, samples):
  args={"sensor": sensor, "samples": samples}
  response = requests.get(api_url + aq_hist_route, params=args)
  return(response.json())


def post_aq(n_reqs):

  prev_ts = round(time.time() * 1000)

  for n in range(n_reqs):

    timestamp = round(time.time() * 1000)
    diff = timestamp - prev_ts
    print("delay:", diff, " ms")
    prev_ts = timestamp

    data = {
      "temp": random.choice([23.5, 24, 23]),
      "red": random.choice([120, 121, 118]),
      "press": random.choice([102, 100, 99]),
      "nh3": random.choice([300, 310, 320]),
      "ox":  random.choice([650, 610, 670]),
      "hum":  random.choice([60.1,62.3, 59.1]),
      "light": random.choice([500,750, 800, 420, 300]),
      "noise": random.choice([65.4, 90, 50, 55, 70.5, 40.9, 52.7, 81.6])
    }

    json_post = json.dumps({"ts": timestamp, "data": data})

    requests.post(api_url + aq_post_route, json = json_post)

    time.sleep(0.1)
