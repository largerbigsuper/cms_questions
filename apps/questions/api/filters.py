from django_filters import rest_framework as filters

from ..models import Chapter, Question

class ChapterFilter(filters.FilterSet):

    class Meta:
        model = Chapter
        fields = {
            'course': ['exact'],
        }


class QuestionFilter(filters.FilterSet):

    class Meta:
        model = Question
        fields = {
            'course': ['exact'],
            'chapter': ['exact'],
            'title': ['icontains'],
        }
