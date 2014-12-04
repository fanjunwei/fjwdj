# coding=utf-8
# Date: 14/12/3
# Time: 12:20
# Email:fanjunwei003@163.com

from time import sleep
import thread
import time
import datetime
from FYAdmin.models import FYUserProfile, TaskLog
from util import fy_api
import logging

__author__ = u'范俊伟'

GET_ALL_LIMIT_TIME = '16:10:00'
run_get_all_limit_timestamp = 0

ORDER_TIME = '16:14:45'
order_timestamp = 0


def task():
    while True:
        try:
            getAllLimit()
            order()
        except:
            pass
        sleep(1)


def getAllLimit():
    global run_get_all_limit_timestamp
    log = logging.getLogger('task')
    log.info('getAllLimit check')
    now = datetime.datetime.now()
    start = datetime.datetime.strptime(GET_ALL_LIMIT_TIME, "%H:%M:%S")
    start = datetime.datetime(now.year, now.month, now.day, hour=start.hour, minute=start.minute,
                              second=start.second)
    start_timestamp = time.mktime(start.timetuple())
    now_timestamp = time.mktime(now.timetuple())

    if now_timestamp >= start_timestamp and run_get_all_limit_timestamp < start_timestamp:
        run_get_all_limit_timestamp = now_timestamp
        log.info('getAllLimit run')
        checked, all_goods = fy_api.all_googds()
        if checked:
            for user_pro in FYUserProfile.objects.all():
                for goods in all_goods:
                    goodsId = goods.get('goodsId')
                    fy_api.trading_limit(user_pro.get_fy_username(), user_pro.get_fy_password(), goodsId, reset=True)


def order():
    global order_timestamp
    log = logging.getLogger('task')
    log.info('order check')
    now = datetime.datetime.now()
    start = datetime.datetime.strptime(ORDER_TIME, "%H:%M:%S")
    start = datetime.datetime(now.year, now.month, now.day, hour=start.hour, minute=start.minute,
                              second=start.second)
    start_timestamp = time.mktime(start.timetuple())
    now_timestamp = time.mktime(now.timetuple())

    if now_timestamp >= start_timestamp and order_timestamp < start_timestamp:
        order_timestamp = now_timestamp
        log.info('order run')
        checked, all_googds = fy_api.all_googds()
        if checked:
            goods_sorter = []
            for item in all_googds:
                goodsId = item.get('goodsId')
                checked, googdsInfo = fy_api.get_money_info(goodsId, None)
                if checked:
                    goods_sorter.append(googdsInfo)
            goods_sorter.sort(fy_api.goods_CMP)

            for user_pro in FYUserProfile.objects.all():
                if user_pro.enable_task:
                    thread.start_new_thread(order_for_user, (user_pro, goods_sorter))


def order_for_user(user_pro, goods_sorter):
    ordered = False
    fy_username = user_pro.get_fy_username()
    fy_password = user_pro.get_fy_password()
    if user_pro.goodsId_list:
        enable_goodsId_list = user_pro.goodsId_list.split(',')
        mini_count = user_pro.mini_count
        for goods in goods_sorter:
            goodsId = goods.get('id')
            if goodsId in enable_goodsId_list:
                checked, limit = fy_api.trading_limit(fy_username, fy_password, goodsId)
                if checked:
                    if limit >= mini_count:
                        checked, errorMessage = fy_api.submit_order(fy_username, fy_password, goodsId, limit)
                        ordered = True
                        if checked:
                            TaskLog.objects.create(user=user_pro.user, state=1, goodsId=goodsId, count=limit)
                        else:
                            TaskLog.objects.create(user=user_pro.user, state=0, goodsId=goodsId, count=limit,
                                                   message=errorMessage)
                        break

                else:
                    TaskLog.objects.create(user=user_pro.user, state=0, goodsId=goodsId, message=limit)
        if not ordered:
            TaskLog.objects.create(user=user_pro.user, state=0, message=u'没有匹配的货物')


def startTask():
    global run_get_all_limit_timestamp, order_timestamp
    now = datetime.datetime.now()
    now_timestamp = time.mktime(now.timetuple())
    run_get_all_limit_timestamp = now_timestamp
    order_timestamp = now_timestamp
    thread.start_new_thread(task, ())


if __name__ == '__main__':
    getAllLimit()