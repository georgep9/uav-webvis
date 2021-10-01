
import requests
import time
import random
import json

api_endpoint = "http://127.0.0.1:5000/api/aq"

if __name__ == "__main__":

  while(True):

    timestamp = round(time.time() * 1000)
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
    #print("JSON to POST:")
    #print(json_post)
    print(timestamp)

    res = requests.post(api_endpoint, json = json_post)
    print("Response:", res)
    print()

    time.sleep(0.1)
