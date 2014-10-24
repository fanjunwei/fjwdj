from time import sleep
from django.core.cache import cache
from fy.fy_query import getFyMoneySupply
import thread


def task():
    while True:
        try:
            cacheFyMoneySupply()
        except:
            pass
        sleep(1)


def cacheFyMoneySupply():
    cache.set('FyMoneySupply', getFyMoneySupply().decode('utf8'))


#thread.start_new_thread(task, ())