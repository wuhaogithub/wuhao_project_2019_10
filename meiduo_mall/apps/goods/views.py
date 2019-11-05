from django.http import JsonResponse
from django.shortcuts import render

# Create your views here.
from django.views import View

from apps.goods.models import SKU, GoodsCategory, GoodsVisitCount
from apps.goods.utils import get_breadcrumb
from utils.response_code import RETCODE

"""
1.功能分析
    用户行为:       用户会点击下一页,会点击排序
    前端行为:       展示相应的数据
    后端行为:       根据用户的点击返回数据

2. 分析后端实现的大体步骤

    ① 先根据分类,把所有数据查询出来
    ② 添加排序
    ③ 添加分页


3.确定请求方式和路由
    GET     /list/?分类id=1
    GET     /list/分类id/  v
"""

class ListView(View):

    def get(self,request,category_id,page):
        try:
            category=GoodsCategory.objects.get(id=category_id)
        except GoodsCategory.DoesNotExist:
            return render(request,'404.html')

        # 面包屑
        # 因为很多地方,都用到了面包屑,将面包屑,抽取出去
        breadcrumb=get_breadcrumb(category)

        # 尽量不要将表的信息,暴露出去
        # 排序字段是使用的查询字符串 ?sort=
        # default:以上架时间
        # hot   :热销 销量
        # price :价格
        sort=request.GET.get('sort')
        if sort == 'default':
            order_field='create_time'
        elif sort == 'hot':
            order_field='sales'
        else:
            order_field='-price'

        # ① 先根据分类,把所有数据查询出来
        data=SKU.objects.filter(category=category).order_by(order_field)
        # data=SKU.objects.filter(category_id=category_id)
        # ② 添加排序
        # ③ 添加分页
        from django.core.paginator import Paginator
        # 3.1创建分页对象
        # per_page : 每页多少条数据
        paginator=Paginator(object_list=data,per_page=5)
        # 3.2获取指定页面的数据
        page_data=paginator.page(page)
        # 3.3获取总页数
        total_page=paginator.num_pages

        context = {

            'breadcrumb': breadcrumb,  # 面包屑导航
            'sort': sort,  # 排序字段
            'category': category,  # 第三级分类
            'page_skus': page_data,  # 分页后数据
            'total_page': total_page,  # 总页数
            'page_num': page,  # 当前页码
        }

        return render(request,'list.html',context=context)

"""
1.功能分析
    用户行为:   点击某一个分类,进入到列表页面
    前端行为:   应该返回一个分类id
    后端行为:   根据分类id查询指定数据

2. 分析后端实现的大体步骤
        ① 获取分类id
        ② 判断分类id是否正确
        ③ 根据分类id进行查询 [SKU,SKU,SKU]
        ④ 将对象列表转换为字典
        ⑤ 返回相应

3.确定请求方式和路由

    GET     hotskus/cat_id/
    GET     hotskus/?cat_id=xxx

"""
class HotSKUView(View):

    def get(self,request,category_id):
        # ① 获取分类id
        # ② 判断分类id是否正确
        try:
            category=GoodsCategory.objects.filter(id=category_id)
        except GoodsCategory.DoesNotExist:
            return JsonResponse({'code':RETCODE.NODATAERR,'errmsg':'没有此数据'})
        # ③ 根据分类id进行查询 [SKU,SKU,SKU]
        skus=SKU.objects.filter(category=category,is_launched=True).order_by('-sales')[:2]

        # ④ 将对象列表转换为字典
        hot_skus=[]
        for sku in skus:
            hot_skus.append({
                'id': sku.id,
                'default_image_url': sku.default_image.url,
                'name': sku.name,
                'price': sku.price
            })
        # ⑤ 返回相应
        return JsonResponse({'code':RETCODE.OK,'errmsg':'ok',"hot_skus":hot_skus})


from django import http
from django.shortcuts import render
from django.views import View
from apps.contents.utils import get_categories
from apps.goods.models import SKU, GoodsCategory
from apps.goods.utils import get_breadcrumb
from utils.response_code import RETCODE


class DetailView(View):

    def get(self,request,sku_id):

        # 获取当前sku的信息
        try:
            sku = SKU.objects.get(id=sku_id)
        except SKU.DoesNotExist:
            return render(request, '404.html')

        # 查询商品频道分类
        categories = get_categories()
        # 查询面包屑导航
        breadcrumb = get_breadcrumb(sku.category)

        # 构建当前商品的规格键
        sku_specs = sku.specs.order_by('spec_id')
        sku_key = []
        for spec in sku_specs:
            sku_key.append(spec.option.id)
        # 获取当前商品的所有SKU
        skus = sku.spu.sku_set.all()
        # 构建不同规格参数（选项）的sku字典
        spec_sku_map = {}
        for s in skus:
            # 获取sku的规格参数
            s_specs = s.specs.order_by('spec_id')
            # 用于形成规格参数-sku字典的键
            key = []
            for spec in s_specs:
                key.append(spec.option.id)
            # 向规格参数-sku字典添加记录
            spec_sku_map[tuple(key)] = s.id
        # 获取当前商品的规格信息
        goods_specs = sku.spu.specs.order_by('id')
        # 若当前sku的规格信息不完整，则不再继续
        if len(sku_key) < len(goods_specs):
            return
        for index, spec in enumerate(goods_specs):
            # 复制当前sku的规格键
            key = sku_key[:]
            # 该规格的选项
            spec_options = spec.options.all()
            for option in spec_options:
                # 在规格参数sku字典中查找符合当前规格的sku
                key[index] = option.id
                option.sku_id = spec_sku_map.get(tuple(key))
            spec.spec_options = spec_options

        # 渲染页面
        context = {
            'categories': categories,
            'breadcrumb': breadcrumb,
            'sku': sku,
            'specs': goods_specs,
        }

        return render(request,'detail.html',context)


"""
1.功能分析
    用户行为:    用户点击了某一个商品/某一个类别,应该+1
    前端行为:       前端必须给我分类id
    后端行为:    统计每一个商品分类在每一天中的访问量

2. 分析后端实现的大体步骤
        1.分类id
        2.获取今天的日期
        3.增加访问量

3.确定请求方式和路由
    GET
    POST  detail/visit/cat_id/
"""

class VisitCountView(View):

    def post(self,request,category_id):
        # 1.分类id
        try:
            category=GoodsCategory.objects.get(id=category_id)
        except GoodsCategory.DoesNotExist:
            return JsonResponse({'code':RETCODE.NODATAERR,'errmsg':'没有此分类'})
        # 2.获取今天的日期

        from django.utils import timezone
        today=timezone.localdate()
        # 3.增加访问量
        # 3.1 我们要根据 分类id和日期,查询数据库 是否已经有今天的指定的分类记录
        try:
            vc=GoodsVisitCount.objects.get(category=category,date=today)
        except GoodsVisitCount.DoesNotExist:
            #不存在
            # 添加记录 count=1
            GoodsVisitCount.objects.create(
                category=category,
                date=today,
                count=1
            )

            return JsonResponse({'code':RETCODE.OK,'errmsg':'ok'})
        else:
            #存在,存在就将count+1
            vc.count+=1
            vc.save()
            return JsonResponse({'code': RETCODE.OK, 'errmsg': 'ok'})



