#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# import_excel.py
# @Author : frankie ()
# @Date   : 5/8/2020, 5:32:46 PM

import json
import os
import traceback
import pathlib

import requests
from django.db import transaction
# from openpyxl import load_workbook
import xlrd

from apps.questions.models import mm_Course, Chapter, mm_Chapter, Question, mm_Question
from server.settings.base import BASE_DIR
import string


def run():
    try:
        with transaction.atomic():
            excel_file_dir = pathlib.Path(BASE_DIR).parent.joinpath('scripts/excel/course_01')
            for fpath in get_excel_files(excel_file_dir): 
                print(fpath)
                parse_excel('纳税', fpath)

    except :
        traceback.print_exc()


def get_excel_files(dir_name):
    print(dir_name)
    files = pathlib.Path(dir_name).glob('*.xls')
    print(files)
    return files



def parse_excel(course_name, excel_file_path):
    # 下载文件

    wb = xlrd.open_workbook(excel_file_path)
    sheet = wb.sheets()[0]
    print('=======')

    # 处理课程
    course, _ = mm_Course.get_or_create(name=course_name)
    
    # 处理章节
    p = pathlib.Path(excel_file_path)
    fname = p.name.split('.')[0]
    chapter_name = fname[:-2]
    qtype_name = fname[-2:]
    # FIXME 题目类别
    qtype = 0
    if qtype_name == '单选':
        qtype = 0
    elif qtype_name == '多选':
        qtype = 1
    elif qtype_name == '判断':
        qtype = 2

    print(chapter_name, qtype)
    chapter, _ = mm_Chapter.get_or_create(course=course, name=chapter_name)

    # 处理题目
    problem_list = []
    for index in range(sheet.nrows):
        print(sheet.row(index))
        if index <= 3:
            continue
        row = sheet.row(index)
        # FIXME 题目
        title = row[0].value
        # FIXME 选项
        choices_list = row[2: -2]
        print(choices_list)
        choices = process_choices(qtype, choices_list)
        # FIXME 答案
        answers_value = row[-1].value
        answers = process_answers(qtype, answers_value)

        if not all([title, choices, answers]):
            continue

        p = Question(
            course=course, 
            chapter=chapter, 
            title=title, 
            choices=choices, 
            answers=answers,
            qtype=qtype)
        problem_list.append(p)
        print(p.__dict__)

    Question.objects.bulk_create(problem_list, 50)

    print('====ok====')

def process_choices(qtype, choices_list):
    """处理字符串
    **A.正确**B.错误
    """
    data = {}
    if qtype == mm_Question.QUESTION_TYPE_PANDUAN:
        data = {
            '1': '对',
            '2': '错',
        }
    else:
        for index, cell in enumerate(choices_list, 1):
            print(cell.value)
            if cell.value:
                data[str(index)] = cell.value

    return data


def process_answers(qtype, answers_value):
    """处理答案
    A ｜ AB    
    """
    if qtype == mm_Question.QUESTION_TYPE_PANDUAN:
        if answers_value == '对':
            answers_str ='1'
        else:
            answers_str = '2'
    else:
        answers_str = str(int(answers_value))
    return list(answers_str)
