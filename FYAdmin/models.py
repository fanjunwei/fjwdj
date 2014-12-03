# coding=utf-8
from django.contrib.auth.models import User
from django.db import models

# Create your models here.
from django.core.signing import Signer
from util.rc4 import RC4


class FYUserProfile(models.Model):
    key = 'sdfcs32vader32cvxae3v>sdcSD#2dvcs'
    user = models.OneToOneField(User)
    fy_username = models.CharField(unique=True, max_length=255, verbose_name=u'泛亚账号')
    fy_password = models.CharField(max_length=255, verbose_name=u'泛亚密码')
    enable_task = models.BooleanField(default=False, verbose_name=u'启用自动资金受托')
    goodsId_list = models.CharField(max_length=255, null=True, blank=True)
    mini_count = models.IntegerField(verbose_name=u'最少购买量', default=3)

    def get_fy_username(self):
        rc4 = RC4(key=self.key)
        return rc4.decry(self.fy_username)

    def set_fy_username(self, value):
        rc4 = RC4(key=self.key)
        self.fy_username = rc4.crypt(value)

    def get_fy_password(self):
        rc4 = RC4(key=self.key)
        return rc4.decry(self.fy_password)

    def set_fy_password(self, value):
        rc4 = RC4(key=self.key)
        self.fy_password = rc4.crypt(value)


class TaskLog(models.Model):
    user = models.ForeignKey(User)
    time = models.DateTimeField(auto_now_add=True)
    state = models.IntegerField()
    goodsId = models.CharField(max_length=10, null=True)
    count = models.IntegerField(null=True)
    message = models.CharField(max_length=255, null=True)