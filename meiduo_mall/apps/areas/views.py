from django.shortcuts import render

# Create your views here.
from django.views import View

from apps.areas.models import Area
from utils.response_code import RETCODE

"""

省  select * from tb_areas where parent_id is NULL;


市  select * from tb_areas where parent_id=130000;
区  select * from tb_areas where parent_id=130100;


如果前端传递一个 parent_id 我们就认为是获取 市/区县信息

如果前端没有传递一个 parent_id 我们就认为是获取 省的信息


areas/
areas/?parent_id=xxxxxx
"""

"""
1.功能分析
    用户行为:
    前端行为:
            如果前端传递一个 parent_id 我们就认为是获取 市/区县信息

            如果前端没有传递一个 parent_id 我们就认为是获取 省的信息


            areas/
            areas/?parent_id=xxxxxx

    后端行为:

2. 分析后端实现的大体步骤


3.确定请求方式和路由
"""
"""
问题:
    1.省市区数据有可能会经常访问到
    2.省市区数据不经常发生变化(某一个时间段)
    3.当前的代码 会经常查询数据库

解决方向是: 减少数据库的查询

解决实现: 把省市区数据 保存在 redis中



"""
from django.http import JsonResponse
from django.core.cache import cache

class AreasView(View):

    def get(self,request):
        parent_id=request.GET.get('area_id')
        if parent_id is None:

            #先读取缓存
            cache_pro=cache.get('cache_pro')

            if cache_pro is None:
                #说明没有缓存

                # 省
                # [Area,Area,Area]
                proviences=Area.objects.filter(parent=None)

                # 将对象列表转换为字典列表
                # JsonResponse 默认是可以对字典进行JSON转换的
                cache_pro=[]
                for pro in proviences:
                    cache_pro.append({
                        'id':pro.id,
                        'name':pro.name
                    })

                #设置缓存
                # 可以用redis,也可以用系统集成号的 cache

                # cache.set(key,value,expires)
                cache.set('cache_pro',cache_pro,24*3600)


            return JsonResponse({'code':RETCODE.OK,'province_list':cache_pro})
            # return JsonResponse(pro_list,safe=False)
            # return render()
            # return Json


        else:
            # 市/区县
            # parent_id
            #先获取缓存
            city_list=cache.get('city_%s'%parent_id)
            #判断
            if city_list is None:
                #1. 根据省的id查询市 查询集
                # pro=Area.objects.get(id=parent_id)
                # cities=pro.subs.all()
                #或者
                cities=Area.objects.filter(parent_id=parent_id)
                # [Area,Area]
                #2.  将对象列表遍历转换为字典列表
                city_list=[]
                for city in cities:
                    city_list.append({
                        'id':city.id,
                        'name':city.name
                    })

                #存储到redis
                cache.set('city_%s'%parent_id,city_list,24*3600)
            #3.返回相应
            return JsonResponse({'code':RETCODE.OK,'subs':city_list})
            # return JsonResponse({'code':RETCODE.OK,'sub_date':{'subs':city_list}})
            # return JsonResponse(city_list,safe=False)

