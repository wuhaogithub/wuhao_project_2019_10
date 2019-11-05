import json
import re

from django import http
from django.contrib.auth import login
from django.shortcuts import render, redirect

# Create your views here.
from django.urls import reverse
from django.views import View
from django_redis import get_redis_connection

from apps.goods.models import SKU
from apps.users.models import User, Address
from apps.users.utils import generic_active_email_url, check_active_token
from utils.response_code import RETCODE

"""
注册页面的展示:
    1. 创建子应用 (django-admin startapp users)
    2. 注册
    3. 路由匹配
"""
"""
1.功能分析
    用户行为:  输入完成 用户名,密码,确认密码,手机号之后,会点击注册按钮
    前端行为:   通过form表单收集 相关信息(用户名,密码,确认密码,手机号)
    后端行为:   实现注册
2.后台功能大体步骤
    ① 接收数据
    ② 验证数据 (我们不相信前端提交的任何数据)
    ③ 保存数据
    ④ 返回相应
3.根据功能来分析请求方式和路由
    POST  register
"""
from django.http.response import HttpResponseBadRequest,HttpResponse, JsonResponse


class RegisterView(View):

    def get(self,request):

        return render(request,'register.html')


    def post(self,request):
        # ① 接收数据
        username=request.POST.get('username')
        password=request.POST.get('password')
        password2=request.POST.get('password2')
        mobile=request.POST.get('mobile')
        # ② 验证数据 (我们不相信前端提交的任何数据)
        #  2.1 四个参数必须都有值
        if not all([username,password,password2,mobile]):
            #说明 有变量为空值
            return HttpResponseBadRequest('参数不全')

        #  2.2  判断用户名 是否符合规则
        import re
        if not re.match(r'[a-zA-Z0-9]{5,20}',username):
            return HttpResponseBadRequest('用户名不满足条件')
                #判断用户名是否重复
        # 2.3 密码是否符合规则
        if not re.match(r'[a-zA-Z0-9]{8,20}',password):
            return HttpResponseBadRequest('密码不符合规则')
        # 2.4 确认密码和密码一致
        if password2 != password:
            return HttpResponseBadRequest('密码不一致')
        # 2.5 判断手机号 是否符合规则
        if not re.match(r'^1[3-9]\d{9}$',mobile):
            return HttpResponseBadRequest('手机号错误')
                #判断手机号是否重复

        # ③ 保存数据
        user = User.objects.create_user(username=username,
                                 password=password,
                                 mobile=mobile)


        # 设置session
        # request.session['username']=user.username
        # request.session['id']=user.id

        # admin 在登陆的时候 可以帮助记录登陆状态
        from django.contrib.auth import login
        # request
        # user:用户对象
        login(request,user)

        # ④ 返回相应
        return redirect(reverse('contents:index'))
        return HttpResponse("ok")
        """
        注册成功之后,跳转到了登陆页面
        注册成功之后,直接登陆,跳转到了首页  v
        """

"""
1.功能分析
    用户行为: 用户输入用户名之后,会失去焦点
    前端行为: 获取用户名,发送给后端 ajax
    后端行为: 判断用户名是否重复

2. 分析后端实现的大体步骤
        ① 获取前端提交的数据
        ② 查询数量
            数量为1: 重复
            数量为0: 不重复

        后端获取到数据之后对比


3.确定请求方式和路由

    提取URL的特定部分，如/weather/beijing/2018，可以在服务器端的路由中用正则表达式截取；
    查询字符串（query string)，形如key1=value1&key2=value2；
    请求体（body）中发送的数据，比如表单数据、json、xml；

    GET     /usernames/xxxx/




"""
class RegisterUsernameCountView(View):

    def get(self,request,username):
        # ① 获取前端提交的数据
        # ② 查询数量
        count=User.objects.filter(username=username).count()
        #     数量为1: 重复
        #     数量为0: 不重复
        return JsonResponse({'count':count})


"""
1.功能分析
    用户行为:   输入用户名,密码,记住密码(有可能点,有可能没有点)
    前端行为:  前端基本验证之后,把  用户名,密码,记住密码 提交给后台
    后端行为:  登陆验证

2. 分析后端实现的大体步骤
        ① 接收数据
        ② 验证数据 (参数是否齐全,是否符合规则)
        ③ 再判断用户名和密码是否匹配一致
        ④ 状态保持
        ⑤ 记住密码
        ⑥ 返回相应

3.确定请求方式和路由
    POST  login
"""

