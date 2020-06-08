import random
import string

from django.db import models, IntegrityError
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import UserManager as AuthUserManager

from utils.modelmanager import ModelManager

class UserManager(AuthUserManager, ModelManager):
    
    Default_Password = '888888'

    def add(self, username, password, **extra_fields):
        # extra_fields.setdefault('username', username)
        return self.create_user(username=username, email=None, password=password, **extra_fields)

    def _create_miniprogram_username(self, avatar, name, openid=None, mini_openid=None, unionid=None):
        username = 'cms_' + ''.join([random.choice(string.ascii_lowercase) for _ in range(8)])
        password = self.Default_Password
        name = name
        user = self.add(username, password, mini_openid=mini_openid, openid=openid, unionid=unionid, avatar=avatar, name=name)
        return user
    
    def get_user_by_miniprogram(self, avatar, name, openid=None, mini_openid=None, unionid=None):
        """通过小程序获取User
        前期有小程序登陆用户，但是没有unionid， 需要同步小程序应用与微信网页应用
        """
        user = None
        if unionid:
            user = self.filter(unionid=unionid).first()
            if user:
                return user

        if mini_openid:
            user = self.filter(mini_openid=mini_openid).first()
        if openid:
            user = self.filter(openid=openid).first()
            
        if user:
            return user
        else:
            user = self._create_miniprogram_username(avatar, name, openid, mini_openid, unionid)
            if user:
                return user
            else:
                raise IntegrityError('注册用户失败')

    def get_user_by_invite_code(self, invite_code):
        """通过邀请码获取用户
        """
        return self.filter(invite_code=invite_code).first()

    def update_exam_count(self, user_id, count):

        self.increase('exam_count', count)

    def get_user_phone(self, phone):
        return self.filter(phone=phone).first()

class User(AbstractUser):
    
    avatar = models.ImageField(max_length=200, blank=True, default='', verbose_name='头像')
    mini_openid = models.CharField(max_length=64, unique=True, null=True, blank=True, verbose_name='小程序账号')
    openid = models.CharField(max_length=64, unique=True, null=True, blank=True, verbose_name='微信账号')
    unionid = models.CharField(max_length=64, unique=True, null=True, blank=True, verbose_name='微信unionid')
    name = models.CharField(max_length=30, blank=True, verbose_name='真实姓名')

    objects = UserManager()

    class Meta:
        db_table = 'cms_users'
        verbose_name = verbose_name_plural = '用户信息'

mm_User = User.objects

