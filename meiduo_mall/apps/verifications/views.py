from django.http import HttpResponse
from django.http import JsonResponse
from django.shortcuts import render

# Create your views here.
from django.views import View

from apps.verifications.constants import SMS_CODE_EXPIRES_SECONDS
from libs.yuntongxun.sms import CCP
from utils.response_code import RETCODE

"""
图片验证码的业务逻辑

1. 功能分析
    用户行为:  用户刷新注册页面/点击图片验证码 应该生成一个图片验证码
    前端行为:   前端生成一个uuid, 然后发送给后端
    后端行为:   生成图片验证码

2. 后端的大体步骤
        ① 获取前端提交的uuid
        ② 生成图片验证码 (图片二进制,图片中的内容)
        ③ 将uuid和图片中的内容保存到redis中
        ④ 返回相应

3. 确定请求方式和路由
    GET     /image_code/?uuid=xxxxx

    GET     /image_code/uuid/   v
"""

class ImageCodeView(View):

    def get(self,request,uuid):
        # ① 获取前端提交的uuid
        # ② 生成图片验证码 (图片二进制,图片中的内容)
        from libs.captcha.captcha import captcha
        # text 就是生成的图片验证码的内容,例如 abcd
        # image 就是 图片二进制
        text,image=captcha.generate_captcha()
        # ③ 将uuid和图片中的内容保存到redis中
        #3.1 连接redis
        from django_redis import get_redis_connection
        redis_conn = get_redis_connection('code')
        #setex key seconds value
        # redis_conn.setex(key,seconds,value)
        # redis_conn.setex(uuid,120,text)

        # key 想加一个前缀
        redis_conn.setex('img_%s'%uuid,120,text)

        # ④ 返回图片
        # return HttpResponse(image)
        # content_type
        # MIME类型
        # 大类/小类
        # application/json
        # text/html
        # image/jpeg
        return HttpResponse(image,content_type='image/jpeg')

"""
容联云发送短信
1.注册(不需要认证)
2.点击快速接入(短信)
3.免费接入指南 https://doc.yuntongxun.com/p/5a531a353b8496dd00dcdfe2
    ①免费开发测试需要使用"控制台首页"中，开发者主账户相关信息，如主账号、应用ID等。

    ②免费开发测试使用的模板ID为1，形式为：【云通讯】您使用的是云通讯短信模板，您的验证码是{1}，请于{2}分钟内正确输入。

        其中{1}和{2}为短信模板的参数。

    !!!!!要添加测试账号!!!!! ③免费开发测试需要在"控制台—管理—号码管理—测试号码"绑定测试号码。
4. 点击查看Demo  https://doc.yuntongxun.com/p/5a533e0c3b8496dd00dce08c

5. 将 我们给大家的 容联云 压缩包 放到libs中
    打开 sms.py文件

6. 先修改三个地方
        # 说明：主账号，登陆云通讯网站后，可在"控制台-应用"中看到开发者主账号ACCOUNT SID
        _accountSid = '8aaf0708568d4143015697b0f4960888'

        # 说明：主账号Token，登陆云通讯网站后，可在控制台-应用中看到开发者主账号AUTH TOKEN
        _accountToken = '57c6c3ef3cef47e680519a734f6812f8'

        # 请使用管理控制台首页的APPID或自己创建应用的APPID
        _appId = '8aaf0708568d4143015697b0f56e088f'

    再修改最后的 main中的代码

"""



###################实现短信发送功能的视图###############################
"""

1.功能分析
    用户行为:   用户输入手机号,验证码之后,点击按钮获取短信验证码
    前端行为:   要收集用户的手机号,验证码 以及当时生成的uuid, 发送axios请求给后端
    后端行为:   给这个手机号发送短信

2.后端的大体步骤
    ① 获取数据
    ② 验证数据
    ③ 比对用户输入的验证码和redis的验证码是否一致
    ④ 生成一个随机短信验证码
    ⑤ 保存短信验证码
    ⑥ 发送短信
    ⑦ 返回相应

3.请求方式和路由
    GET
        提取URL的特定部分，如/weather/beijing/2018，可以在服务器端的路由中用正则表达式截取；
        code/uuid/mobile/user_text/

        查询字符串（query string)，形如key1=value1&key2=value2；
        code/?uuid=xxxx&mobile=xxxx&image_code=xxxx

        image_codes/mobile/?image_code=xxxx&image_code_id=xxxx


    POST image_codes/   body

"""
from django.http import HttpResponseBadRequest
class SmsCodeView(View):

    def get(self,request,mobile):
        # ① 获取数据
        #mobile
        #用户的输入的验证码:  image_code
        #uuid:              image_code_id
        image_code=request.GET.get('image_code')
        image_code_id=request.GET.get('image_code_id')

        # ② 验证数据
        if not all([image_code,image_code_id]):
            return HttpResponseBadRequest('参数不全')
        # 省略 用户验证码长度验证
        # 省略 image_code_id 的正则验证

        # ③ 比对用户输入的验证码和redis的验证码是否一致
        # 3.1 连接redis
        from django_redis import get_redis_connection
        redis_conn = get_redis_connection('code')
        # 3.2 获取指定的数据
        redis_text=redis_conn.get('img_%s'%image_code_id)

        if redis_text is None:
            return HttpResponseBadRequest('图片验证码以过期')
        # 3.3 比对
        if redis_text.decode().lower() != image_code.lower():
            return HttpResponseBadRequest('图片验证码不一致')

        send_flag=redis_conn.get('send_flag_%s'%mobile)
        if send_flag:
            return JsonResponse({'errmsg':'短信发送太频繁','code':'4001'})

        # ④ 生成一个随机短信验证码
        # 6位数值
        from random import randint
        sms_code='%06d'%randint(0,999999)

        # ⑤ 保存短信验证码
        # redis_conn.setex('sms_%s'%mobile,300,sms_code)
        redis_conn.setex('sms_%s'%mobile,SMS_CODE_EXPIRES_SECONDS,sms_code)

        #添加一个标记
        redis_conn.setex('send_flag_%s'%mobile,60,1)
        # ⑥ 发送短信
        #免费开发测试使用的模板ID为1，形式为：
        # 【云通讯】您使用的是云通讯短信模板，您的验证码是{1}，请于{2}分钟内正确输入。
        # 其中{1}和{2}为短信模板的参数
        # CCP().send_template_sms(mobile,[sms_code,5],1)

        from celery_tasks.sms.tasks import send_sms_code
        # 任务的参数,平移到delay中
        # delay 中 添加函数的参数
        send_sms_code.delay(mobile,sms_code)

        # ⑦ 返回相应
        return JsonResponse({'msg':'ok','code':RETCODE.OK})
