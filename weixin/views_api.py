# coding=utf-8
# Date:2014/9/24
# Email:wangjian2254@gmail.com
import datetime
from django.contrib.auth.models import User

from django.core.cache import cache
from FYAdmin.models import TaskLog
from fy.fy_query import getFyMoneySupply
from util import fy_api
from wechat_sdk import WechatBasic
from django.http import HttpResponse
from weixin.models import WeiXinUser, WeiXinMessage
from django.contrib.auth import authenticate, get_user_model

TOKEN = "pibgrj1409810714"


def handleRequest(request):
    signature = request.GET.get("signature", '')
    timestamp = request.GET.get("timestamp", '')
    nonce = request.GET.get("nonce", '')
    wechat = WechatBasic(token=TOKEN)
    if request.method == 'GET':
        echoStr = request.GET.get("echostr", '')
        if wechat.check_signature(signature, timestamp, nonce):
            response = HttpResponse(echoStr, content_type="text/plain")
        else:
            response = HttpResponse('', content_type="text/plain")
        return response
    elif request.method == 'POST':
        if wechat.check_signature(signature, timestamp, nonce):
            response = HttpResponse(responseMsg(request, wechat), content_type="application/xml")
        else:
            response = HttpResponse('', content_type="application/xml")

        return response
    else:
        return HttpResponse('', content_type="application/xml")


def getHelperText(weixinUser, user):
    helperText = ''
    if user != None:
        helperText += u'欢迎:' + user.first_name + u'\n'

    helperText += u'''平台测试中
QQ：81300697
回复1：获取泛亚有色金属最新资金配比情况
回复2：绑定管理账号'''
    if user != None:
        helperText += u'\n'
        helperText += u'''回复3：获取账户资金
回复4：获取近一周自动购买记录'''
    return helperText


def message_cash_summary(user):
    res = ''
    if hasattr(user, 'fyuserprofile'):
        checked, cash_summary = fy_api.cash_summary(user.fyuserprofile.get_fy_username(),
                                                    user.fyuserprofile.get_fy_password())
        if checked:
            res += u'资金权益:%s\n' % fy_api.format_money(cash_summary.get('cashValue'))
            res += u'货物权益:%s\n' % fy_api.format_money(cash_summary.get('goodsValue'))
        else:
            res = cash_summary
    else:
        res = u'未设置泛亚账户'

    return res


def format_time(time):
    return time.strftime('%Y-%m-%d %H:%M:%S')


def message_task_log(user):
    res = u''

    fyuserprofile = user.fyuserprofile
    start_time = datetime.datetime.now() - datetime.timedelta(days=7)
    logs = TaskLog.objects.filter(time__gt=start_time, user=user)
    if logs.count() > 0:
        res = u'自动购买记录\n'
        for log in logs:
            if log.state == 1:
                res += u'%s,成功购买%d手%s\n' % (format_time(log.time), log.count, log.goodsId)
            else:
                res += u'%s,失败,%s\n' % (format_time(log.time), log.message)
    else:
        res = u'无自动购买记录'

    return res


def responseMsg(request, wechat):
    res = ''
    wechat.parse_data(request.body)
    message = wechat.get_message()
    weixinUser, user = checkWeixinuser(message.source)

    if weixinUser.current_state == 0:
        if message.type == 'text':
            try:
                weixinmsg = WeiXinMessage.objects.get(messageid=message.id, weixinuser=weixinUser)
            except WeiXinMessage.DoesNotExist:
                weixinmsg = WeiXinMessage()
                weixinmsg.messageid = message.id
                weixinmsg.weixinuser = weixinUser
            weixinmsg.content = message.content
            weixinmsg.save()
            if message.content == '1':
                try:
                    res = wechat.response_text(getFyMoneySupply().decode('utf8'))
                except Exception, e:
                    print str(e)
            elif message.content == '2':
                weixinUser.current_state = 1
                weixinUser.current_sub_state = 0
                res = wechat.response_text(u'请输入管理账号')
            elif message.content == '3' and user != None:
                res = wechat.response_text(message_cash_summary(user))
            elif message.content == '4' and user != None:
                res = wechat.response_text(message_task_log(user))
    elif weixinUser.current_state == 1:
        if message.type == 'text':
            if weixinUser.current_sub_state == 0:
                weixinUser.state_parm = message.content
                weixinUser.current_sub_state = 1
                res = wechat.response_text(u'请输入密码')
            elif weixinUser.current_sub_state == 1:
                username = weixinUser.state_parm
                password = message.content
                user = authenticate(username=username,
                                    password=password)
                weixinUser.current_state = 0
                weixinUser.current_sub_state = 0
                if not user or not user.is_active:
                    res = wechat.response_text(u'用户或密码错误')
                else:
                    weixinUser.user_id = user.pk
                    res = wechat.response_text(u'绑定成功\n' + getHelperText(weixinUser, user))

    weixinUser.save()
    if not res:
        res = wechat.response_text(getHelperText(weixinUser, user))
    return res


def checkWeixinuser(weixinid):
    try:
        weixinUser = WeiXinUser.objects.get(weixinid=weixinid)
    except WeiXinUser.DoesNotExist:
        weixinUser = WeiXinUser()
        weixinUser.weixinid = weixinid
        weixinUser.save()
    user = None
    if weixinUser.user_id != None:
        try:
            user = User.objects.get(pk=weixinUser.user_id)
        except User.DoesNotExist:
            pass
    return weixinUser, user

