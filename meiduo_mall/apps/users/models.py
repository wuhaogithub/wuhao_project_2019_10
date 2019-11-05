from django.db import models

# Create your models here.
"""
1. 可以自己定义模型
    要自己实现密码的加密,密码的验证等功能
    class User(models.Model):
        username=models.CharField(max_length=20)
        password=models.CharField(max_length=20)
        mobile=models.CharField(max_length=20)
2. 使用系统的模型 (系统的模型可以帮助我们进行密码的加密和密码的验证)

"""
from django.contrib.auth.models import AbstractUser

# 我们期望 系统使用我们的 User
# 我们就应该告知系统 使用我们的模型类
"""
1.自己分析注册页面 我应该保存哪些字段(自己找一些网站自己分析)
2.定义模型(使用 AbstractUser)
3.定义模型之后,迁移就是报错!!!! 我们要替换系统的User -- AUTH_USER_MODEL
"""
class User(AbstractUser):

    mobile=models.CharField(max_length=11,unique=True,verbose_name='手机号')

    #邮箱的激活状态
    email_active=models.BooleanField(default=False,verbose_name='邮件激活状态')

    #默认地址
    default_address = models.ForeignKey('Address', related_name='users', null=True, blank=True,
                                        on_delete=models.SET_NULL, verbose_name='默认地址')

    class Meta:
        db_table = 'tb_users'
        verbose_name = '用户'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.username
"""
分析模型的技巧:
    1.根据功能进行模型的分析
    2.根据功能进行模型的考量(增删改查)
    3.优化(最再考虑)
"""
from utils.models import BaseModel

class Address(BaseModel):
    """用户地址"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='addresses', verbose_name='用户')
    title = models.CharField(max_length=20, verbose_name='地址名称')
    receiver = models.CharField(max_length=20, verbose_name='收货人')
    province = models.ForeignKey('areas.Area', on_delete=models.PROTECT, related_name='province_addresses', verbose_name='省')
    city = models.ForeignKey('areas.Area', on_delete=models.PROTECT, related_name='city_addresses', verbose_name='市')
    district = models.ForeignKey('areas.Area', on_delete=models.PROTECT, related_name='district_addresses', verbose_name='区')
    place = models.CharField(max_length=50, verbose_name='地址')
    mobile = models.CharField(max_length=11, verbose_name='手机')
    tel = models.CharField(max_length=20, null=True, blank=True, default='', verbose_name='固定电话')
    email = models.CharField(max_length=30, null=True, blank=True, default='', verbose_name='电子邮箱')
    is_deleted = models.BooleanField(default=False, verbose_name='逻辑删除')

    class Meta:
        db_table = 'tb_address'
        verbose_name = '用户地址'
        verbose_name_plural = verbose_name
        ordering = ['-update_time']
