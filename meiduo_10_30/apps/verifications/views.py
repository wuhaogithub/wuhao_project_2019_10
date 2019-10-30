from django import http
from django.shortcuts import render

# Create your views here.
from django.views import View


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

