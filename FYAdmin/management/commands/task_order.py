# coding=utf-8
# Date: 14/11/13
# Time: 14:59
# Email:fanjunwei003@163.com
import json
from django.core.management import BaseCommand
from util.task import orderRun

__author__ = u'范俊伟'


class Command(BaseCommand):
    def handle(self, *args, **options):
        print 'orderRun'
        orderRun(wait=True)



