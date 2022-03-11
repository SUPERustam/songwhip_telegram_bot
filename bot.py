import requests
from pprint import pprint
import os
import json

TOKEN = os.getenv("TOKEN")
tel = f"https://api.telegram.org/bot{TOKEN}/"
method = "getUpdates"
print(TOKEN)

params = {}
response = requests.get(tel + "deleteWebhook")
response = requests.get(tel + method, params=params)
with open('update.json', 'w', encoding='utf8') as f:
    f.write(json.dumps(response.json()))
pprint(response.json())


# print(response.status_code, response.content, response.json, sep="\n")
