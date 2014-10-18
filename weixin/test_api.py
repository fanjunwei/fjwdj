# coding=utf-8
import json

__author__ = 'fanjunwei003'
import xml.etree.ElementTree as ET
import urllib
import urllib2

g_access_token = 'F5ha7ANRUbG29bxsYmi9eUiDulDqRKOwfpmkapr_xNCceWIhbTpjT794Xf4udP1njsQAegGlxMNHT4HVtKND_j_mdcgjJru1FhmfrTmK1Es'


def test():
    tree = ET.fromstring('<xml></xml>')
    fromE = ET.Element('ToUserName')
    fromE.text = 'sfsdfsdfsdf'
    tree.append(fromE)
    print ET.tostring(tree, 'utf8')


def get_access_token(appid, secret):
    f = urllib.urlopen(
        'https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid=%s&secret=%s' % (appid, secret))
    data = f.read()
    f.close()
    return data


def set_menu(access_token):
    url = 'https://api.weixin.qq.com/cgi-bin/menu/create?access_token=' + access_token
    data = {
        "button": [
            {
                "type": "click",
                "name": "今日歌曲",
                "key": "V1001_TODAY_MUSIC"
            },
            {
                "name": "菜单",
                "sub_button": [
                    {
                        "type": "view",
                        "name": "搜索",
                        "url": "http://www.soso.com/"
                    },
                    {
                        "type": "view",
                        "name": "视频",
                        "url": "http://v.qq.com/"
                    },
                    {
                        "type": "click",
                        "name": "赞一下我们",
                        "key": "V1001_GOOD"
                    }]
            }]
    }
    req = urllib2.Request(url, json.dumps(data, ensure_ascii=False))
    response = urllib2.urlopen(req)
    res = response.read()
    return res


def send_message(access_token, user_id,message):
    url = 'https://api.weixin.qq.com/cgi-bin/message/custom/send?access_token=' + access_token
    data = {
        "touser": user_id,
        "msgtype": "text",
        "text":
            {
                "content": message
            }
    }
    req = urllib2.Request(url, json.dumps(data, ensure_ascii=False))
    response = urllib2.urlopen(req)
    res = response.read()
    return res


if __name__ == '__main__':
    print send_message(g_access_token,'oygUbtyUX1gpV0TEuuj9U9W1FHh8','hello')
# appID = 'wxe6b9104cf8fdb1d8'
# appsecret = 'c0e208c32da2f2c5c7d78f1e06670835'
# print get_access_token(appID, appsecret)
