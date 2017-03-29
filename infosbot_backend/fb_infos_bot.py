from flask import Flask, request
from os.path import basename, isfile, join
from urllib.request import urlopen, Request
from urllib.parse import urlencode
from bs4 import BeautifulSoup
from lxml import html
from mutagen.id3 import ID3, TCON
from requests_toolbelt.multipart.encoder import MultipartEncoder
import requests
import datetime
import re

import json
import logging

 #Enable logging
logger = logging.getLogger(__name__)
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO, filename='infos_logger.log', filemode='a')

logger.setLevel(logging.DEBUG)
logger.debug('fb Infos Bot Logging')

SEARCH, SELECT = range(2)

PAGE_TOKEN="EAAY1oJrTs2QBACGZAZCZCZC8KFW9ZBtNn4zEVpH7Cxf75g7xZAqPjoqoFpwnv3K87t8E3miHf4Fd1cHsUwue36Gh55ZAaXgafltAj2Y4LBpSNl7tV3ClbMJ7ScX3zJSSOmZCaljoAD0uDlNL1uLss2knLGK1KZC0FzWrPiZCnSlCa365pnfAxbJakh"
items = None

app = Flask(__name__)


@app.route('/testbot', methods=["GET"])
def confirm():
    if request.args.get('hub.verify_token') == "vcp3yqdkm7h1hz7hekot":
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
    print(messaging_events)
    for event in messaging_events:
        sender_id = event['sender']['id']

        # check if we actually have some input
        if "message" in event and event['message'].get("text","") != "":
            print('received message')
            text = event['message']['text']
            reply = "echo: " +text
            send_text(sender_id, reply)
        elif "postback" in event and event['postback'].get("payload","") == "start":
            reply = "Herzlich willkommen zum 1LIVE InfoMessenger. \n\nHier bekommst Du alle Infos geliefert, die Du wissen musst, um mitreden zu können, selbst die, von denen Du nicht weißt, dass Du sie wissen wolltest :) \n\nWas Du dafür tun musst: Fast nichts."
            send_text(sender_id, reply)
        # elif "postback" in event and event['postback'].get("payload","").split("#")[0] == "listen_audio":
        #     audio_url = event['postback'].get("payload","").split("#")[1]
        #     audio_file = get_audio(audio_url)
        #     send_audio(sender_id, audio_file)
            #reply = "Zukünftig wird dir hier ein Audio geschickt..."
            #send_text(sender_id, reply)

def send_text(recipient_id, text):
    """send a text message to a recipient"""
    recipient = { 'id' : recipient_id }
    message = { 'text' : text }
    payload = {
        'recipient' : recipient,
        'message' : message
    }
    send(payload)

def send_image(recipient_id, image_url):
    """send an image to a recipient"""

    recipient = { 'id' : recipient_id }

    # create an image object
    image = { 'url' : image_url }

    # add the image object to an attachment of type "image"
    attachment = {
        'type'      : 'image',
        'payload'   : image
    }

    # add the attachment to a message instead of "text"
    message = { 'attachment' : attachment }

    # now create the final payload with the recipient
    payload = {
        'recipient' : recipient,
        'message' : message
    }
    send(payload)

def send_audio(recipient_id, audio_file):
    """send an audio to a recipient"""
    audio_file = "https://mediandr-a.akamaihd.net/progressive/2017/0302/AU-20170302-0656-0300.mp3"

    recipient = { "id" : recipient_id }
    audio = { 'url' : audio_file }
    filedata= '@' + audio_file + ';type=audio/mp3'

    attachment = {
        'type' : 'audio',
        'payload' : audio
    }

    message = { 'attachment' : attachment }

    payload = {
        'recipient' : recipient,
        'message' : message,
        'filedata' : filedata
    }


    send(payload)

def send_generic_template(recipient_id, gifts):
    """send a generic message with title, text, image and buttons"""
    selection = []

    for key in gifts:
        print(key)
        gift = key

        title = gifts[gift]['title']
        print (title)
        item_url = gifts[gift]['link']
        image_url = 'http://www1.wdr.de/mediathek/audio/sendereihen-bilder/wdr_sendereihenbild100~_v-Podcast.jpg'
        subtitle = gifts[gift]['teaser']
        listen_Button = {
            'type' : 'postback',
            'title' : 'ZeitZeichen anhören',
            'payload' : 'listen_audio#' + item_url
        }
        download_Button = {
            'type' : 'web_url',
            'title' : 'ZeitZeichen herunterladen',
            'url' : item_url
        }
        visit_Button = {
            'type' : 'web_url',
            'url' : 'http://www1.wdr.de/radio/wdr5/sendungen/zeitzeichen/index.html',
            'title' : 'Zum WDR ZeitZeichen'
        }
        share_Button = {
            'type' : 'element_share'
        }
	### Buttons sind auf max 3 begrenzt! ###
        buttons = []
        buttons.append(listen_Button)
        buttons.append(download_Button)
        #buttons.append(visit_Button)
        buttons.append(share_Button)

        elements = {
            'title' : title,
            'item_url' : item_url,
            'image_url' : image_url,
            'subtitle' : subtitle,
            'buttons' : buttons
        }

        selection.append(elements)

    load = {
            'template_type' : 'generic',
            'elements' : selection
        }

    attachment = {
        'type' : 'template',
        'payload' : load
    }

    message = { 'attachment' : attachment }

    recipient = { 'id' : recipient_id }

    payload = {
        'recipient' : recipient,
        'message' : message
    }
    send(payload)

def send(payload):
    """send a payload via the graph API"""
    #print(json.dumps(payload))
    headers = {'Content-Type': 'application/json'}
    r = requests.post("https://graph.facebook.com/v2.6/me/messages?access_token="+PAGE_TOKEN,
        data = json.dumps(payload),
        headers = headers)

if __name__ == '__main__':
    #update_data()
    #data = parse()
    #logger.debug('Content of Page written into: ' + str(data))
    app.debug = False
    app.run(port=4444)
