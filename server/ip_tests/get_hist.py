from test_functions import get_ip_hist, post_ip
import time

before_ts = 1700000000000 # future unix time

print("Posting 3 images...")
post_ip(3) # post 3 images
print("Done.")

print("First get request for 3 images...")
ts = round(time.time() * 1000)
# first history request for the 3 images,
# should force server to query ddb then read objects from s3
get_ip_hist(before_ts, 3) 
print("Request time: " + str(round(time.time() * 1000) - ts) + "ms")

print("Second get request for 3 images...")
ts = round(time.time() * 1000)
# second history request for the 3 images,
# server should return redis cache of first request
get_ip_hist(before_ts, 3)
print("Request time: " + str(round(time.time() * 1000) - ts) + "ms")

