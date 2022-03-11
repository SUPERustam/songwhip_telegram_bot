import json
import os
from pprint import pprint

import httpx
import uvicorn
from fastapi import FastAPI
from bs4 import BeautifulSoup
from pyngrok import ngrok

TOKEN = os.getenv("TOKEN")
TELEGRAM_URL = f"https://api.telegram.org/bot{TOKEN}/"

app = FastAPI()


def scrapper(url: str) -> dict:
    with httpx.Client(follow_redirects=True) as client:
        response = client.get("https://songwhip.com/" + url)
    if response.status_code != 200:
        return {"error": "Wrong link"}

    links = {}

    html = response.text
    soup = BeautifulSoup(html, 'html.parser')
    songs = soup.find(id="__NEXT_DATA__")
    songs = songs.get_text()
    data = json.loads(songs)

    with open("log.json", 'w', encoding="utf8") as f:
        f.write(json.dumps(data))

    try:
        # print(data['props']['initialReduxState']["artists"].keys())
        dct_links = next(iter(data['props']['initialReduxState']['tracks'].values()))[
            'value']
    except:
        return {"error": "Can't process this link"}

    artists = [artist["value"]['name']
               for artist in data['props']['initialReduxState']["artists"].values()]

    links["spotify"] = dct_links['links']['spotify'][0]['link']
    links["itunes"] = dct_links['links']['itunes'][0]['link']
    # links["yandex"] = dct_links['links']['yandex'][0]['link']
    links["image"] = dct_links['image']
    links['track'] = dct_links['name']
    links['artists'] = ", ".join(artists)
    links['songwhip'] = str(response.url)
    return links


@app.get("/song/{url:path}")
async def root(url) -> dict | str:
    return scrapper(url)


@app.post(f"/{TOKEN}")
async def webhook(update_data: dict):
    links = scrapper(update_data['message']['text'])
    if links.get("error", None) != None:
        query = httpx.get(TELEGRAM_URL + "sendMessage", params={
            "chat_id": update_data["message"]["chat"]["id"], "text": links["error"]})
        return
    caption = f"<b>Spotify:</b> <a>{links['spotify']}</a> \
            <b>Apple Music:</b> \
<a>{links['itunes'].replace('{country}', 'ru')}</a>"

    params = {"chat_id": update_data["message"]["chat"]["id"],
              "photo": links["image"],
              "caption": caption,
              "parse_mode": "HTML"
              }
    with httpx.Client() as client:
        query = client.get(TELEGRAM_URL + "sendPhoto", params=params)


if __name__ == "__main__":
    port = 8443
    ngrok_tunnel = ngrok.connect(port, bind_tls=True)
    print('URL:', ngrok_tunnel.public_url + "/docs")
    # print(ngrok_tunnel.public_url +
    #       "/song/https://open.spotify.com/track/0lwkTJnLBVWvEnxtku7Msy?si=bbef3477f7f04255")
    with httpx.Client() as client:
        response = client.get(TELEGRAM_URL + "setWebhook",
                              params={"url": f"{ngrok_tunnel.public_url}/{TOKEN}"})
    uvicorn.run(app, port=port)

'''
TODO:
1. make dev enviroment
2. github host source code
3. make 100% test coverage
'''
