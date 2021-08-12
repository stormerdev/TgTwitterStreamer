# Telegram - Twitter - Bot
# Github.com/New-dev0/TgTwitterStreamer
# GNU General Public License v3.0


import logging
import re

import tweepy
from telethon import TelegramClient, events
from telethon.tl.custom import Button
from tweepy.asynchronous import AsyncStream

from Configs import Var

logging.basicConfig(level=logging.INFO)


Client = TelegramClient("HausPROMO Streamer", Var.API_ID, Var.API_HASH).start(
    bot_token=Var.BOT_TOKEN
)

auth = tweepy.OAuthHandler(Var.CONSUMER_KEY, Var.CONSUMER_SECRET)
auth.set_access_token(Var.ACCESS_TOKEN, Var.ACCESS_TOKEN_SECRET)
api = tweepy.API(auth)

print("<<--- Montando o Robô! --->>")
TRACK_IDS = []
for userid in Var.TRACK_USERS.split(" "):
    try:
        user = api.get_user(screen_name=userid)._json
        TRACK_IDS.append(str(user["id"]))
        print(f"<<--- Adicionado {user['screen_name']} no monitoramento ! --->>")
    except Exception as e:
        print(e)


class TgStreamer(AsyncStream):
    async def on_connect(self):
        print("<<<---||| Stream Conectada |||--->>>")

    def get_urls(self, media):
        if not media:
            return []
        return [m["media_url_https"] for m in media if m["type"] == "photo"]

    async def on_status(self, status):
        tweet = status._json
        if tweet["text"].startswith("RT "):
            return
        user = tweet["user"]
        if not str(user["id"]) in TRACK_IDS:
            return
        pic, content = [], ""
        try:
            entities = tweet.get("entities", {}).get("media")
            extended_entities = tweet.get("extended_entities", {}).get("media")
            extended_tweet = (
                tweet.get("extended_tweet", {}).get("entities", {}).get("media")
            )
            all_urls = set()
            for media in (entities, extended_entities, extended_tweet):
                urls = self.get_urls(media)
                all_urls.update(set(urls))
            for pik in all_urls:
                pic.append(pik)
            content = tweet.get("extended_tweet").get("full_text")
        except BaseException:
            pass
        #text = f"[{user['name']}](https://twitter.com/{user['screen_name']})"
        text = f""
        mn = " ✨ Nova Promoção ✨"
        if content and (len(content) < 1000):
            text += mn + "\n\n" + "`{content}`"
            text = re.sub(r'(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:\'".,<>?«»“”‘’]))', '', text)
        else:
            text += mn + "\n\n" + f"`{tweet['text']}`"
            text = re.sub(r'(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:\'".,<>?«»“”‘’]))', '', text)
        url = f"https://twitter.com/{user['screen_name']}/status/{tweet['id']}"
        multichat = Var.TO_CHAT.split()
        for chat in multichat:
            try:
                chat = int(chat)
            except BaseException:
                pass
            try:
                if pic:
                    if len(pic) == 1:
                        for pic in pic:
                            await Client.send_message(
                                chat,
                                text,
                                link_preview=False,
                                file=pic,
                                buttons=Button.url(text="Ver 🔗", url=url),
                            )
                    else:
                        await Client.send_file(
                                chat,
                                file=pic,
                        )
                        await Client.send_message(
                                chat,
                                text,
                                link_preview=False,
                                buttons=Button.url(text="Ver 🔗", url=url),
                        )
                else:
                    await Client.send_message(
                        chat,
                        text,
                        link_preview=False,
                        buttons=Button.url(text="Ver 🔗", url=url),
                    )
            except Exception as er:
                print(er)

    async def on_connection_error(self):
        print("<<---|| Connection Error ||--->>")

    async def on_exception(self, exception):
        print(exception)


@Client.on(events.NewMessage(pattern=r"/start"))
async def startmsg(event):
    await event.reply(
        file="ult.webp",
        buttons=[
            [Button.inline("Olá, estou online =)", data="ok")],
            [
                Button.url(
                    "Criação",
                    url="",
                ),
                Button.url("Grupo", url=""),
            ],
        ],
    )


@Client.on(events.callbackquery.CallbackQuery(data=re.compile("ok")))
async def _(e):
    return await e.answer("Estou online!!!")


if __name__ == "__main__":
    Stream = TgStreamer(
        Var.CONSUMER_KEY, Var.CONSUMER_SECRET, Var.ACCESS_TOKEN, Var.ACCESS_TOKEN_SECRET
    )
    Stream.filter(follow=TRACK_IDS)

    with Client:
        Client.run_until_disconnected()  # Running Client
