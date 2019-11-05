from django.db import models

# Create your models here.
"""

省/市/区
id          name        parent_id

10000       河北省         NULL

10010       石家庄市        10000
10020       保定市          10000


10011       长安区          10010
10012       桥西区          10010




"""

from django.db import models

class Area(models.Model):
    """省市区"""
    # id
    name = models.CharField(max_length=20, verbose_name='名称')
    # self 自关联
    # on_delete 级联操作
    # related_name 关联模型类名小写_set  area_set
    #           related_name='subs',
    parent = models.ForeignKey('self', on_delete=models.SET_NULL, related_name='subs', null=True, blank=True, verbose_name='上级行政区划')

    class Meta:
        db_table = 'tb_areas'
        verbose_name = '省市区'
        verbose_name_plural = '省市区'

    def __str__(self):
        return self.name
