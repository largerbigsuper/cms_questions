import logging

import requests
from rest_framework import viewsets, mixins, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.conf import settings
from django.contrib.auth import authenticate


from ..models import mm_User
from .serializers import (
    UserSerializer, 
    UserProfileSerializer, 
    MiniprogramLoginSerializer, 
    LoginSerializer, 
    GetCodeSerializer, 
    BindPhoneSerializer
)

from utils.wechat.WXBizDataCrypt import WXBizDataCrypt
from utils.common import process_login, process_logout
from utils.serializers import NoneParamsSerializer

logger = logging.getLogger('api_weixin')

class UserViewSet(viewsets.ReadOnlyModelViewSet):
    
    queryset = mm_User.all()
    serializer_class = UserSerializer

    @action(detail=False, methods=['post'], serializer_class=MiniprogramLoginSerializer, permission_classes=[], authentication_classes=[])
    def login_miniprogram(self, request):
        """小程序登录
        1. csrf校验去除
        """
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        code = serializer.validated_data['code']
        avatar = serializer.validated_data['avatar']
        name = serializer.validated_data['name']
        encryptedData = serializer.validated_data['encryptedData']
        iv = serializer.validated_data['iv']
        logger.info('code: {}'.format(code))
        logger.info('encryptedData: {}'.format(encryptedData))
        logger.info('iv: {}'.format(iv))
        
        wx_res = requests.get(settings.MINI_PROGRAM_LOGIN_URL + code)
        ret_json = wx_res.json()
        logger.info('code: {}, name: {}'.format(code, name))
        logger.info('wechat resp: {}'.format(ret_json))
        if 'openid' not in ret_json:
            return Response(data=ret_json, status=status.HTTP_400_BAD_REQUEST)
        
        # 处理unionid
        session_key = ret_json['session_key']
        pc = WXBizDataCrypt(settings.MINI_PROGRAM_APP_ID, session_key)
        try:
            decrypt_dict = pc.decrypt(encryptedData, iv)
        except Exception as e:
            return Response(status=status.HTTP_401_UNAUTHORIZED) 
        logger.info('decrypt_dict : {}'.format(decrypt_dict))
        # unionid不一定存在
        unionid = decrypt_dict.get('unionId')
        mini_openid = ret_json['openid']
        user = mm_User.get_user_by_miniprogram(avatar, name,  mini_openid=mini_openid, unionid=unionid)
        process_login(request, user)
        serializer_user = UserProfileSerializer(user)
        data = serializer_user.data

        return Response(data=data)

    @action(detail=False, methods=['post'], serializer_class=LoginSerializer, permission_classes=[], authentication_classes=[])
    def login(self, request):
        """登录"""

        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        username = serializer.validated_data['username']
        password = serializer.validated_data.get('password')
        code = serializer.validated_data.get('code')
        code_login = False
        if code:
            code_login = True
            _code = mm_User.cache.get(username)
            if code != _code:
                data = {
                    'detail': '验证码不存在或错误'
                }
                return Response(data=data, status=status.HTTP_400_BAD_REQUEST)
        user = mm_User.filter(username=username).first()
        if user:
            if not code_login:
                user = authenticate(request, username=username, password=password)
                if not user:
                    user = authenticate(request, username=username, password=password)
            if user:
                process_login(request, user)
                serailizer = UserProfileSerializer(user)
                data = serailizer.data
                return Response(data=data)
            else:
                return Response(data={'detail': '账号或密码错误'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(data={'detail': '账号不存在'}, status=status.HTTP_400_BAD_REQUEST)


    @action(detail=False, methods=['get'])
    def logout(self, request):
        """退登"""
        
        process_logout(request)
        return Response()

    @action(detail=False, methods=['get', 'post'], permission_classes=[IsAuthenticated], serializer_class=UserProfileSerializer)
    def profile(self, request):
        """个人信息获取／修改"""

        if request.method == 'GET':
            serializer = self.serializer_class(request.user)
            return Response(data=serializer.data)
        else:
            serializer = self.serializer_class(
                request.user, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(data=serializer.data)
            else:
                return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    @action(detail=False, methods=['post'], permission_classes=[], authentication_classes=[], serializer_class=GetCodeSerializer)
    def get_code(self, request):
        """发送验证码"""
        
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        phone = serializer.validated_data['phone']
        return Response()

    @action(detail=False, methods=['post'], serializer_class=BindPhoneSerializer)
    def bind_phone(self, request):
        """绑定手机号
        """
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        phone = serializer.validated_data['phone']
        code = serializer.validated_data['code']
        name = serializer.validated_data['name']
        id_card = serializer.validated_data['id_card']
        _code = mm_User.cache.get(phone)
        if not code or _code != code:
            data = {
                'detail': '验证码不存在或错误'
            }
            return Response(data=data, status=status.HTTP_400_BAD_REQUEST)
        user = mm_User.get_user_phone(phone)
        if user and user != request.user:
            data = {
                'detail': '手机号已被绑定，请联系管理员。'
            }
            return Response(data=data, status=status.HTTP_400_BAD_REQUEST)
        else:
            user = request.user
        user.phone = phone
        user.name = name
        user.id_card = id_card
        user.save()
        return Response()
