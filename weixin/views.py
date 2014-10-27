# coding=utf-8
# Date:2014/9/24
# Email:wangjian2254@gmail.com

from django.core.cache import cache
from fy.fy_query import getFyMoneySupply
from wechat_sdk import WechatBasic
from django.http import HttpResponse

TOKEN = "pibgrj1409810714"


def handleRequest(request):
    signature = request.GET.get("signature", None)
    timestamp = request.GET.get("timestamp", None)
    nonce = request.GET.get("nonce", None)
    wechat = WechatBasic(token=TOKEN)
    if request.method == 'GET':
        echoStr = request.GET.get("echostr", None)
        if wechat.check_signature(signature, timestamp, nonce):
            response = HttpResponse(echoStr, content_type="text/plain")
        else:
            response = HttpResponse(None, content_type="text/plain")
        return response
    elif request.method == 'POST':
        if wechat.check_signature(signature, timestamp, nonce):
            response = HttpResponse(responseMsg(request, wechat), content_type="application/xml")
        else:
            response = HttpResponse(None, content_type="application/xml")

        return response
    else:
        return None


def responseMsg(request, wechat):
    wechat.parse_data(request.body)
    message = wechat.get_message()
    helperText = u'''平台测试中
QQ：81300697
回复1：获取泛亚有色金属最新资金配比情况'''
    if message.type == 'text':
        if message.content == '1':
            try:
                return wechat.response_text(getFyMoneySupply().decode('utf8'))
            except Exception, e:
                print str(e)

    return wechat.response_text(helperText)