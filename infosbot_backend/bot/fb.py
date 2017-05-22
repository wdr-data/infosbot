import os
import json
import logging

import requests

PAGE_TOKEN = os.environ['INFOSBOT_PAGE_TOKEN']
logger = logging.getLogger(__name__)


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


def send_text_with_button(recipient_id, info, status="other"):
    """send a message with a button (1-3 buttons possible)"""
    if status == "intro":
        status_id = 0
        text = info.intro_text
        button_title = info.first_question
    elif status == "one":
        status_id = 1
        text = info.first_text
        button_title = info.second_question
    elif status == "two":
        status_id = 2
        text = info.second_text
        button_title = "None"
    elif status == "other":
        status_id = 3
        text = info
        button_title = "OK"

    logger.debug("Text: " + str(text) + ", info.introtext: " + str(info.intro_text))
    logger.debug("Status at send_text_with_button: " + str(status) + " " + str(status_id))

    if status_id == 3:
        task = 'subscribe#' + recipient_id
    else:
        task = 'more#' + str(status_id) + '#' + str(info.id)

    more_button = {
        'type': 'postback',
        'title': button_title,
        'payload': task
    }

    back_button = {
        'type': 'postback',
        'title': 'Zurück',
        'payload': 'back'
    }
    buttons = []
    if status_id == 2:
        buttons.append(back_button)
    else:
        buttons.append(more_button)
        buttons.append(back_button)

    load = {
            'template_type': 'button',
            'text': text,
            'buttons': buttons
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
    logger.debug("Payload from send_text_with_button: " + str(payload))
    send(payload)


def send_list_template(infos, recipient_id):
    """send a generic message with a list of choosable informations"""
    selection = []
    count = 0

    for info in infos:
        count += 1
        title = info.headline
        logger.debug(title)

        button = {
            'type': 'postback',
            'title': 'Mehr dazu',
            'payload': 'info#' + str(info.id) + '#' + str(count)
        }
        buttons = []
        buttons.append(button)

        if info.media != "":
            image = "https://infos.data.wdr.de/backend/static/media/" + str(info.media)
            elements = {
                'title': title,
                'image_url': image,
                'buttons': buttons
            }
        else:
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
    logger.debug("JSON Payload: " + json.dumps(payload))
    headers = {'Content-Type': 'application/json'}
    requests.post("https://graph.facebook.com/v2.6/me/messages?access_token=" + PAGE_TOKEN,
                  data=json.dumps(payload),
                  headers=headers)