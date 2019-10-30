from django import http
from django.shortcuts import render

# Create your views here.
from django.views import View

from utils.response_code import RETCODE


class ImageCodeView(View):
    def get(self, request, uuid):
        # ① 获取前段传来的uuid
        # ② 生成图片验证码（二进制图片， 图片内容）
        from libs.captcha.captcha import captcha
        text, image = captcha.generate_captcha()
        # ③ 连接redis，保存uuid和图片验证码
        from django_redis import get_redis_connection
        redis_conn = get_redis_connection('code')
        redis_conn.setex('img_%s'%uuid, 120, text)
        # ④ 返回图片
        return http.HttpResponse(image, content_type='image/jpeg')
class SmsCodeView(View):
    # def get(self, request, mobile):
    #     # ① 接受数据
    #     image_code = request.GET.get('image_code')
    #     image_code_id = request.GET.get('image_code_id')
    #     # ② 验证数据
    #     if not all([image_code, image_code_id]):
    #         return http.HttpResponseBadRequest('参数不全')
    #     # ③ 对比用户输入的验证码与redis中的验证码书否一致
    #     # 3.1 连接redis
    #     from django_redis import get_redis_connection
    #     redis_conn = get_redis_connection('code')
    #     # 3.2 获取指定的验证码内容
    #     redis_text = redis_conn.get('image_%s'%image_code_id)
    #     # 3.3 判断验证码是否过期
    #     if redis_text is None:
    #         return http.HttpResponseBadRequest('图形验证码过期')
    #     # 3.4 对比用户输入的验证码与redis中的是否一致
    #     if redis_text.decode().lower() != image_code.lower():
    #         return http.HttpResponseBadRequest('图形验证码错误')
    #     # 3.5 判断短信是否发的太频繁
    #     send_flag = redis_conn.get('send_flag_%s'% mobile)
    #     if send_flag:
    #         return http.HttpResponse({'errmsg':'短信发的太频繁了', 'code':'4001'})
    #
    #     # ④ 产生短信验证码
    #     from random import randint
    #     sms_code = '06%d' %randint(0, 999999)
    #     # ⑤ 保存短息验证码
    #     from apps.verifications.constants import SMS_CODE_EXPIRES_SECONDS
    #     redis_conn.setex('sms_code_%s'%mobile, SMS_CODE_EXPIRES_SECONDS, sms_code)
    #     # 做一个标记
    #     redis_conn.setex('send_flag_%s'% mobile)
    #     # ⑥ 发送短信验证码
    #     from libs.yuntongxun.sms import CCP
    #     CCP.send_template_sms(mobile, [send_flag,5], 1)
    #     # ⑦ 返回响应
    #     return http.HttpResponse({'msg':'ok', 'code':RETCODE.OK})






    def get(self, request, mobile):
        # ① 获取数据
        # mobile
        # 用户的输入的图形验证码:  image_code
        # uuid:              image_code_id
        image_code = request.GET.get('image_code')
        image_code_id = request.GET.get('image_code_id')

        # ② 验证数据
        if not all([image_code, image_code_id]):
            return http.HttpResponseBadRequest('参数不全')
        # 省略 用户验证码长度验证
        # 省略 image_code_id 的正则验证

        # ③ 比对用户输入的验证码和redis的验证码是否一致
        # 3.1 连接redis
        from django_redis import get_redis_connection
        redis_conn = get_redis_connection('code')
        # 3.2 获取指定的数据
        redis_text = redis_conn.get('img_%s' % image_code_id)
        # 3.3 判断验证码是否过期

        if redis_text is None:
            return http.HttpResponseBadRequest('图片验证码以过期')
        # 3.4 比对
        if redis_text.decode().lower() != image_code.lower():
            return http.HttpResponseBadRequest('图片验证码不一致')

        send_flag = redis_conn.get('send_flag_%s' % mobile)
        if send_flag:
            return http.JsonResponse({'errmsg': '短信发送太频繁', 'code': '4001'})

        # ④ 生成一个随机短信验证码
        # 6位数值
        from random import randint
        sms_code = '%06d' % randint(0, 999999)

        # ⑤ 保存短信验证码
        # redis_conn.setex('sms_%s'%mobile,300,sms_code)
        from apps.verifications.constants import SMS_CODE_EXPIRES_SECONDS
        redis_conn.setex('sms_%s' % mobile, SMS_CODE_EXPIRES_SECONDS, sms_code)

        # 添加一个标记
        redis_conn.setex('send_flag_%s' % mobile, 60, 1)
        # ⑥ 发送短信
        # 免费开发测试使用的模板ID为1，形式为：
        # 【云通讯】您使用的是云通讯短信模板，您的验证码是{1}，请于{2}分钟内正确输入。
        # 其中{1}和{2}为短信模板的参数
        from libs.yuntongxun.sms import CCP
        CCP().send_template_sms(mobile,[sms_code,5],1)

        # from celery_tasks.sms.tasks import send_sms_code
        # # 任务的参数,平移到delay中
        # # delay 中 添加函数的参数
        # send_sms_code.delay(mobile, sms_code)

        # ⑦ 返回相应
        return http.JsonResponse({'msg': 'ok', 'code': RETCODE.OK})

