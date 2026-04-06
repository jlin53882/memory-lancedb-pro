import urllib.request
import json

# Check the actual response from models endpoint
url = "http://127.0.0.1:4096/v1/models"
req = urllib.request.Request(url)
with urllib.request.urlopen(req, timeout=10) as resp:
    print("Status:", resp.status)
    print("Headers:", dict(resp.headers))
    body = resp.read()
    print("Body:", body[:2000])
