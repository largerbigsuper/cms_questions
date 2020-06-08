import random
import datetime

from django.db import models
from django.conf import settings
from django_extensions.db.fields.json import JSONField

from utils.modelmanager import ModelManager
from utils.datetime import strdatime

class CourseManager(ModelManager):
    pass

class Course(models.Model):

    code = models.CharField(max_length=20, unique=True, verbose_name='项目编号')
    name = models.CharField(max_length=100, verbose_name='项目名称')

    objects = CourseManager()

    class Meta:
        db_table = 'cms_course'
        ordering = ['id']
        verbose_name = '培训课程'
        verbose_name_plural = '培训课程'

    def __str__(self):
        return self.name

mm_Course = Course.objects

class ChapterManager(ModelManager):
    pass

class Chapter(models.Model):

    course = models.ForeignKey(Course, on_delete=models.CASCADE, verbose_name='所属项目')
    name = models.CharField(max_length=100, verbose_name='知识模块')
    order_num = models.IntegerField(default=10000, verbose_name='排序值[越小越靠前]')

    objects = ChapterManager()

    class Meta:
        db_table = 'cms_chapter'
        ordering = ['course', 'order_num', 'id']
        verbose_name = '知识模块'
        verbose_name_plural = '知识模块'

    def __str__(self):
        return '项目:%s, 名称: %s' % (self.course.name, self.name)

mm_Chapter = Chapter.objects


class QuestionManager(ModelManager):

    QUESTION_TYPE_DANXUAN = 0
    QUESTION_TYPE_DUOXUAN = 1
    QUESTION_TYPE_PANDUAN = 2

    QUESTION_TYPES = (
        (QUESTION_TYPE_DANXUAN, '单选题'),
        (QUESTION_TYPE_DUOXUAN, '多选题'),
        (QUESTION_TYPE_PANDUAN, '判断题'),
    )

    cache_key = 'q_{pk}'

    def get_random_questions(self, course_id, qtype, count):
        all_id_list = self.filter(course_id=course_id, qtype=qtype).values_list('id', flat=True)
        all_id_list = list(all_id_list)
        if count > len(all_id_list):
            return all_id_list
        else:
            return random.sample(all_id_list, count)

    def get_question(self, pk, use_cache=True):
        if use_cache is True:
            data = self.cache.get(self.cache_key.format(pk=pk))
            if not data:
                q = self.filter(pk=pk).first()
                data = q.dict if q else {}
                self.cache.set(self.cache_key.format(pk=pk), data)
                return data
            else:
                return data
        else:
            q = self.filter(pk=pk).first()
            return q.dict if q else {}

    def _get_answer(self, user_answer_item, correct_answer_item, qtype_score_dict):
        user_answer = user_answer_item['answers']
        correct_answer = correct_answer_item['answers']
        qtype = correct_answer_item['qtype']
        score = 0
        is_correct = 0
        if len(user_answer) == len(correct_answer) and sorted(user_answer) == sorted(correct_answer):
            is_correct = 1
            score = qtype_score_dict[qtype]

        user_answer_item['score'] = score
        user_answer_item['is_correct'] = is_correct
        return user_answer_item
            
    def _get_answers(self, answers, qtype_score_dict):
        """处理用户提交的答案
        [
            {
                "id": 3011,
                "answers": [
                    "A"
                ]
            }
        ]
        """
        answers_dict = {x['id']: x for x in answers}
        questions = self.filter(pk__in=answers_dict.keys()).values('id', 'answers', 'qtype')
        correct_answers_dict = {x['id']: x for x in questions}
        result = []
        for answer_item in answers:
            correct_answer_item = correct_answers_dict[answer_item['id']]
            item = self._get_answer(answer_item, correct_answer_item, qtype_score_dict)
            result.append(item)
        total_score = sum([x['score'] for x in result])
        return result, total_score


class Question(models.Model):
    # {
    #     "course": 0,
    #     "chapter": 0,
    #     "title": "2、根据以下现象选择正确的观点？(单选题)",
    #     "answers": [
    #         "A"
    #     ],
    #     "images": "yhpicture/nj_cz_t2_tp97.jpg",
    #     "choices": {
    #         "A": "车入车库需手动开门",
    #         "B": "车辆检修需停稳",
    #         "C": "检修时，叉齿需降至地面",
    #         "D": "检修需关闭发动机"
    #     },
    #     "order_num": "1",
    #     "q_type": 0,
    #     "level": 1
    # }

    course = models.ForeignKey(Course, on_delete=models.CASCADE, verbose_name='所属课程')
    chapter = models.ForeignKey(Chapter, on_delete=models.CASCADE, verbose_name='所属章节')
    title = models.CharField(max_length=600, blank=True, verbose_name='标题')
    choices = JSONField(default='{}', verbose_name='选择内容')
    answers = JSONField(default='[]', verbose_name='答案')
    qtype = models.SmallIntegerField(
        choices=QuestionManager.QUESTION_TYPES,
        default=QuestionManager.QUESTION_TYPE_DANXUAN,
        blank=True,
        verbose_name='题目类型')
    order_num = models.IntegerField(default=100000, verbose_name='排序值[越小越靠前]')

    objects = QuestionManager()

    class Meta:
        db_table = 'cms_question'
        ordering = ['course', 'order_num', 'id']
        verbose_name = '题目'
        verbose_name_plural = '题目'

    def __str__(self):
        return self.title


    @property
    def dict(self):
        data = {
            'id': self.id,
            'course_id': self.course_id,
            'chapter_id': self.chapter_id,
            'title': self.title,
            'choices': self.choices,
            'answers': self.answers,
            'images': self.images.url if self.images else '',
            'qtype': self.qtype,
            'order_num': self.order_num,
        }
        return data


mm_Question = Question.objects

