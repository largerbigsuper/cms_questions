from rest_framework import serializers

from apps.questions.models import Chapter, Course, Question


class CourseSerializer(serializers.ModelSerializer):

    class Meta:
        model = Course
        fields = ['id', 'name', 'code']


class ChapterSerializer(serializers.ModelSerializer):

    course = CourseSerializer()

    class Meta:
        model = Chapter
        fields = ['id', 'course', 'name']

class InlineChapterSerializer(serializers.ModelSerializer):

    class Meta:
        model = Chapter
        fields = ['id', 'name']


class QuestionSerializer(serializers.ModelSerializer):

    course = CourseSerializer()
    chapter = InlineChapterSerializer()
    choices = serializers.DictField()
    answers = serializers.ListField()

    class Meta:
        model = Question
        fields = ['id', 'course', 'chapter', 'title', 'choices', 'answers', 'qtype',]

