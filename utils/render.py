import logging

from rest_framework.renderers import JSONRenderer

logger = logging.getLogger('django.request')

class FormatedJSONRenderer(JSONRenderer):

    def render(self, data, accepted_media_type=None, renderer_context=None):
        response = renderer_context['response']
        status_code_str = str(response.status_code)
        if status_code_str.startswith('2'):
            response.status_code = 200
            if data:
                if 'msg' not in data:
                    data = {
                        'msg': 'OK',
                        'data': data
                    }
            else:
                data = {
                    'msg': 'OK',
                    'data': data
                }
        else:
            logger.error(response.data)
        return super().render(data, accepted_media_type, renderer_context)
