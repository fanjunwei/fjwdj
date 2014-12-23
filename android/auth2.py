# coding=utf-8
# Date: 14/12/23
# Time: 12:43
# Email:fanjunwei003@163.com
import datetime
from android.models import Auth2, get_new_auth2_token

__author__ = u'范俊伟'

AUTH_TIMEOUT_DAYS = 30


def getAuth2Token(user, time=datetime.datetime.now()):
    try:
        auth2 = Auth2.objects.get(user=user)
        if auth2.password != user.password:
            auth2.token = get_new_auth2_token()
            auth2.create_time = time
            auth2.password = user.password
            auth2.save()
        if (time - auth2.create_time).days > AUTH_TIMEOUT_DAYS:
            auth2.token = get_new_auth2_token()
            auth2.create_time = time
            auth2.save()
    except Auth2.DoesNotExist:
        auth2 = Auth2()
        auth2.token = get_new_auth2_token()
        auth2.user = user
        auth2.password = user.password
        auth2.save()
    return auth2.token


def checkAuth2Token(token, time=datetime.datetime.now()):
    try:
        auth2 = Auth2.objects.get(token=token)
        if auth2.password != auth2.user.password:
            return None
        elif (time - auth2.create_time).days > AUTH_TIMEOUT_DAYS:
            return None
        return auth2.user
    except Auth2.DoesNotExist:
        pass
    return None


