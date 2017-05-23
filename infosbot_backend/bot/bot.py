import json
import logging
import os
import csv

from flask import Flask, request
import requests
#from django.utils.timezone import localtime, now
from django.utils import timezone
from fuzzywuzzy import fuzz, process

from backend.models import Info, FacebookUser, Dialogue
from .fb import (send, send_text, send_text_with_button, send_image, send_audio,
                 send_generic_template, send_list_template, send_text_and_quickreplies)

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
        if "message" in event and event['message'].get("quick_reply", "") != "":
            quick_reply = event['message']['quick_reply']['payload']
            if quick_reply.split("#")[0] == 'info':
                info_id = quick_reply.split('#')[1]
                info_set = quick_reply.split('#')[2]
                data = Info.objects.get(id=info_id)
                send_info(sender_id, data, info_set)

                # reply = 'Es geht los'
                # send_text(sender_id, reply)
        elif "message" in event and event['message'].get("text", "") != "" and event['message'].get('quick_reply') == None:
            logger.debug('received message')
            text = event['message']['text']
            if text == '/info':
                data = get_data()
                schema(data, sender_id)
                #send_list_template(data, sender_id)
            elif text == '/testpush':
                reply = "Push Notification Test..."
                send_text(sender_id, reply)
                push_notification()
                # data = get_data()
                # send_list_template(data, sender_id)
            elif text == '/config':
                reply = "Hier kannst du deine facebook Messenger-ID hinterlegen um automatisch ein tägliches Update von uns zu erhalten.\n" \
                        "Wenn du dich registieren möchtest klicke \"OK\". Du kannst deine Entscheidung jederzet wieder ändern."
                send_text_with_button(sender_id, reply)
            else:
                dialogues = Dialogue.objects.all()
                best_match = process.extractOne(
                    text,
                    dialogues,
                    scorer=fuzz.token_set_ratio,
                    score_cutoff=50)

                if best_match:
                    reply = best_match[0].output
                else:
                    reply = "Tut mir Leid, darauf habe ich keine Antwort."

                send_text(sender_id, reply)
        elif "postback" in event and event['postback'].get("payload", "") == "start":
            reply = "Herzlich willkommen zum 1LIVE InfoMessenger. \n\n" \
                    "Hier bekommst Du alle Infos geliefert, die Du wissen musst, um mitreden zu " \
                    "können, selbst die, von denen Du nicht weißt, dass Du sie wissen wolltest :)" \
                    "\nWas Du dafür tun musst: Fast nichts." \
                    "\n\nUm dich für dein automatisches Update zu registrieren klicke auf \"OK\"."
            send_text_with_button(sender_id, reply)
        elif "postback" in event and event['postback'].get("payload", "").split("#")[0] == "info":
            info_id = quick_reply.split('#')[1]
            info_set = quick_reply.split('#')[2]
            data = Info.objects.get(id=info_id)
            next_id = Info.objects.filter(id__gt = info_id)[:1]
            send_text_with_button(sender_id, data, next_id, info_set)
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
        elif "postback" in event and event['postback'].get("payload", "") == "back":
            data = get_data()
            #send_list_template(data, sender_id)

def get_data():
    today = timezone.localtime(timezone.now()).date()
    infos = Info.objects.filter(pub_date__date=today, published=True)
    logger.info("Got %s infos", len(infos))
    return infos

def schema(data, user_id):
    reply = "Heute haben wir folgende Themen für dich: \n"
    first_id = None

    for info in data:
        if first_id is None:
            first_id = info.id
        reply += ' +++ ' + info.headline
    reply += ' +++ '

    quickreplies = []
    button = {
        'content_type' : 'text',
        'title' : "Los geht's",
        'payload' : 'info#' + str(first_id) + '#intro'
    }
    quickreplies.append(button)

    send_text_and_quickreplies(reply, quickreplies, user_id)

def send_info(user_id, data, status):
    try:
        today = timezone.localtime(timezone.now()).date()
        next_id = Info.objects.filter(id__gt=data.id, pub_date__date=today, published=True)[:1][0].id
    except IndexError:
        next_id = None

    if status == "intro":
        status_id = 'one'
        reply = data.intro_text
        button_title = data.first_question
    elif status == "one":
        status_id = 'two'
        reply = data.first_text
        button_title = data.second_question
    elif status == "two":
        status_id = 'next'
        reply = data.second_text
        button_title = "None"

    quickreplies = []
    more_button = {
        'content_type' : 'text',
        'title' : button_title,
        'payload' : 'info#' + str(data.id) + '#' + str(status_id)
    }
    next_button = {
        'content_type': 'text',
        'title': 'Nächste Info',
        'payload': 'info#' + str(next_id) + '#intro'
    }
    if status_id == 'next' and next_id is not None:
        quickreplies.append(next_button)
        send_text_and_quickreplies(reply, quickreplies, user_id)
    elif status_id != 'next' and next_id is not None:
        quickreplies.append(more_button)
        quickreplies.append(next_button)
        send_text_and_quickreplies(reply, quickreplies, user_id)
    elif status_id != 'next' and next_id is None:
        quickreplies.append(more_button)
        send_text_and_quickreplies(reply, quickreplies, user_id)
    elif status_id == 'next' and next_id is None:
        send_text(user_id, reply)


def subscribe_user(user_id):
    if FacebookUser.objects.filter(uid = user_id).exists():
        reply = "Du bist bereits für Push Nachrichten angemeldet."
        send_text(user_id, reply)
    else:
        FacebookUser.objects.create(uid = user_id)
        logger.debug('User with ID ' + str(FacebookUser.objects.latest('add_date')) + ' subscribed.')
        reply = "Danke für deine Anmeldung!\nDu erhältst nun ein tägliches Update jeweils um 8:00 Uhr wochentags."
        send_text(user_id, reply)

def unsubscribe_user(user_id):
    if FacebookUser.objects.filter(uid = user_id).exists():
        logger.debug('User with ID ' + str(FacebookUser.objects.get(uid = user_id)) + ' unsubscribed.')
        FacebookUser.objects.get(uid = user_id).delete()
        reply = "Du wurdest aus der Empfängerliste für Push Benachrichtigungen gestrichen. Danke!"
        send_text(user_id, reply)
    else:
        reply = "Du bist noch kein Nutzer der Push Nachrichten. Wenn du dich anmelden möchtest wähle \'Anmelden\' im Menü."
        send_text(user_id, reply)

def push_notification():
    data = get_data()
    user_list = FacebookUser.objects.values_list('uid', flat=True)
    for user in user_list:
        logger.debug("Send Push to: " + user)
        reply = "Heute haben wir folgende Themen für dich:"
        send_text(sender_id, reply)
        send_list_template(data, user)
