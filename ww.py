import re
import requests
from requests.auth import HTTPDigestAuth
import time

while True:
    t = time.time()
    print(int(t))
    time.sleep(1)