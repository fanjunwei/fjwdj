# coding=utf-8
# Date:2014/9/24
# Email:wangjian2254@gmail.com
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

appID = 'wxe6b9104cf8fdb1d8'
appsecret = 'c0e208c32da2f2c5c7d78f1e06670835'


def handleRequest(request):
    if request.method == 'GET':
        # response = HttpResponse(request.GET['echostr'],content_type="text/plain")
        response = HttpResponse(checkSignature(request), content_type="text/plain")
        return response
    elif request.method == 'POST':
        # c = RequestContext(request,{'result':responseMsg(request)})
        # t = Template('{{result}}')
        # response = HttpResponse(t.render(c),content_type="application/xml")
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
    # rawStr = smart_str(request.POST['XML'])
    msg = paraseMsgXml(ET.fromstring(rawStr))
    msgtype = msg.get('MsgType')
    content = msg.get('Content', '')
    picurl = msg.get('PicUrl', '')
    fuid = msg['FromUserName']
    result_msg = u'test'

    items = []
    item1 = {'Title': u'测试新闻', 'Description': u'新闻内容',
             'PicUrl': 'http://i3.sinaimg.cn/dy/2014/1017/U5790P1DT20141017100148.jpg',
             'Url': 'http://fashion.sina.com.cn/z/s/2015SSshanghaiFW/'}
    item2 = {'Title': u'测试新闻1', 'Description': u'新闻内容12',
             'PicUrl': 'http://i3.sinaimg.cn/dy/2014/1017/U5790P1DT20141017100148.jpg',
             'Url': 'http://fashion.sina.com.cn/z/s/2015SSshanghaiFW/'}
    items.append(item1)
    # items.append(item2)
    text = getReplyXmlNews(msg, items)
    return text
    #return getReplyXml(msg, result_msg.encode('utf-8'))


def paraseMsgXml(rootElem):
    msg = {}
    if rootElem.tag == 'xml':
        for child in rootElem:
            msg[child.tag] = smart_str(child.text)
    return msg


def getReplyXml(msg, replyContent):
    # extTpl = "<xml><ToUserName><![CDATA[%s]]></ToUserName><FromUserName><![CDATA[%s]]></FromUserName><CreateTime>%s</CreateTime><MsgType><![CDATA[%s]]></MsgType><Content><![CDATA[%s]]></Content><FuncFlag>0</FuncFlag></xml>";
    # extTpl = extTpl % (msg['FromUserName'], msg['ToUserName'], str(int(time.time())), 'text', replyContent)
    tree = ET.fromstring('<xml></xml>')
    ToUserName = ET.Element('ToUserName')
    ToUserName.text = msg['FromUserName']
    tree.append(ToUserName)

    FromUserName = ET.Element('FromUserName')
    FromUserName.text = msg['ToUserName']
    tree.append(FromUserName)

    CreateTime = ET.Element('CreateTime')
    CreateTime.text = str(int(time.time()))
    tree.append(CreateTime)

    MsgType = ET.Element('MsgType')
    MsgType.text = 'text'
    tree.append(MsgType)

    Content = ET.Element('Content')
    Content.text = replyContent
    tree.append(Content)

    return ET.tostring(tree, 'utf8')


def getReplyXmlNews(msg, items):
    # extTpl = '''<xml>
    # <ToUserName><![CDATA[%s]]></ToUserName>
    # <FromUserName><![CDATA[%s]]></FromUserName>
    # <CreateTime>%s</CreateTime>
    # <MsgType><![CDATA[news]]></MsgType>
    # <ArticleCount>1</ArticleCount>
    # <Articles>
    # <item>
    # <Title><![CDATA[手机号实名]]></Title>
    # <Description><![CDATA[%s]]></Description>
    # <PicUrl><![CDATA[%s]]></PicUrl>
    # <Url><![CDATA[]]></Url>
    # </item>
    # </Articles>
    # </xml> '''
    # extTpl = extTpl % (msg['FromUserName'], msg['ToUserName'], str(int(time.time())), replyContent, url)
    # return extTpl
    tree = ET.fromstring('<xml></xml>')
    tree.append(getTextElement('ToUserName', msg['FromUserName']))
    tree.append(getTextElement('FromUserName', msg['ToUserName']))
    tree.append(getTextElement('CreateTime', str(int(time.time()))))
    tree.append(getTextElement('MsgType', 'news'))
    tree.append(getTextElement('ArticleCount', str(len(items))))
    Articles = ET.Element('Articles')
    for i in items:
        Articles.append(getNewsElement(i))
    tree.append(Articles)
    return ET.tostring(tree, 'utf8')


def getTextElement(tag, text):
    element = ET.Element(tag)
    element.text = text
    return element


def getNewsElement(item):
    element = ET.fromstring('<item></item>')

    ETitle = ET.Element('Title')
    ETitle.text = item.get('Title', '')
    element.append(ETitle)

    EDescription = ET.Element('Description')
    EDescription.text = item.get('Description', '')
    element.append(EDescription)

    EPicUrl = ET.Element('PicUrl')
    EPicUrl.text = item.get('PicUrl', '')
    element.append(EPicUrl)

    EUrl = ET.Element('Url')
    EUrl.text = item.get('Url', '')
    element.append(EUrl)

    return element


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
# import os,uuid
# try:
# f = urllib2.urlopen(url)
# data = f.read()
# filename = str(uuid.uuid4())
# with open("%s/%s" % (os.path.join(MEDIA_ROOT, "idimg"), filename), "wb") as code:
# code.write(data)
# truename = Truename.objects.get(pk=trueid)
# if truename.idstatus < 2:
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