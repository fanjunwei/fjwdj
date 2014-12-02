# coding=utf-8
from django.contrib.auth.models import User
from django.db import models

# Create your models here.
from django.core.signing import Signer


class FYUserProfile(models.Model):
    user = models.OneToOneField(User)
    fy_username = models.CharField(unique=True, max_length=255, verbose_name=u'泛亚账号')
    fy_password = models.CharField(max_length=255, verbose_name=u'泛亚密码')

    def get_fy_username(self):
        return self.fy_username

    def set_fy_username(self, value):
        self.fy_username = value

    def get_fy_password(self):
        return self.fy_password

    def set_fy_password(self, value):
        self.fy_password = value