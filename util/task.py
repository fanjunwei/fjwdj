# coding=utf-8
# Date: 14/12/3
# Time: 12:20
# Email:fanjunwei003@163.com
import os
import threading

from time import sleep
import thread
import time
import datetime
from FYAdmin.models import FYUserProfile, TaskLog
from util import fy_api
import logging
import fcntl

__author__ = u'范俊伟'

GET_ALL_LIMIT_TIME = '16:10:00'
run_get_all_limit_timestamp = 0

ORDER_TIME = '16:14:45'
order_timestamp = 0

countLock = threading.RLock()
thread_run_count = 0


def addCount():
    global thread_run_count
    countLock.acquire()
    thread_run_count += 1
    countLock.release()


def subCount():
    global thread_run_count
    countLock.acquire()
    thread_run_count -= 1
    countLock.release()


def task():
    BASE_DIR = os.path.dirname(__file__)
    lock_file_path = os.path.join(BASE_DIR, 'task.lock')
    fp = open(lock_file_path, 'w')
    fcntl.flock(fp, fcntl.LOCK_EX)
    log = logging.getLogger('task')
    log.info('==============================startTask=======================================')
    while True:
        try:
            getAllLimitCheckTime()
            orderCheckTime()
        except:
            pass
        sleep(1)
    fcntl.flock(fp, fcntl.LOCK_UN)
    fp.close()


def getAllLimitCheckTime():
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
        getAllLimitRun()


def getAllLimitRun():
    log = logging.getLogger('task')
    log.info('getAllLimit run')
    checked, all_goods = fy_api.all_googds()
    if checked:
        for user_pro in FYUserProfile.objects.all():
            for goods in all_goods:
                goodsId = goods.get('goodsId')
                fy_api.trading_limit(user_pro.get_fy_username(), user_pro.get_fy_password(), goodsId)


def orderCheckTime():
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
        orderRun()


def orderRun(wait=False):
    log = logging.getLogger('task')
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

        for user_pro in FYUserProfile.objects.filter(enable_task=True):
            addCount()
            thread.start_new_thread(order_for_user, (user_pro, goods_sorter))
    if wait:
        while thread_run_count > 0:
            time.sleep(1)


def order_for_user(user_pro, goods_sorter):
    try:
        ordered = False
        fy_username = user_pro.get_fy_username()
        fy_password = user_pro.get_fy_password()
        if user_pro.goodsId_list:
            enable_goodsId_list = user_pro.goodsId_list.split(',')
            mini_count = user_pro.mini_count
            for goods in goods_sorter:
                goodsId = goods.get('id')
                if goodsId in enable_goodsId_list:
                    checked, limit = fy_api.trading_limit(fy_username, fy_password, goodsId, for_cache=True)
                    if checked:
                        if limit >= mini_count:
                            checked, errorMessage = fy_api.submit_order(fy_username, fy_password, goodsId, limit)
                            ordered = True
                            if checked:
                                TaskLog.objects.create(user=user_pro.user, state=1, goodsId=goodsId, count=limit,
                                                       message='配比:%s%%,价格:%s' % (
                                                       goods.get('ratio_format'), goods.get('recommendation')))
                            else:
                                TaskLog.objects.create(user=user_pro.user, state=0, goodsId=goodsId, count=limit,
                                                       message=errorMessage)
                            break

                    else:
                        TaskLog.objects.create(user=user_pro.user, state=0, goodsId=goodsId, message=limit)
            if not ordered:
                TaskLog.objects.create(user=user_pro.user, state=0, message=u'没有匹配的货物')
    finally:
        subCount()


def startTask():
    global run_get_all_limit_timestamp, order_timestamp
    return
    now = datetime.datetime.now()
    now_timestamp = time.mktime(now.timetuple())
    run_get_all_limit_timestamp = now_timestamp
    order_timestamp = now_timestamp
    thread.start_new_thread(task, ())
