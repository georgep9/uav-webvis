
import requests
import time
import random
import json

aq_live_api = "http://127.0.0.1:5000/api/aq/live"
aq_sen_api = "http://127.0.0.1:5000/api/aq/sen"

def get_aq_live():

  last_ts = None
  from_to_arg = ""

  while(True):

    req_url = aq_live_api
    if last_ts is not None: 
      req_url = req_url + str(from_to_arg)

    response = requests.get(req_url)
    response = response.json()
    #print(response)
    last_ts = response[-1]["ts"]
    from_to_arg = "?from_ts=" + str(last_ts)

    print(len(response))
    print(last_ts)

    time.sleep(0.1)

def get_aq_sen(sensor, samples):

  args={"sensor": sensor, "samples": samples}

  response = requests.get(aq_sen_api, params=args)
  print(response.json())

if __name__ == "__main__":

  get_aq_live()
  #get_aq_sen('light', 5)