class LoginView(View):

    def get(self,request):

        return render(request,'login.html')

    # 1.相应状态码可以帮助我们分析问题
    # 2.面试会问

    # 405 Method Not Allowed  没有实现对应的请求方法
    def post(self,request):
        # ① 接收数据
        username=request.POST.get('username')
        password=request.POST.get('pwd')
        remembered = request.POST.get('remembered')
        # ② 验证数据 (参数是否齐全,是否符合规则)
        if not all([username,password]):
            return HttpResponseBadRequest('参数不全')
        # 用户名,密码是否符合正则,此处省略
        # ③ 再判断用户名和密码是否匹配一致
        from django.contrib.auth import authenticate
        # 认证成功返回User对象
        # 认证失败返回None
        from django.contrib.auth.backends import ModelBackend
        user = authenticate(username=username,password=password)
        if user is None:
            return HttpResponseBadRequest('用户名或密码错误')
        # ④ 状态保持
        login(request,user)
        # ⑤ 记住登陆
        if remembered == 'on':
            #记住登陆 2周
            request.session.set_expiry(None)
        else:
            #不记住登陆
            request.session.set_expiry(0)

        # ⑥ 返回相应


        response = redirect(reverse('contents:index'))

        #设置cookie
        response.set_cookie('username',user.username,max_age=3600*24*14)

        #合并购物车
        from apps.carts.utils import merge_cookie_to_redis
        response=merge_cookie_to_redis(request,user,response)

        return response

"""
1.功能分析
    用户行为:  点击退出按钮
    前端行为:  前端发送请求
    后端行为:  实现退出功能

2. 分析后端实现的大体步骤
        ① 清除状态保持的信息
        ② 跳转到指定页面

3.确定请求方式和路由
    GET logout
"""

class LogoutView(View):

    def get(self,request):

        # request.session.flush()

        from django.contrib.auth import logout
        logout(request)

        #删除cookie中的username

        response =  redirect(reverse('contents:index'))

        # response.set_cookie('username',None,max_age=0)
        response.delete_cookie('username')

        return response

"""
登陆用户才可以访问个人中心

1.页面必须是登陆用户才可以访问
2.可以用 已知学的知识来实现判断
3.使用系统的mixin
4.修改了mixin的默认跳转url
"""
from django.contrib.auth.mixins import LoginRequiredMixin

class UserCenterInfoView(LoginRequiredMixin,View):

    def get(self,request):
        # request.user 请求中 有用户的信息
        # is_authenticated 判断用户是否为登陆用户
        # 登陆用户为True
        # 未登陆用户为False
        # if request.user.is_authenticated:
        #     return render(request,'user_center_info.html')
        # else:
        #     return redirect(reverse('users:login'))

        #1.获取/组织登陆用户的信息
        context = {
            'username':request.user.username,
            'mobile':request.user.mobile,
            'email':request.user.email,
            'email_active':request.user.email_active,
        }
        #2.传递给模板,让模板进行渲染
        return render(request,'user_center_info.html',context=context)

"""
1.功能分析
    用户行为:       用户输入邮箱之后,点击保存
    前端行为:       邮箱提交给后端
    后端行为:       保存邮箱,给这个邮箱发送一个激活连接,


2. 分析后端实现的大体步骤
        !!!必须是登陆用户才可以访问!!!
        ① 接收
        ② 验证
        ③ 更新数据
        ④ 给邮箱发送激活连接
        ⑤ 返回相应

3.确定请求方式和路由

    put/post/get

    GET     --获取数据
    POST    --新增数据
    PUT     --更新数据
    DELETE  --删除数据

    put   put和post类似,请求的数据在body中
    发送axios 请求,传递是 JSON数据


"""

