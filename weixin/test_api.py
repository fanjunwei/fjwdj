# coding=utf-8
import json

__author__ = 'fanjunwei003'
import xml.etree.ElementTree as ET
import urllib
import urllib2

g_access_token = '5MsPNj7cWMnV3Fh0vNh2_Rl-P4STnL1ifg1tlkys1kHBCilRp_FJRiS0YC7uOvw2pEZruUxpsDP7SW_5L1MxKUAYDHwamXBLYUnC9BRpSfs'

appID = 'wxe6b9104cf8fdb1d8'
appsecret = 'c0e208c32da2f2c5c7d78f1e06670835'

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


def send_message(access_token, user_id, message):
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


def create_erweima_ticket(access_token, scene_id):
    url = 'https://api.weixin.qq.com/cgi-bin/qrcode/create?access_token=' + access_token
    data = {"expire_seconds": 1800,
            "action_name": "QR_SCENE",
            "action_info":
                {"scene": {"scene_id": int(scene_id)}}}
    req = urllib2.Request(url, json.dumps(data, ensure_ascii=False))
    response = urllib2.urlopen(req)
    res = response.read()
    return res


def get_erweima_url(ticket):
    return 'https://mp.weixin.qq.com/cgi-bin/showqrcode?' + urllib.urlencode({'ticket': ticket})


def get_userinfo(access_token, user_id):
    url_parms = {'access_token': access_token,
                 'openid': user_id,
                 'lang': 'zh_CN'}
    url = 'https://api.weixin.qq.com/cgi-bin/user/info?' + urllib.urlencode(url_parms)
    f = urllib.urlopen(url)
    data = f.read()
    f.close()
    return data


def get_user_list(access_token):
    openids = []
    next_openid = None
    while True:
        url_parms = {'access_token': access_token}
        if next_openid:
            url_parms['next_openid'] = next_openid
        url = 'https://api.weixin.qq.com/cgi-bin/user/get?' + urllib.urlencode(url_parms)
        f = urllib.urlopen(url)
        data = f.read()
        f.close()
        jo=json.loads(data)
        j_data=jo.get('data',None)
        if j_data:
            j_openid=j_data.get('openid',None)
            if j_openid:
                openids.append(j_openid)
        next_openid=jo.get('next_openid',None)
        if not next_openid:
            break

    return openids


if __name__ == '__main__':
    # print send_message(g_access_token, 'oygUbtyUX1gpV0TEuuj9U9W1FHh8', 'hello')
    # res = json.loads(create_erweima_ticket(g_access_token, 12323))
    # ticket = res.get('ticket', '').encode('utf8')
    #
    # print get_erweima_url(ticket)
    # print get_userinfo(g_access_token,'oygUbtyUX1gpV0TEuuj9U9W1FHh8')
    print get_user_list(g_access_token)

# appID = 'wxe6b9104cf8fdb1d8'
# appsecret = 'c0e208c32da2f2c5c7d78f1e06670835'
# print get_access_token(appID, appsecret)
