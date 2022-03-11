import os
from pprint import pprint
import httpx


TOKEN = os.getenv("TOKEN")
SERVER_URL = os.getenv("SERVER_URL")

TELEGRAM_URL = f"https://api.telegram.org/bot{TOKEN}/"
response = httpx.get(TELEGRAM_URL + "setWebhook",
                     params={"url": SERVER_URL})
response = httpx.get(TELEGRAM_URL + "getWebhookInfo")

pprint(response.url)
pprint(response.text)
