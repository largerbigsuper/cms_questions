
from django import forms

from django_admin_json_editor.admin import JSONEditorWidget

from .models import Question

QUESTION_CHOICES_SCHEMA = {
    'type': 'object',
    'title': '答案选项',
    'properties': {
        'A': {
            'title': 'A选项',
            'type': 'string',
            'format': 'textarea',
        },
        'B': {
            'title': 'B选项',
            'type': 'string',
            'format': 'textarea',
        },
        'C': {
            'title': 'C选项',
            'type': 'string',
            'format': 'textarea',
        },
        'D': {
            'title': 'D选项',
            'type': 'string',
            'format': 'textarea',
        },
    },
}

QUESTION_ANSWERS_SCHEMA = {
  "type": "array",
  "uniqueItems": True,
  "items": {
    "type": "string",
    "enum": ["A", "B", "C", "D"]
  }
}

class QuestionAdminForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = '__all__'
        widgets = {
            'choices': JSONEditorWidget(QUESTION_CHOICES_SCHEMA, collapsed=False),
            'answers': JSONEditorWidget(QUESTION_ANSWERS_SCHEMA, collapsed=False),
        }