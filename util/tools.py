# coding=utf-8
# Date: 11-12-8
# Time: 下午10:28
import json
import threading

from django.http import HttpResponse
from django.core.cache import cache
from wechat_sdk import WechatBasic
from wechat_sdk.exceptions import OfficialAPIError

__author__ = u'王健'

wechatObjLock = threading.RLock()


def jsonResponse(data):
    return HttpResponse(json.dumps(data), 'application/json')