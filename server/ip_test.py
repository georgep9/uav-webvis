import requests
import json
from io import BytesIO
import base64
import time
from PIL import Image

ip_endpoint = ""

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

  targets = ["Aruco Marker", "Person", "Bag"]

  prev_ts = round(time.time() * 1000)

  while(True):

    timestamp = round(time.time() * 1000)
    diff = timestamp - prev_ts
    print("delay:", diff, " ms")
    prev_ts = timestamp

    image = images[idx]
    detected = [targets[idx]]
    idx = idx + 1
    if idx > 2: idx = 0

    json_post = json.dumps({"ts": timestamp, "image": image, "detected": detected})
    requests.post(ip_endpoint, json = json_post)
   
    time.sleep(1)


if __name__ == "__main__":
  post_ip()