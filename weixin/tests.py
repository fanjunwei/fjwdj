# coding=utf-8
# Date: 14/12/5
# Time: 21:50
# Email:fanjunwei003@163.com
import hashlib
from django.core.urlresolvers import reverse
from django.test import TestCase

__author__ = u'范俊伟'


def get_signature(token, timestamp, nonce):
    tmp_list = [token, timestamp, nonce]
    tmp_list.sort()
    tmp_str = ''.join(tmp_list)
    return hashlib.sha1(tmp_str).hexdigest()


class ViewTest(TestCase):
    def test(self):
        TOKEN = "pibgrj1409810714"

        timestamp = '1232323r23434'
        nonce = '234234324'
        signature = get_signature(TOKEN, timestamp, nonce)
        data = '''<xml>
 <ToUserName><![CDATA[1232dfdfd]]></ToUserName>
 <FromUserName><![CDATA[sfdf33sdfdf]]></FromUserName>
 <CreateTime>1348831860</CreateTime>
 <MsgType><![CDATA[text]]></MsgType>
 <Content><![CDATA[2]]></Content>
 <MsgId>452234342343</MsgId>
 </xml>'''
        url = reverse('weixin:handleRequest') + "?timestamp=%s&nonce=%s&signature=%s" % (timestamp, nonce, signature)
        response = self.client.generic('POST', url, data, content_type='application/xml')
        print response