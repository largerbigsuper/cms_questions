# -*- coding: utf-8 -*-
from django.contrib import admin

from .models import Course, Chapter, Question


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('id', 'code', 'name')
    search_fields = ('name',)


@admin.register(Chapter)
class ChapterAdmin(admin.ModelAdmin):
    list_display = ('id', 'course', 'name', 'order_num')
    list_filter = ('course',)
    search_fields = ('name',)


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'course',
        'chapter',
        'title',
        'choices',
        'answers',
        'qtype',
        'order_num',
    )
    list_filter = ('course', 'chapter')
