from django.db import models

# Create your models here.
"""
表和表的关系

1:1(一对一)
常用信息

user_id     name    age     tel
1           如花      18      133xxxx


不长用信息
user_id       address     父亲      母亲
     1        江南          如x      xxxx



1:n(一对多)

用户表
user_id     name        age
1             唐伯虎       22

订单表
user_id        order_id    price       date
   1             1111        200         2019-1-1
    1            1112        2000        2019-1-2

n:m(多对多)

学生:老师

商品:供应商

商品
商品id    商品name
111         iPhone
222         华为

供应商
供应商id   供应商名字
345         富士康
987         付土康

商品和供应商的关系

id      商品id    供应商id
        111      345
        111      987
        222     345
        222     987
"""

from django.db import models
from utils.models import BaseModel
# Create your models here.
class ContentCategory(BaseModel):
    """广告内容类别"""
    name = models.CharField(max_length=50, verbose_name='名称')
    key = models.CharField(max_length=50, verbose_name='类别键名')

    class Meta:
        db_table = 'tb_content_category'
        verbose_name = '广告内容类别'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


class Content(BaseModel):
    """广告内容"""
    category = models.ForeignKey(ContentCategory, on_delete=models.PROTECT, verbose_name='类别')
    title = models.CharField(max_length=100, verbose_name='标题')
    url = models.CharField(max_length=300, verbose_name='内容链接')
    image = models.ImageField(null=True, blank=True, verbose_name='图片')
    text = models.TextField(null=True, blank=True, verbose_name='内容')
    sequence = models.IntegerField(verbose_name='排序')
    status = models.BooleanField(default=True, verbose_name='是否展示')

    class Meta:
        db_table = 'tb_content'
        verbose_name = '广告内容'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.category.name + ': ' + self.title
