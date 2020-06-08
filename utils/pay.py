import string
import time
from datetime import datetime, timedelta
from random import choice

import base64
import hashlib
from Crypto.Cipher import AES

from weixin import WeixinPay as BaseWeixinPay

from django.conf import settings

WEIXIN_PAY = settings.WEIXIN_PAY


def gen_out_trade_no(pay_type=1):
    """
    生成内部订单号
    格式：
    {pay_type}{20190119161237}{xxxxyyyy}
    :param pay_type: 1: 支付宝， 2：微信, 3:退款
    :return:
    """
    # create_time = datetime.now().strftime('%Y%m%d%H%M%S')
    create_time = str(int(time.time()))
    random_str = ''.join([choice(string.digits) for _ in range(4)])
    return '{pay_type}{create_time}{random_str}'.format(pay_type=pay_type, create_time=create_time, random_str=random_str)

def get_order_time_expire(minutes=30):
    now = datetime.now()
    time_expire = now + timedelta(minutes=minutes)
    return time_expire, time_expire.strftime('%Y%m%d%H%M%S')



key = WEIXIN_PAY.APICLIENT_KEY_PATH
cert = WEIXIN_PAY.APICLIENT_CERT_PATH

class WeixinPay(BaseWeixinPay):

    def get_mch_key_md5(self):
        """获取商户key的md5值
        """
        return hashlib.md5(self.mch_key.encode("utf-8")).hexdigest().lower()


    def parse_refund_result(self, xml):
        """获取退款回调数据
        （1）对加密串A做base64解码，得到加密串B
        （2）对商户key做md5，得到32位小写key* ( key设置路径：微信商户平台(pay.weixin.qq.com)-->账户设置-->API安全-->密钥设置 )
        （3）用key*对加密串B做AES-256-ECB解密（PKCS7Padding）
        """

        BS = AES.block_size
        pad = lambda s: s + (BS - len(s) % BS) * chr(BS - len(s) % BS)
        unpad = lambda s: s[0:-ord(s[-1])]
        
        data = self.to_dict(xml)
        req_info = data['req_info'].encode()
        req_info = base64.decodebytes(req_info)
        hash = hashlib.md5()
        hash.update(self.mch_key.encode())
        key = hash.hexdigest().encode()

        cipher = AES.new(key, AES.MODE_ECB)
        decrypt_bytes = cipher.decrypt(req_info)
        decrypt_str = decrypt_bytes.decode()
        decrypt_str = unpad(decrypt_str)
        
        data = self.to_dict(decrypt_str)
        
        return data



weixinpay_vip_buy = WeixinPay(
    app_id=WEIXIN_PAY.WEIXIN_APP_ID,
    mch_id=WEIXIN_PAY.WEIXIN_MCH_ID,
    mch_key=WEIXIN_PAY.WEIXIN_MCH_KEY,
    notify_url=WEIXIN_PAY.WEIXIN_NOTIFY_URL_VIP_BUY
)

weixinpay_vip_buy_refund = WeixinPay(
    app_id=WEIXIN_PAY.WEIXIN_APP_ID,
    mch_id=WEIXIN_PAY.WEIXIN_MCH_ID,
    mch_key=WEIXIN_PAY.WEIXIN_MCH_KEY,
    notify_url=WEIXIN_PAY.WEIXIN_NOTIFY_URL_VIP_BUY_REFUND,
    key=key,
    cert=cert,
)


weixinpay_foregift = WeixinPay(
    app_id=WEIXIN_PAY.WEIXIN_APP_ID,
    mch_id=WEIXIN_PAY.WEIXIN_MCH_ID,
    mch_key=WEIXIN_PAY.WEIXIN_MCH_KEY,
    notify_url=WEIXIN_PAY.WEIXIN_NOTIFY_URL_GOREGIFT
)


weixinpay_foregift_refund = WeixinPay(
    app_id=WEIXIN_PAY.WEIXIN_APP_ID,
    mch_id=WEIXIN_PAY.WEIXIN_MCH_ID,
    mch_key=WEIXIN_PAY.WEIXIN_MCH_KEY,
    notify_url=WEIXIN_PAY.WEIXIN_NOTIFY_URL_GOREGIFT_REFUND,
    key=key,
    cert=cert,
)

