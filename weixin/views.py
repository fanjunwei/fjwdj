# coding=utf-8
# Date:2014/9/24
#Email:wangjian2254@gmail.com
import httplib
import json, base64
import uuid
from django.contrib.auth.models import User


__author__ = u'王健'

from django.http import HttpResponse
from django.template import RequestContext, Template
from django.views.decorators.csrf import csrf_exempt
from django.utils.encoding import smart_str, smart_unicode

import xml.etree.ElementTree as ET
import urllib, urllib2, time, hashlib

TOKEN = "pibgrj1409810714"

HANWANG_KEY = '3b1c7302-4d31-4c56-b034-94b48e59dd5d'

YOUDAO_KEY = '你申请到的有道的Key'
YOUDAO_KEY_FROM = "有道的key-from"
YOUDAO_DOC_TYPE = "xml"

YUNMAI_USERNAME = 'test141001'
YUNMAI_PASSWORD = 'asdg23sdgsuUILo878sdsdf'
YUNMAI_URL = 'http://eng.ccyunmai.com:5008/SrvEngine'


def handleRequest(request):
    if request.method == 'GET':
        #response = HttpResponse(request.GET['echostr'],content_type="text/plain")
        response = HttpResponse(checkSignature(request), content_type="text/plain")
        return response
    elif request.method == 'POST':
        #c = RequestContext(request,{'result':responseMsg(request)})
        #t = Template('{{result}}')
        #response = HttpResponse(t.render(c),content_type="application/xml")
        response = HttpResponse(responseMsg(request), content_type="application/xml")
        return response
    else:
        return None


def checkSignature(request):
    global TOKEN
    signature = request.GET.get("signature", None)
    timestamp = request.GET.get("timestamp", None)
    nonce = request.GET.get("nonce", None)
    echoStr = request.GET.get("echostr", None)

    token = TOKEN
    tmpList = [token, timestamp, nonce]
    tmpList.sort()
    tmpstr = "%s%s%s" % tuple(tmpList)
    tmpstr = hashlib.sha1(tmpstr).hexdigest()
    if tmpstr == signature:
        return echoStr
    else:
        return None


def responseMsg(request):
    rawStr = smart_str(request.body)
    #rawStr = smart_str(request.POST['XML'])
    msg = paraseMsgXml(ET.fromstring(rawStr))
    msgtype = msg.get('MsgType')
    content = msg.get('Content', '')
    picurl = msg.get('PicUrl', '')
    fuid = msg['FromUserName']
    result_msg = u'test'

    return getReplyXml(msg, result_msg.encode('utf-8'))


def paraseMsgXml(rootElem):
    msg = {}
    if rootElem.tag == 'xml':
        for child in rootElem:
            msg[child.tag] = smart_str(child.text)
    return msg


def getReplyXml(msg, replyContent):
    extTpl = "<xml><ToUserName><![CDATA[%s]]></ToUserName><FromUserName><![CDATA[%s]]></FromUserName><CreateTime>%s</CreateTime><MsgType><![CDATA[%s]]></MsgType><Content><![CDATA[%s]]></Content><FuncFlag>0</FuncFlag></xml>";
    extTpl = extTpl % (msg['FromUserName'], msg['ToUserName'], str(int(time.time())), 'text', replyContent)
    return extTpl

def getReplyXmlImg(msg, replyContent,url=''):
    extTpl='''<xml>
<ToUserName><![CDATA[%s]]></ToUserName>
<FromUserName><![CDATA[%s]]></FromUserName>
<CreateTime>%s</CreateTime>
<MsgType><![CDATA[news]]></MsgType>
<ArticleCount>1</ArticleCount>
<Articles>
<item>
<Title><![CDATA[手机号实名]]></Title>
<Description><![CDATA[%s]]></Description>
<PicUrl><![CDATA[%s]]></PicUrl>
<Url><![CDATA[]]></Url>
</item>
</Articles>
</xml> '''
    extTpl = extTpl % (msg['FromUserName'], msg['ToUserName'], str(int(time.time())), replyContent, url)
    return extTpl

def eventMsg(msg):
    eventtype = msg.get('Event')
    eventkey = msg.get('EventKey', '')

    if eventtype == 'CLICK':
        if eventkey == 'user':
            # 注册
            pass
        elif eventkey == 'shiming':
            # 实名
            pass
    elif eventtype == 'subscribe':
        pass


# def downloadIDimage(url, trueid):
#     import os,uuid
#     try:
#         f = urllib2.urlopen(url)
#         data = f.read()
#         filename = str(uuid.uuid4())
#         with open("%s/%s" % (os.path.join(MEDIA_ROOT, "idimg"), filename), "wb") as code:
#             code.write(data)
#         truename = Truename.objects.get(pk=trueid)
#         if truename.idstatus < 2:
#             truename.imgfile = '%s/%s'%('idimg', filename)
#             truename.idstatus = 2
#             truename.save()
#         return True
#     except Exception,e:
#         return False



def paraseResultXml(rootElem):
    msg = {}
    if rootElem.tag == 'xml':
        for child in rootElem:
            if child.text:
                msg[child.tag] = smart_str(child.text)
            else:
                for c in child:
                    msg[c.tag] = smart_str(c.text)

    return msg