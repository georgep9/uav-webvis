
import requests
import time
import random
import json

aq_live_api = "http://127.0.0.1:5000/api/aq/live"
aq_sen_api = "http://127.0.0.1:5000/api/aq/sen"

def get_aq_live():
  for i in range(1):

    response = requests.get(aq_live_api)
    print(response.json())

    time.sleep(0.25)

def get_aq_sen(sensor, samples):

  args={"sensor": sensor, "samples": samples}

  response = requests.get(aq_sen_api, params=args)
  print(response.json())

if __name__ == "__main__":

  get_aq_live()
  get_aq_sen('light', 5)

