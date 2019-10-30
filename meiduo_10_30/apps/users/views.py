import re

from django import http
from django.shortcuts import render, redirect

# Create your views here.
from django.urls import reverse
from django.views import View

from apps.users.models import User


class RegisterView(View):
    def get(self, request):

        return render(request, 'register.html')
    def post(self, requset):
        # ① 接收数据
        username = requset.POST.get('username')
        password = requset.POST.get('password')
        password2 = requset.POST.get('password2')
        mobile = requset.POST.get('mobile')
        allow = requset.POST.get('allow')
        # ② 验证数据
        # 1.判断接收的参数是否完整
        if not all([username, password,
                    password2, mobile]):
            return http.HttpResponseBadRequest('参数不全')
        # 2.判断用户名格式是否正确
        if not re.match(r'[a-zA-Z0-9]{5,20}', username):
            return http.HttpResponseBadRequest('用户名格式不对')

        # 3.判断用户密码输入格式是否正确
        if not re.match(r'[a-zA-Z0-9]{8,20}', password):
            return http.HttpResponseBadRequest('密码格式不正确')
        # 4.核对两次输入的密码是否一致
        if not password ==password2:
            return http.HttpResponseBadRequest('两次输入的密码不一致')
        # 5.判断手机号格式是否正确
        if not re.match(r'^1[3-9]\d{9}$', mobile):
            return http.HttpResponseBadRequest('手机号码根式不正确')
        if allow != 'on':
            return http.HttpResponseBadRequest('请勾选用户协议')
        # ③ 保存数据
        user = User.objects.create_user(username=username,
                                        password=password,
                                        mobile=mobile)
        # 通过django的认证系统中login存储用户信息在session中
        from django.contrib.auth import login
        login(requset, user)

        # ④ 返回响应
        return redirect(reverse('contents:index'))
class RegisterUsernameCountView(View):
    def get(self, request, username):
        count = User.objects.filter(username=username).count()
        return http.JsonResponse({'count':count})