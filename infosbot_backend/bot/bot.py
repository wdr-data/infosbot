import json
import logging
import os
import csv

from flask import Flask, request
import requests
#from django.utils.timezone import localtime, now
from django.utils import timezone

from ..backend.models import Info, FacebookUser
from .fb import (send, send_text, send_text_with_button, send_image, send_audio,
                 send_generic_template, send_list_template)

# TODO: The idea is simple. When you send "subscribe" to the bot, the bot server would add a record according to the sender_id to their
# database or memory , then the bot server could set a timer to distribute the news messages to those sender_id who have subscribed for the news.

# Enable logging
logger = logging.getLogger(__name__)

logger.info('FB Infos Bot Logging')


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
                reply = "Heute haben wir folgende Themen für dich:"
                send_text(sender_id, reply)
                data = get_data()
                send_list_template(data, sender_id)
            elif text == '/config':
                reply = "Hier kannst du deine facebook Messenger-ID hinterlegen um automatisch ein tägliches Update von uns zu erhalten.\n" \
                        "Wenn du dich registiren möchtest klicke \"OK\". Du kannst deine Entscheidung jederzet wieder ändern."
                send_text_with_button(sender_id, reply)
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
            requested_info_id = event['postback'].get("payload", "").split("#")[1]
            info = Info.objects.get(id=int(requested_info_id))
            status = "intro"
            send_text(sender_id, info.headline)
            if info.media != "":
                image = "https://infos.data.wdr.de/backend/static/media/" + str(info.media)
                send_image(sender_id, image)
            logger.debug("status in postback: " + status)
            send_text_with_button(sender_id, info, status)
        elif "postback" in event and event['postback'].get("payload", "").split("#")[0] == "more":
            requested_info_id = event['postback'].get("payload", "").split("#")[2]
            info = Info.objects.get(id=int(requested_info_id))
            logger.debug(event['postback'].get("payload", "").split("#")[1])
            if event['postback'].get("payload", "").split("#")[1] == "0":
                status = "one"
            elif event['postback'].get("payload", "").split("#")[1] == "1":
                status = "two"
            send_text_with_button(sender_id, info, status)
            # reply = "Hier folgen weitere Infos zum Thema."
            # send_text(sender_id, reply)
        elif "postback" in event and event['postback'].get("payload", "").split("#")[0] == "subscribe":
            subscribe_user(sender_id)
            reply = "Danke für deine Anmeldung!\nDu erhältst nun ein tägliches Update jeweils um 8:00 Uhr wochentags."
            send_text(sender_id, reply)
        elif "postback" in event and event['postback'].get("payload", "") == "back":
            data = get_data()
            send_list_template(data, sender_id)


def get_data():
    today = timezone.localtime(timezone.now()).date()
    return Info.objects.filter(pub_date__date=today)[:4]


def subscribe_user(user_id):
    FacebookUser.objects.create(uid = user_id)
    logger.debug('User with ID ' + FacebookUser.objects.latest('add_date') + ' subscribed.')
