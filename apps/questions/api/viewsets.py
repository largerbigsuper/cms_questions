from rest_framework import viewsets

from apps.questions.models import mm_Question
from apps.questions.api.serializers import QuestionSerializer
from apps.questions.api.filters import ChapterFilter, QuestionFilter

class QuestionViewSet(viewsets.ReadOnlyModelViewSet):

    serializer_class = QuestionSerializer
    filter_class = QuestionFilter
    queryset = mm_Question.select_related('course', 'chapter').all()

