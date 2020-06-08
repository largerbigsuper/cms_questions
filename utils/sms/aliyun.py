import uuid
import random
import json

from django.core.cache import cache
from django.conf import settings
from aliyunsdkcore.client import AcsClient
from aliyunsdkcore.request import CommonRequest

from utils.exceptions import GenericAPIException

ALIYUN_SMS = settings.ALIYUN_SMS

class SMSClient:

    def __init__(self, access_key_id, access_secret_key, sign_name, temple_code):
        self.client = AcsClient(access_key_id, access_secret_key, 'default')
        self.temple_code = temple_code
        self.sign_name = sign_name
    
    @staticmethod
    def gen_code():
        return ''.join(random.sample(list(map(str, range(10))), 4))

    def send(self, phone_number, **kwargs):
        """发送单个验证码"""

        request = CommonRequest()
        request.set_accept_format('json')
        request.set_domain('dysmsapi.aliyuncs.com')
        request.set_method('POST')
        request.set_protocol_type('https') # https | http
        request.set_version('2017-05-25')
        request.set_action_name('SendSms')

        request.add_query_param('TemplateCode', self.temple_code)
        request.add_query_param('SignName', self.sign_name)
        request.add_query_param('PhoneNumbers', phone_number)
        if 'code' not in kwargs and len(kwargs) == 0:
            kwargs['code'] = self.gen_code()
        request.add_query_param('TemplateParam', json.dumps(kwargs))
        request.add_body_params('OutId', uuid.uuid1())
        response = self.client.do_action(request)
        # b'{"Message":"OK","RequestId":"97FDD87D-5B50-4BFA-BF9C-CA24768A5FE0","BizId":"419112860178747080^0","Code":"OK"}'
        resp = json.loads(response.decode('utf-8'))
        if resp['Message'] == 'OK':
            if 'code' in kwargs:
                timeout = kwargs.get('timeout', 5 * 60)
                cache.set(phone_number, kwargs['code'], timeout)
        else:
            raise GenericAPIException(resp['Message'])
        return resp


client_login = SMSClient(ALIYUN_SMS.ACCESS_KEY_ID, ALIYUN_SMS.ACCESS_KEY_SECRET, ALIYUN_SMS.SIGN_NAME, ALIYUN_SMS.TPL_LOGIN.TEMPLATE_CODE)
client_order = SMSClient(ALIYUN_SMS.ACCESS_KEY_ID, ALIYUN_SMS.ACCESS_KEY_SECRET, ALIYUN_SMS.SIGN_NAME, ALIYUN_SMS.TPL_ORDER.TEMPLATE_CODE)
client_vip = SMSClient(ALIYUN_SMS.ACCESS_KEY_ID, ALIYUN_SMS.ACCESS_KEY_SECRET, ALIYUN_SMS.SIGN_NAME, ALIYUN_SMS.TPL_VIP.TEMPLATE_CODE)


if __name__ == "__main__":
    print(client_login.send('18258185399', code='18258185399'))
    print(client_order.send('18258185399', title='无敌爆炒牛蛙', status='成功', orderId='orderid'))
    print(client_vip.send('18258185399'))
