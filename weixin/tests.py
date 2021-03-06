# coding=utf-8
# Date: 14/12/5
# Time: 21:50
# Email:fanjunwei003@163.com
import hashlib
import datetime
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.test import TestCase
from FYAdmin.models import FYUserProfile, TaskLog
from weixin.views_api import format_time

__author__ = u'范俊伟'

message_id = 0

openid = 'sfdf33sdfdf'


def get_signature(token, timestamp, nonce):
    tmp_list = [token, timestamp, nonce]
    tmp_list.sort()
    tmp_str = ''.join(tmp_list)
    return hashlib.sha1(tmp_str).hexdigest()


def register(username, password, fy_username, fy_password):
    user = User()
    user.username = username
    user.set_password(password)
    user.email = '2342@163.com'
    user.save()
    profile = FYUserProfile()
    profile.user = user
    profile.set_fy_username(fy_username)
    profile.set_fy_password(fy_password)
    profile.save()
    return user, profile


def send_to_weixin_api(client, content):
    global message_id
    message_id += 1
    TOKEN = "pibgrj1409810714"
    timestamp = '1232323r23434'
    nonce = '234234324'
    signature = get_signature(TOKEN, timestamp, nonce)
    data = '''<xml>
<ToUserName><![CDATA[1232dfdfd]]></ToUserName>
<FromUserName><![CDATA[%s]]></FromUserName>
<CreateTime>1348831860</CreateTime>
<MsgType><![CDATA[text]]></MsgType>
<Content><![CDATA[%s]]></Content>
<MsgId>%d</MsgId>
</xml>''' % (openid, content, message_id)
    url = reverse('weixin:handleRequest') + "?timestamp=%s&nonce=%s&signature=%s" % (timestamp, nonce, signature)
    response = client.generic('POST', url, data, content_type='application/xml')
    print response


def create_test_task_log(user):
    time = datetime.datetime.now()
    TaskLog.objects.create(user=user, time=time, state=1, goodsId='SB', count=12, message='')
    TaskLog.objects.create(user=user, time=time, state=0, message='无法购买')


class ViewTest(TestCase):
    def test1(self):
        username = 'fanjunwei'
        passowrd = '123'
        user, profile = register(username, passowrd, '', '')
        create_test_task_log(user)
        send_to_weixin_api(self.client, '2')
        url = u"%s?openid=%s" % ( reverse('weixin:bind'), openid)
        response = self.client.get(url)
        # print response
        data = {
            'username': username,
            'password': passowrd,
        }
        response = self.client.post(url, data)
        # print response
        send_to_weixin_api(self.client, '3')

    def test2(self):
        test_time=datetime.datetime(2014,12,5,19,0,0)
        print format_time(test_time)

