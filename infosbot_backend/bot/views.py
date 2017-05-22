import os
import json

from django.shortcuts import render

from . import bot

HUB_VERIFY_TOKEN = os.environ['INFOSBOT_HUB_VERIFY_TOKEN']


def webhook(request):
    if request.method == 'GET':
        if request.GET.get('hub.verify_token') == HUB_VERIFY_TOKEN:
            return request.GET['hub.challenge']
        else:
            return 'Hello World!'

    elif request.method == 'POST':
        data = json.load(request.body.decode())
        bot.handle_messages(data)
        return "ok"


