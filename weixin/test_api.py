# coding=utf-8
__author__ = 'fanjunwei003'
import json
import xml.etree.ElementTree as ET
import urllib
import urllib2
from poster.encode import multipart_encode
from poster.streaminghttp import register_openers

g_access_token = 'tsgkJaQNFBIqpPlZu9TogDGQcb_OaSomwNhN6y9WGbzwSD_KcGkLzQHJNV3qLRFf_M7TelatQwTq4CZpaxZSkF0DOApYhqrRq-K_j-gWIL4'

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
    return json.loads(data)


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
        jo = json.loads(data)
        j_data = jo.get('data', None)
        if j_data:
            j_openid = j_data.get('openid', None)
            if j_openid:
                openids.append(j_openid)
        next_openid = jo.get('next_openid', None)
        if not next_openid:
            break

    return openids


def upload_media(access_token, type, file_path):
    '''
    上传资源
    :param access_token:
    :param type: image,voice,video,thumb
    :return:{"type":"image","media_id":"G6TUmSkGlfA7wR88lRdTmEXyOpUszWOTAaGpu1Me4UyogqVQawGWj0liPUIFTc8R","created_at":1413693421}
    '''
    url_parms = {'access_token': access_token,
                 'type': type}
    url = 'http://file.api.weixin.qq.com/cgi-bin/media/upload?' + urllib.urlencode(url_parms)
    register_openers()
    datagen, headers = multipart_encode({"media": open(file_path, "rb")})
    request = urllib2.Request(url, datagen, headers)
    result = urllib2.urlopen(request).read()
    return result


def download_media(access_token, media_id):
    '''
    下载媒体文件
    :param access_token:
    :param media_id:
    :return:
    '''
    url_parms = {'access_token': access_token,
                 'media_id': media_id}
    url = 'http://file.api.weixin.qq.com/cgi-bin/media/get?' + urllib.urlencode(url_parms)
    response = urllib.urlopen(url)
    result = response.read()
    content_type = response.headers.get('Content-Type', '')
    if content_type.find('text') != -1 or content_type.find('json') != -1:
        raise Exception(result)
    else:
        return result


if __name__ == '__main__':
    g_access_token = get_access_token(appID, appsecret).get('access_token',None)
    print g_access_token
    # data = download_media(g_access_token, 'G6TUmSkGlfA7wR88lRdTmEXyOpUszWOTAaGpu1Me4UyogqVQawGWj0liPUIFTc8R')
    # f = open('img.jpg', 'wr')
    # f.write(data)
    # f.close()

    # print upload_media(g_access_token, 'image', '/Users/fanjunwei003/Desktop/wvgalnl_uboot.jpg')
    # print get_userinfo(g_access_token, 'oygUbtyUX1gpV0TEuuj9U9W1FHh8')
# g_access_token = get_access_token(appID, appsecret).get('access_token',None)
# if g_access_token:
# print(g_access_token)

# print send_message(g_access_token, 'oygUbtyUX1gpV0TEuuj9U9W1FHh8', 'hello')
# res = json.loads(create_erweima_ticket(g_access_token, 12323))
# ticket = res.get('ticket', '').encode('utf8')
#
# print get_erweima_url(ticket)
# print get_userinfo(g_access_token,'oygUbtyUX1gpV0TEuuj9U9W1FHh8')

# appID = 'wxe6b9104cf8fdb1d8'
# appsecret = 'c0e208c32da2f2c5c7d78f1e06670835'
# print get_access_token(appID, appsecret)
