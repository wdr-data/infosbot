import os
import json

from django.shortcuts import render
from django.http import HttpResponse

from . import bot

HUB_VERIFY_TOKEN = os.environ.get('INFOSBOT_HUB_VERIFY_TOKEN', 'na')


def webhook(request):
    if request.method == 'GET':
        if request.GET.get('hub.verify_token') == HUB_VERIFY_TOKEN:
            return HttpResponse(request.GET['hub.challenge'], content_type="text/plain")
        else:
            return HttpResponse('Hello World!', content_type="text/plain")

    elif request.method == 'POST':
        data = json.load(request.body.decode())
        bot.handle_messages(data)
        return HttpResponse("ok", content_type="text/plain")


