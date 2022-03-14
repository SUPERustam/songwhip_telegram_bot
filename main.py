import json
import os

import httpx
from fastapi import FastAPI, Response, status
from bs4 import BeautifulSoup

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

    try:
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


def validate_url(text: str) -> str:
    if text == "/start":
        return "start"
    return ''


def sendMessage(text: str, id: int) -> None:
    with httpx.Client() as client:
        client.get(TELEGRAM_URL + "sendMessage", params={
            "chat_id": id, "text": text})


@app.get("/song/{url:path}")
async def song_url(url) -> dict:
    return scrapper(url)


@app.post(f"/telegram_bot", status_code=status.HTTP_200_OK)
async def webhook(update_data: dict, response: Response):
    if update_data.get('message', None) == None:
        response.status_code = status.HTTP_202_ACCEPTED
        return
    if update_data['message'].get('text', None) == None:
        response.status_code = status.HTTP_202_ACCEPTED
        return

    verdict = validate_url(update_data['message']['text'])
    if not verdict:
        links = scrapper(update_data['message']['text'])
    elif verdict == 'start':
        welcome_string = '''
Just send me link from your music app!
For example: https://open.spotify.com/track/25nU5mxSzlzyOXzeqx4c5j
        '''
        sendMessage(welcome_string, update_data["message"]["chat"]["id"])
        return
    else:
        sendMessage(verdict, update_data["message"]["chat"]["id"])

    links = scrapper(update_data['message']['text'])
    if links.get("error", None) != None:
        sendMessage(links['error'], update_data["message"]["chat"]["id"])
        return

    caption = f"""
<b>{links['track'].strip()} — {links['artists'].strip()}</b>

<b>Spotify:</b> {links['spotify'].strip()}
<b>Apple Music:</b> {links['itunes'].replace('{country}', 'ru').strip()}
<b>Others:</b> {links['songwhip'].strip()}
"""
    params = {"chat_id": update_data["message"]["chat"]["id"],
              "photo": links["image"],
              "caption": caption,
              "parse_mode": "HTML"
              }
    with httpx.Client() as client:
        query = client.get(TELEGRAM_URL + "sendPhoto", params=params)
