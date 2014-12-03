# coding=utf-8
from django.contrib.auth.models import User
from django.db import models

# Create your models here.
from django.core.signing import Signer


class FYUserProfile(models.Model):
    user = models.OneToOneField(User)
    fy_username = models.CharField(unique=True, max_length=255, verbose_name=u'泛亚账号')
    fy_password = models.CharField(max_length=255, verbose_name=u'泛亚密码')
    enable_task = models.BooleanField(default=False, verbose_name=u'启用自动资金受托')
    goodsId_list = models.CharField(max_length=255, null=True, blank=True)
    mini_count = models.IntegerField(verbose_name=u'最少购买量', default=3)

    def get_fy_username(self):
        return self.fy_username

    def set_fy_username(self, value):
        self.fy_username = value

    def get_fy_password(self):
        return self.fy_password

    def set_fy_password(self, value):
        self.fy_password = value


class TaskLog(models.Model):
    user = models.ForeignKey(User)
    time = models.DateTimeField(auto_now_add=True)
    state = models.IntegerField()
    goodsId = models.CharField(max_length=10, null=True)
    count = models.IntegerField(null=True)
    message = models.CharField(max_length=255, null=True)