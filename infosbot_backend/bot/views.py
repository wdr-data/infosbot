import os
import json
import logging

from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse

from . import bot

HUB_VERIFY_TOKEN = os.environ.get('INFOSBOT_HUB_VERIFY_TOKEN', 'na')
logger = logging.getLogger(__name__)


@csrf_exempt
def webhook(request):
    if request.method == 'GET':
        if request.GET.get('hub.verify_token') == HUB_VERIFY_TOKEN:
            return HttpResponse(request.GET['hub.challenge'], content_type="text/plain")
        else:
            return HttpResponse('Hello World!', content_type="text/plain")

    elif request.method == 'POST':
        data = json.loads(request.body.decode())
        try:
            bot.handle_messages(data)
        except:
            logger.exception("Error handling messages")
        return HttpResponse("ok", content_type="text/plain")


