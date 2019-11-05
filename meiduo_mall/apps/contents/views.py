from collections import OrderedDict

from django.shortcuts import render
from django.views import View
# Create your views here.
from apps.contents.models import ContentCategory
from apps.contents.utils import get_categories
from apps.goods.models import GoodsChannel

"""
首页加载的非常慢
    1.我们要通过数据库查询分类数据,查询首页数据
    2.还需要经过渲染

优先想到的就是 对分类信息进行缓存处理

经过数据缓存之后,数据的渲染还是很慢

最终我们考虑,让用户直接访问 已经渲染好的html页面, 页面静态化

静态页面怎么来实现呢?
    ① 还是需要先 访问数据库
    ② 将查询处理的数据进行渲染
    ③ 将渲染的html页面,写入到指定文件
    当用户访问的首页的时候,我们让他访问这个页面就可以了

"""

class IndexView(View):


    def get(self,request):
        # 查询商品频道和分类
        categories=get_categories()

        # 广告数据
        contents = {}
        content_categories = ContentCategory.objects.all()
        for cat in content_categories:
            contents[cat.key] = cat.content_set.filter(status=True).order_by('sequence')

        # 渲染模板的上下文
        context = {
            'categories': categories,
            'contents': contents,
        }

        return render(request,'index.html',context=context)


######################FDFS上传图片的代码#################################
# 以下代码 在 python manage.py shell 中运行
#1.导入Fdfs库
# from fdfs_client.client import Fdfs_client
#
# #2.创建Fdfs客户端实例,让客户端实例加载配置文件
# #   因为配置文件可以找到tracker server
# client=Fdfs_client('utils/fastdfs/client.conf')
# #3.上传文件, 使用绝对路径
# client.upload_by_filename('/home/python/Desktop/images/1.jpg')
#4.获取(分析)上传成功之后返回的数据
"""
getting connection
<fdfs_client.connection.Connection object at 0x7fb42c7bf198>
<fdfs_client.fdfs_protol.Tracker_header object at 0x7fb42c7bf160>
{'Remote file_id': 'group1/M00/00/00/wKjllF2uzOmAcOc-AALd0X8OZb4802.jpg',
'Uploaded size': '183.00KB',
'Storage IP': '192.168.229.148',
 'Local file name': '/home/python/Desktop/images/1.jpg',
 'Group name': 'group1',
  'Status': 'Upload successed.'
  }

"""