class EmailView(LoginRequiredMixin,View):

    def put(self,request):
        # !!!必须是登陆用户才可以访问!!!
        # ① 接收  axios
        body=request.body
        body_str=body.decode()
        data=json.loads(body_str)
        # ② 验证
        email=data.get('email')
        if not re.match(r'^[a-z0-9][\w\.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$',email):
            return JsonResponse({'code':RETCODE.PARAMERR,'errmsg':'邮箱不符合规则'})
        # ③ 更新数据
        request.user.email=email
        request.user.save()
        # ④ 给邮箱发送激活连接
        from django.core.mail import send_mail

        # #subject, message, from_email, recipient_list,
        # #subject        主题
        # subject='美多商场激活邮件'
        # #message,       内容
        # message=''
        # #from_email,  谁发的
        # from_email = '欢乐玩家<qi_rui_hua@163.com>'
        # #recipient_list,  收件人列表
        # recipient_list = ['qi_rui_hua@163.com']
        #
        # """
        # 1.思考了一下,我们给用户发送邮件的目的是什么
        #     目的:用户点击这个连接,让他跳转到指定页面,同时修改这个用户的邮件状态
        # 2. 步骤:
        #     ① 有指定的页面
        #     ② 获取用户
        # 3.分析 如何获取用户信息
        #     分析: 用户点击哪个连接就是在发送GET请求.我们就应该在GET请求中,传递用户信息
        #     emailsactive/?user_id=1
        # 4. 用户的信息太明显了,我们需要对用户信息 加密
        # 5. 加密抽取
        # """
        #
        # # 对用户信息进行加密
        # active_url=generic_active_email_url(request.user.id,email)
        # # 用户点击这个连接,让他跳转到指定页面,同时修改这个用户的邮件状态
        # html_mesage="<a href='%s'>戳我有惊喜,恭喜你,注册成功,请点击激活</a>"%active_url
        #
        # send_mail(subject=subject,
        #           message=message,
        #           from_email=from_email,
        #           recipient_list=recipient_list,
        #           html_message=html_mesage)

        from celery_tasks.email.tasks import send_active_email
        send_active_email.delay(request.user.id,email)


        # ⑤ 返回相应
        return JsonResponse({'code':RETCODE.OK,'errmsg':'ok'})


"""
1.功能分析

    用户行为:       用户点击激活连接
    前端行为:       前端应该发送什么数据,来确定是激活某个用户
    后端行为:       激活用户邮箱状态

2. 分析后端实现的大体步骤
        ①获取token信息
        ②token信息解密
        ③根据用户信息进行数据的更新
        ④跳转到指定页面

3.确定请求方式和路由
    GET     emailsactive/
"""

from django.db import DataError

class EmailActiveView(View):

    def get(self,request):
        # ①获取token信息
        token=request.GET.get('token')
        if token is None:
            return HttpResponseBadRequest('缺少参数')
        # ②token信息解密
        data=check_active_token(token)
        if data is None:
            return HttpResponseBadRequest('验证失败')
        # ③根据用户信息进行数据的更新
        id=data.get('id')
        email=data.get('email')
        # 我们需要查询指定用户 ,request.user 可能没有登陆用户信息
        # User.objects.filter().filter()
        try:
            user=User.objects.get(id=id,email=email)
        except User.DoesNotExist:
            return HttpResponseBadRequest('验证失败')
        user.email_active=True
        user.save()
        # ④跳转到指定页面
        return redirect(reverse('users:center'))

        # return HttpResponse('激活成功')
        # return render(request)


class UserCenterSiteView(View):

    def get(self,request):

        return render(request,'user_center_site.html')



