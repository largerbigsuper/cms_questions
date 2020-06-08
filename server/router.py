from rest_framework import routers

from apps.users.api import viewsets as user_viewsets
from apps.questions.api import viewsets as questions_viewsets


router = routers.DefaultRouter()
router.register('user', user_viewsets.UserViewSet, 'api-user')
router.register('questions', questions_viewsets.QuestionViewSet, 'api-questions')
