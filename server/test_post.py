
import requests
import time
import random
import json
from PIL import Image
from io import BytesIO
import base64

aq_endpoint = "http://127.0.0.1:5000/api/aq"
ip_endpoint = "http://127.0.0.1:5000/api/ip/live"


def post_aq():

  prev_ts = round(time.time() * 1000)

  while(True):

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
    #print("JSON to POST:")
    #print(json_post)
    # print(timestamp)

    res = requests.post(aq_endpoint, json = json_post)
    # print("Response:", res)
    # print()

    time.sleep(0.05)

def post_ip():

  

  idx = 0

  image_links = ["https://www.brisbaneboatsforsale.com.au/wp-content/blogs.dir/176/files/2018/01/bbforsale_barcrusher.jpg", 
      "https://www.worldsbestbars.com/wp-content/uploads/2018/04/bar_640_480_byblosbar2_54aeaa00090de.jpg",
      "https://www.cunard.com/content/dam/cunard/marketing-assets/destinations/brisbane-370060808-750x568.jpg.image.640.480.low.jpg"]

  images = []
  for link in image_links:
    img= Image.open(requests.get(link, stream=True).raw)
    im_file = BytesIO()
    img.save(im_file, format="JPEG")
    im_bytes = im_file.getvalue()
    image = base64.b64encode(im_bytes).decode("utf-8")
    images.append(image)

  prev_ts = round(time.time() * 1000)

  while(True):

    timestamp = round(time.time() * 1000)
    diff = timestamp - prev_ts
    print("delay:", diff, " ms")
    prev_ts = timestamp

    image = images[idx]
    idx = idx + 1
    if idx > 2: idx = 0

    detected = []

    json_post = json.dumps({"ts": timestamp, "image": image, "detected": detected})
    res = requests.post(ip_endpoint, json = json_post)
   
    time.sleep(0.5)

  
if __name__ == "__main__":

  post_aq()
  #post_ip()