"""

新增地址

1.功能分析
    用户行为:       填写完成地址信息
    前端行为:       收集相关信息
    后端行为:       保存入库

2. 分析后端实现的大体步骤
        ① 接收数据
        ② 验证数据
        ③ 数据入库
        ④ 返回相应

3.确定请求方式和路由
    POST        /addresses/create/
"""
class CreateAddressView(LoginRequiredMixin, View):
    """新增地址"""

    def post(self, request):
        """实现新增地址逻辑"""
        # 判断是否超过地址上限：最多20个
        # Address.objects.filter(user=request.user).count()
        count = request.user.addresses.count()
        if count >= 20:
            return http.JsonResponse({'code': RETCODE.THROTTLINGERR, 'errmsg': '超过地址数量上限'})

        # 接收参数
        json_dict = json.loads(request.body.decode())
        receiver = json_dict.get('receiver')
        province_id = json_dict.get('province_id')
        city_id = json_dict.get('city_id')
        district_id = json_dict.get('district_id')
        place = json_dict.get('place')
        mobile = json_dict.get('mobile')
        tel = json_dict.get('tel')
        email = json_dict.get('email')

        # 校验参数
        if not all([receiver, province_id, city_id, district_id, place, mobile]):
            return http.HttpResponseBadRequest('缺少必传参数')
        if not re.match(r'^1[3-9]\d{9}$', mobile):
            return http.HttpResponseBadRequest('参数mobile有误')
        if tel:
            if not re.match(r'^(0[0-9]{2,3}-)?([2-9][0-9]{6,7})+(-[0-9]{1,4})?$', tel):
                return http.HttpResponseBadRequest('参数tel有误')
        if email:
            if not re.match(r'^[a-z0-9][\w\.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
                return http.HttpResponseBadRequest('参数email有误')

        # 保存地址信息
        try:
            address = Address.objects.create(
                user=request.user,
                title = receiver,
                receiver = receiver,
                province_id = province_id,
                city_id = city_id,
                district_id = district_id,
                place = place,
                mobile = mobile,
                tel = tel,
                email = email
            )

            # 设置默认地址
            if not request.user.default_address:
                request.user.default_address = address
                request.user.save()
        except Exception as e:

            return http.JsonResponse({'code': RETCODE.DBERR, 'errmsg': '新增地址失败'})

        # 新增地址成功，将新增的地址响应给前端实现局部刷新
        address_dict = {
            "id": address.id,
            "title": address.title,
            "receiver": address.receiver,
            "province": address.province.name,
            "city": address.city.name,
            "district": address.district.name,
            "place": address.place,
            "mobile": address.mobile,
            "tel": address.tel,
            "email": address.email
        }

        # 响应保存结果
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': '新增地址成功', 'address':address_dict})

"""

删除地址

1.功能分析
    用户行为:       点击想要删除的某一个地址
    前端行为:       传递一个删除id
    后端行为:       实现删除

2. 分析后端实现的大体步骤
        ① 接收参数
        ② 验证参数
        ③ 实现删除
        ④ 返回相应

3.确定请求方式和路由
    DELETE  addresses/(?P<address_id>\d+)/
"""

"""

修改地址

1.功能分析
    用户行为:     点击编辑某一个
    前端行为:     收集更新的数据
    后端行为:       实现更新

2. 分析后端实现的大体步骤

            ① 接收数据
            ② 验证数据
            ③ 查询并更新数据
            ④ 返回相应

3.确定请求方式和路由
    PUT     addresses/(?P<address_id>\d+)/

"""
class UpdateDestroyAddressView(LoginRequiredMixin, View):
    """修改和删除地址"""

    def put(self, request, address_id):
        """修改地址"""
        # 接收参数
        json_dict = json.loads(request.body.decode())
        receiver = json_dict.get('receiver')
        province_id = json_dict.get('province_id')
        city_id = json_dict.get('city_id')
        district_id = json_dict.get('district_id')
        place = json_dict.get('place')
        mobile = json_dict.get('mobile')
        tel = json_dict.get('tel')
        email = json_dict.get('email')

        # 校验参数
        if not all([receiver, province_id, city_id, district_id, place, mobile]):
            return http.HttpResponseBadRequest('缺少必传参数')
        if not re.match(r'^1[3-9]\d{9}$', mobile):
            return http.HttpResponseBadRequest('参数mobile有误')
        if tel:
            if not re.match(r'^(0[0-9]{2,3}-)?([2-9][0-9]{6,7})+(-[0-9]{1,4})?$', tel):
                return http.HttpResponseBadRequest('参数tel有误')
        if email:
            if not re.match(r'^[a-z0-9][\w\.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
                return http.HttpResponseBadRequest('参数email有误')

        # 判断地址是否存在,并更新地址信息
        try:
            Address.objects.filter(id=address_id).update(
                user = request.user,
                title = receiver,
                receiver = receiver,
                province_id = province_id,
                city_id = city_id,
                district_id = district_id,
                place = place,
                mobile = mobile,
                tel = tel,
                email = email
            )
        except Exception as e:

            return http.JsonResponse({'code': RETCODE.DBERR, 'errmsg': '更新地址失败'})

        # 构造响应数据
        address = Address.objects.get(id=address_id)
        address_dict = {
            "id": address.id,
            "title": address.title,
            "receiver": address.receiver,
            "province": address.province.name,
            "city": address.city.name,
            "district": address.district.name,
            "place": address.place,
            "mobile": address.mobile,
            "tel": address.tel,
            "email": address.email
        }

        # 响应更新地址结果
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': '更新地址成功', 'address': address_dict})

    def delete(self, request, address_id):
        """删除地址"""
        try:
            # 查询要删除的地址
            address = Address.objects.get(id=address_id)

            # 将地址逻辑删除设置为True
            address.is_deleted = True
            address.save()
        except Exception as e:

            return http.JsonResponse({'code': RETCODE.DBERR, 'errmsg': '删除地址失败'})

        # 响应删除地址结果
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': '删除地址成功'})
"""

查询地址

1.功能分析
    用户行为:   刷新页面
    前端行为:   传递用户信息 (session 是依赖于cookie,cookie信息肯定是传递给后端)
    后端行为:   根据用户信息,查询指定用户的地址

2. 分析后端实现的大体步骤
        ① 获取登陆用户信息
        ② 根据用户信息进行查询
        ③ 将对象列表转换为字典列表
        ④ 返回相应

3.确定请求方式和路由
    GET     addresses/
"""
class AddressView(LoginRequiredMixin, View):
    """用户收货地址"""

    def get(self, request):
        """提供收货地址界面"""
        # 获取用户地址列表
        login_user = request.user
        addresses = Address.objects.filter(user=login_user, is_deleted=False)

        address_dict_list = []
        for address in addresses:
            address_dict = {
                "id": address.id,
                "title": address.title,
                "receiver": address.receiver,
                "province": address.province.name,
                "province_id":address.province_id,
                "city": address.city.name,
                "city_id":address.city_id,
                "district": address.district.name,
                "district_id":address.district_id,
                "place": address.place,
                "mobile": address.mobile,
                "tel": address.tel,
                "email": address.email
            }
            address_dict_list.append(address_dict)

        context = {
            'default_address_id': login_user.default_address_id,
            'addresses': address_dict_list,
        }

        return render(request, 'user_center_site.html', context)


"""
1.功能分析
    用户行为:  登陆用户点击商品访问商品详情
    前端行为:   获取商品id,发送给后端
    后端行为:   记录用户的浏览记录

    更多的掌握redis数据
    所以,我们把数据保存在redis中
    string: key:value
    hash:   key:
                field:value
                field:value
                field:value
    list:   key: [value,value,value]
    set:    key: {value4,value2,value3}
    zset:   key: {value1,value2,value3}


2. 分析后端实现的大体步骤(记录有顺序(列表,有序集合),记录不能重复,记录就展示5条)
    ①有用户信息(必须是登陆用户)
    ②获取商品id
    ③判断商品id(查询)
    ④数据保存
    4.1 先去重
    4.2 再添加
    4.3 确保有5条记录

    ⑤ 返回相应

3.确定请求方式和路由

    POST    brower_history/
"""

class UserHistoryView(LoginRequiredMixin,View):

    def post(self,request):
        # ①有用户信息(必须是登陆用户)
        user=request.user
        # ②获取商品id
        data=json.loads(request.body.decode())
        sku_id=data.get('sku_id')
        # ③判断商品id(查询)
        try:
            sku=SKU.objects.get(id=sku_id)
        except SKU.DoesNotExist:
            return JsonResponse({'code':RETCODE.NODATAERR,'errmsg':'没有此商品'})
        # ④数据保存
        redis_conn = get_redis_connection('history')

        # 一,创建管道实例
        pipeline=redis_conn.pipeline()
        #二.管道收集指令
        # 4.1 先去重
        pipeline.lrem('history_%s'%user.id,0,sku_id)
        # 4.2 再添加
        pipeline.lpush('history_%s'%user.id,sku_id)
        # 4.3 确保有5条记录
        pipeline.ltrim('history_%s'%user.id,0,4)
        #三,执行 !!!! 一定要记得执行
        pipeline.execute()

        # # 4.1 先去重
        # redis_conn.lrem('history_%s'%user.id,0,sku_id)
        # # 4.2 再添加
        # redis_conn.lpush('history_%s'%user.id,sku_id)
        # # 4.3 确保有5条记录
        # redis_conn.ltrim('history_%s'%user.id,0,4)
        # ⑤ 返回相应
        return JsonResponse({'code':RETCODE.OK,'errmsg':'ok'})


    def get(self,request):

        # ①获取用户信息
        user=request.user
        # ②获取redis数据 [16,10,1]
        redis_conn = get_redis_connection('history')
        ids=redis_conn.lrange('history_%s'%user.id,0,4)

        history_list=[]
        for id in ids:
            # ③ 根据id查询商品详细信息 SKU
            sku=SKU.objects.get(id=id)
            # ④ 将对象转换为字典
            history_list.append({
                 'id': sku.id,
                'name': sku.name,
                'default_image_url': sku.default_image.url,
                'price': sku.price
            })
        # ⑤ 返回数据
        return JsonResponse({'code':RETCODE.OK,'errmsg':'ok','skus':history_list})

"""
1.功能分析
    用户行为:
    前端行为:
    后端行为:

2. 分析后端实现的大体步骤
        ①获取用户信息
        ②获取redis数据 [16,10,1]
        ③ 根据id查询商品详细信息 SKU
        ④ 将对象转换为字典
        ⑤ 返回数据


3.确定请求方式和路由
    GET
"""

