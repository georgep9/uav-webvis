from test_functions import get_ip_live
import time

ts = round(time.time() * 1000)
get_ip_live()
print("Request time: " + str(round(time.time() * 1000) - ts) + "ms")