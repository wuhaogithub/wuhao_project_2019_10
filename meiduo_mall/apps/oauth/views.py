from django.contrib.auth import login
from django.shortcuts import render, redirect

# Create your views here.
from django.urls import reverse

from apps.oauth.models import OAuthQQUser
from apps.oauth.utils import serect_openid, check_openid
from apps.users.models import User

"""

我们所做的这些都是为了一个 openid
openid是此网站上唯一对应用户身份的标识，网站可将此ID进行存储便于用户下次登录时辨识其身份

1. 申请appid和appkey,redirect_uri

        QQ_CLIENT_ID = '101518219'

        QQ_CLIENT_SECRET = '418d84ebdc7241efb79536886ae95224'

        QQ_REDIRECT_URI = 'http://www.meiduo.site:8000/oauth_callback'

2. 安置按钮
3. 按钮点击可以跳转到指定页面
    https://wiki.connect.qq.com/%E4%BD%BF%E7%94%A8authorization_code%E8%8E%B7%E5%8F%96access_token


    https://graph.qq.com/oauth2.0/authorize?response_type=code&client_id=101518219&redirect_uri=http://www.meiduo.site:8000/oauth_callback&state=xxxx

4. 跳转到指定页面,需要用户同意登陆,同意登陆之后,腾讯给我们一个code

5. 用code换取token
6. 用token换取openid
"""

"""
openid 和 用户id 一一对应
"""
from django.views import View
from django.http import HttpResponseBadRequest
class QQLoginView(View):

    def get(self,request):
        # 1.获取code
        code=request.GET.get('code')
        state=request.GET.get('state')
        if code is None:
            return HttpResponseBadRequest('没有code')
        #2.通过code换取token
        #2.1 导入 QQLoginTool
        from meiduo_mall import settings
        from QQLoginTool.QQtool import OAuthQQ
        #2.2 创建实例对象
        #client_id=None, client_secret=None, redirect_uri=None, state=None
        oauthqq=OAuthQQ(client_id=settings.QQ_CLIENT_ID,             #app_key
                        client_secret=settings.QQ_CLIENT_SECRET,
                        redirect_uri=settings.QQ_REDIRECT_URI,
                        state=state)
        # oauthqq.get_qq_url()
        #2.3 获取token
        token = oauthqq.get_access_token(code)
        #3.通过token 换取 openid
        openid=oauthqq.get_open_id(token)

        #'928A3695E768D69B6DBE6DB6385C4A44'

        #4. 根据openid进行数据的查询判断
        try:
            qquser=OAuthQQUser.objects.get(openid=openid)
        except OAuthQQUser.DoesNotExist:
            # 如果数据库中不存在了openid,说明用户没有绑定过了,我们应该让他绑定

            new_openid=serect_openid(openid)

            return render(request, 'oauth_callback.html',context={'openid':new_openid})
        else:
            # 如果数据库中已经存在了openid,说明用户已经绑定过了,我们应该让它登陆

            # 保持登陆的状态
            login(request,qquser.user)

            response = redirect(reverse('contents:index'))
            #设置cookie
            response.set_cookie('username',qquser.user.username,max_age=24*3600)

            return response


    def post(self,request):
        # ①接收数据
        mobile=request.POST.get('mobile')
        pwd=request.POST.get('pwd')
        sms_code=request.POST.get('sms_code')
        secret_openid=request.POST.get('openid')


        #添加解密
        openid=check_openid(secret_openid)
        if openid is None:
            return HttpResponseBadRequest('openid错误')
        # ②验证数据  openid   (此处课上省略)
        #     参数是否齐全
        #     手机号是否符合规则
        #     密码是否符合规则
        #     短信验证码是否一致

        # ③根据手机号进行用户信息的查询  user
        try:
            user=User.objects.get(mobile=mobile)
        except User.DoesNotExist:
            #     如果不存在,说明用户手机号没有注册过,我们就以这个手机号注册一个用户
            user=User.objects.create_user(username=mobile,
                                          password=pwd,
                                          mobile=mobile)


        else:
            #     如果存在,则需要验证密码
            if not user.check_password(pwd):
                return HttpResponseBadRequest('密码错误')


        # ④ 绑定openid 和 user
        OAuthQQUser.objects.create(user=user,openid=openid)
        # ⑤ 登陆(设置登陆状态,设置cookie,跳转到首页)
        login(request,user)

        response=redirect(reverse('contents:index'))

        response.set_cookie('username',user.username,max_age=24*3600)

        return response

"""
1.功能分析
    用户行为:
    前端行为:     把openid,用户手机号,密码,短信验证码 提交给后台
    后端行为:   实现用户和openid的绑定

2. 分析后端实现的大体步骤

    ①接收数据
    ②验证数据  openid
        参数是否齐全
        手机号是否符合规则
        密码是否符合规则
        短信验证码是否一致
    ③根据手机号进行用户信息的查询  user
        如果存在,则需要验证密码
        如果不存在,说明用户手机号没有注册过,我们就以这个手机号注册一个用户
    ④ 绑定openid 和 user
    ⑤ 登陆(设置登陆状态,设置cookie,跳转到首页)

3.确定请求方式和路由
    POST

"""








