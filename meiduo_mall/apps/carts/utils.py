

"""
合并的逻辑
1.思想: 抽象的问题具体化
2.具体化之后,步骤就出来
3.步骤出来之后,就可以实现抽象的代码


抽象的事务具体化

1.获取cookie数据
cookie
    {
        1:{count:5,selected:False},
        3:{count:5,selected:True},
    }

2.把redis数据读取下来

redis

    hash  {1:100,2:100}
    set   {1,2}

初始化一个字典
一个列表用于记录选中的id
一个列表用于记录未选中的id
3. 对cookie数据进行遍历
合并
  new_update_hash               {1:5,3:5}       更新到redis中
  new_update_selected_set       {3}           更新到reids中
  new_update_unselected_set     {1}           更新到reids中

4.将合并的数据更新到redis中





1.当cookie中和redis中都有相同的商品时,数量怎么办?
    产品1: 以cookie为主,             v
    产品2: 以Redis为主,
    产品3: 以Redis+cookie为主,

2.cookie中有数据,redis中没有
    将cookie中的数据,添加到redis中
3.redis中已有的数据,不动

"""
import base64
import pickle

from django_redis import get_redis_connection


def merge_cookie_to_redis(request,user,response):

    """
        1.获取cookie数据
        2.把redis数据读取下来
        初始化一个字典
        一个列表用于记录选中的id
        一个列表用于记录未选中的id
        3. 对cookie数据进行遍历
        4.将合并的数据更新到redis中
        5.删除cookie数据
    """
    # 1.获取cookie数据
    cookie_str=request.COOKIES.get('carts')
    if cookie_str is not None:
        cookie_dict=pickle.loads(base64.b64decode(cookie_str))
        #有数据合并
        # 2.把redis数据读取下来
        # user=request.user
        redis_conn = get_redis_connection('carts')
        id_count_bytes=redis_conn.hgetall('carts_%s'%user.id)
        selected_ids=redis_conn.smembers('selected_%s'%user.id)
        # redis的数据读取出来都是bytes
        id_count_redis={}
        for id,count in id_count_bytes.items():
            id_count_redis[int(id)]=int(count)
        # 初始化一个字典
        new_hash_update_data={}
        # 一个列表用于记录选中的id
        selected_list=[]
        # 一个列表用于记录未选中的id
        unselected_list=[]
        # 3. 对cookie数据进行遍历
        # {sku_id:{count:xxx,selected:xxx}}
        for sku_id,count_selected_dict in cookie_dict.items():
            if sku_id in id_count_redis:
                #如果sku_id 在id_count_redis中,则count以cookie为主
                new_hash_update_data[sku_id]=count_selected_dict['count']
            else:
                #如果sku_id 没有在id_count_redis中,则添加到redis中
                new_hash_update_data[sku_id]=count_selected_dict['count']

            # 选中状态以cookie为主
            if count_selected_dict['selected']:
                selected_list.append(sku_id)
            else:
                unselected_list.append(sku_id)

        # 4.将合并的数据更新到redis中
        # hash
        redis_conn.hmset('carts_%s'%user.id,new_hash_update_data)
        # 选中的id,应该添加到集合中
        if len(selected_list)>0:
            redis_conn.sadd('selected_%s'%user.id,*selected_list)
        # 未选中的应该从redis的集合中删除
        if len(unselected_list)>0:
            redis_conn.srem('selected_%s'%user.id,*unselected_list)

        # 5.删除cookie数据
        response.delete_cookie('carts')

        return response
    else:
        return response
