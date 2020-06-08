#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2018/12/1 下午11:31
# @Author  : Frankie
# @Email   : zaihuazhao@163.com
# @File    : exceptions.py
from rest_framework import status
from rest_framework.exceptions import APIException

class GenericAPIException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = '参数错误'
    default_code = 'error'

