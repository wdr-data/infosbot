import json
import logging
from os.path import basename, isfile, join
from urllib.request import urlopen, Request
from urllib.parse import urlencode
import sqlite3 as lite
import datetime
import re
import os

from flask import Flask, request
from bs4 import BeautifulSoup
from lxml import html
import requests

# Enable logging
logger = logging.getLogger(__name__)
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.DEBUG)

logger.info('FB Infos Bot Logging')

SEARCH, SELECT = range(2)

PAGE_TOKEN = os.environ['INFOSBOT_PAGE_TOKEN']
HUB_VERIFY_TOKEN = os.environ['INFOSBOT_HUB_VERIFY_TOKEN']
infos = list()

app = Flask(__name__)


@app.route('/testbot', methods=["GET"])
def confirm():
    if request.args['hub.verify_token'] == HUB_VERIFY_TOKEN:
        return request.args['hub.challenge']
    return 'Hello World!'


@app.route('/testbot', methods=["POST"])
def receive_message():
    data = request.json
    handle_messages(data)
    return "ok"


def handle_messages(data):
    """handle all incoming messages"""
    messaging_events = data['entry'][0]['messaging']
    logger.debug(messaging_events)
    for event in messaging_events:
        sender_id = event['sender']['id']

        # check if we actually have some input
        if "message" in event and event['message'].get("text", "") != "":
            logger.debug('received message')
            text = event['message']['text']
            if text == '/info':
                reply = "Heute haben wir folgende Themen für dich:\n"
                send_text(sender_id, reply)
                data = get_data()
                send_list_template(data, sender_id)
            else:
                reply = "echo: " + text
                send_text(sender_id, reply)
        elif "postback" in event and event['postback'].get("payload", "") == "start":
            reply = "Herzlich willkommen zum 1LIVE InfoMessenger. \n\n" \
                    "Hier bekommst Du alle Infos geliefert, die Du wissen musst, um mitreden zu " \
                    "können, selbst die, von denen Du nicht weißt, dass Du sie wissen wolltest" \
                    " :) \n\nWas Du dafür tun musst: Fast nichts. Tippe \"/info\" um dein " \
                    "Update zu bekommen."
            send_text(sender_id, reply)
        elif "postback" in event and event['postback'].get("payload", "").split("#")[0] == "info":
            for info in infos:
                #reply = event['postback'].get("payload","").split("#")[1]
                #reply += info[0]
                if event['postback'].get("payload", "").split("#")[1] == str(info[0]):
                    reply = info[2]
                    send_text(sender_id, reply)
        #     audio_url = event['postback'].get("payload","").split("#")[1]
        #     audio_file = get_audio(audio_url)
        #     send_audio(sender_id, audio_file)
            #reply = "Zukünftig wird dir hier ein Audio geschickt..."
            #send_text(sender_id, reply)


def get_data():
    db_path = 'infosbot_backend/db.sqlite3'
    database = lite.connect('db.sqlite3')

    with database:

        cur = database.cursor()
        cur.execute("SELECT * FROM backend_info")

        while True:
            row = cur.fetchone()

            if row is None:
                break
            # heute abfragen und in dict ablegen...
            if row[7].split()[0] == '2017-04-03':
                infos.append(row)

        #logger.debug(info)
    return infos


def send_text(recipient_id, text):
    """send a text message to a recipient"""
    recipient = {'id': recipient_id}
    message = {'text': text}
    payload = {
        'recipient': recipient,
        'message': message
    }
    send(payload)


def send_image(recipient_id, image_url):
    """send an image to a recipient"""

    recipient = {'id': recipient_id}

    # create an image object
    image = {'url': image_url}

    # add the image object to an attachment of type "image"
    attachment = {
        'type': 'image',
        'payload': image
    }

    # add the attachment to a message instead of "text"
    message = {'attachment': attachment}

    # now create the final payload with the recipient
    payload = {
        'recipient': recipient,
        'message': message
    }
    send(payload)


def send_audio(recipient_id, audio_file):
    """send an audio to a recipient"""
    audio_file = "https://mediandr-a.akamaihd.net/progressive/2017/0302/AU-20170302-0656-0300.mp3"

    recipient = {"id": recipient_id}
    audio = {'url': audio_file}
    filedata = '@' + audio_file + ';type=audio/mp3'

    attachment = {
        'type': 'audio',
        'payload': audio
    }

    message = {'attachment': attachment}

    payload = {
        'recipient': recipient,
        'message': message,
        'filedata': filedata
    }
    send(payload)


def send_generic_template(recipient_id, gifts):
    """send a generic message with title, text, image and buttons"""
    selection = []

    for key in gifts:
        logger.debug(key)
        gift = key

        title = gifts[gift]['title']
        logger.debug(title)
        item_url = gifts[gift]['link']
        image_url = 'http://www1.wdr.de/mediathek/audio/sendereihen-bilder/wdr_sendereihenbild100~_v-Podcast.jpg'
        subtitle = gifts[gift]['teaser']

        listen_Button = {
            'type': 'postback',
            'title': 'ZeitZeichen anhören',
            'payload': 'listen_audio#' + item_url
        }
        download_Button = {
            'type': 'web_url',
            'title': 'ZeitZeichen herunterladen',
            'url': item_url
        }
        visit_Button = {
            'type': 'web_url',
            'url': 'http://www1.wdr.de/radio/wdr5/sendungen/zeitzeichen/index.html',
            'title': 'Zum WDR ZeitZeichen'
        }
        share_Button = {
            'type': 'element_share'
        }
        ### Buttons sind auf max 3 begrenzt! ###
        buttons = []
        buttons.append(listen_Button)
        buttons.append(download_Button)
        buttons.append(share_Button)

        elements = {
            'title': title,
            'item_url': item_url,
            'image_url': image_url,
            'subtitle': subtitle,
            'buttons': buttons
        }

        selection.append(elements)

    load = {
            'template_type': 'generic',
            'elements': selection
        }

    attachment = {
        'type': 'template',
        'payload': load
    }

    message = {'attachment': attachment}

    recipient = {'id': recipient_id}

    payload = {
        'recipient': recipient,
        'message': message
    }
    send(payload)


def send_list_template(infos, recipient_id):
    """send a generic message with a list of choosable informations"""
    selection = []

    for info in infos:
        title = info[1]
        logger.debug(title)
        button = {
            'type': 'postback',
            'title': 'Mehr dazu',
            'payload': 'info#' + str(info[0])
        }
        buttons = []
        buttons.append(button)

        elements = {
            'title': title,
            'buttons': buttons
        }

        selection.append(elements)

    load = {
            'template_type': 'list',
            'top_element_style': 'compact',
            'elements': selection
        }

    attachment = {
        'type': 'template',
        'payload': load
    }

    message = {'attachment': attachment}

    recipient = {'id': recipient_id}

    payload = {
        'recipient': recipient,
        'message': message
    }
    send(payload)


def send(payload):
    """send a payload via the graph API"""
    logger.debug(json.dumps(payload))
    headers = {'Content-Type': 'application/json'}
    requests.post("https://graph.facebook.com/v2.6/me/messages?access_token=" + PAGE_TOKEN,
                  data=json.dumps(payload),
                  headers=headers)


if __name__ == '__main__':
    #update_data()
    #data = parse()
    #logger.debug('Content of Page written into: ' + str(data))
    app.debug = False
    app.run(port=4444)
