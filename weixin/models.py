# coding=utf-8
# Date: 11-12-8
# Time: 下午10:28
import datetime

__author__ = u'王健'
from django.db import models

# Create your models here.

class WeiXinUser(models.Model):
    SEX_CHOICES = (
        (0, u'未知'),
        (1, u'男'),
        (2, u'女'),
    )
    user_id = models.IntegerField(null=True, blank=True, verbose_name=u'关联的账号ID')
    weixinid = models.CharField(max_length=50, db_index=True, verbose_name=u'微信openid')
    nickname = models.CharField(max_length=20, null=True, blank=True, verbose_name=u'昵称')
    sex = models.IntegerField(null=True, choices=SEX_CHOICES, blank=True, verbose_name=u'性别')
    language = models.CharField(max_length=10, verbose_name=u'语言')
    city = models.CharField(max_length=20, verbose_name=u'城市')
    province = models.CharField(max_length=20, verbose_name=u'省份')
    country = models.CharField(max_length=20, verbose_name=u'国家')
    headimgurl = models.URLField(null=True, blank=True, verbose_name=u'头像地址')
    current_scene_id = models.IntegerField(null=True, blank=True, verbose_name=u'二维码场景ID')
    is_active = models.BooleanField(default=True, verbose_name=u'是否关注')
    subscribe_time = models.IntegerField(null=True, blank=True, verbose_name=u'关注时间戳')
    unionid = models.CharField(max_length=50, null=True, blank=True)
    current_state = models.IntegerField(default=0)
    current_sub_state = models.IntegerField(default=0)
    state_parm = models.CharField(max_length=255)

    def __unicode__(self):
        if self.nickname:
            return self.nickname
        else:
            return u'ID:%s' % self.weixinid

    class Meta:
        verbose_name_plural = verbose_name = u'微信用户'


class WeiXinMessage(models.Model):
    weixinuser = models.ForeignKey(WeiXinUser, verbose_name=u'作者')
    messageid = models.CharField(max_length=50, unique=True, verbose_name=u'微信messageid')
    content = models.CharField(max_length=100, null=True, blank=True, db_index=True, verbose_name=u'微信内容')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name=u'发送信息的时间')

    def __unicode__(self):
        return u'%s' % (self.content,)

    class Meta:
        verbose_name_plural = verbose_name = '微信消息'
