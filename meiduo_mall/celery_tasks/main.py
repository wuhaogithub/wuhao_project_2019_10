"""
http://docs.celeryproject.org/en/latest/django/first-steps-with-django.html#using-celery-with-django

生产者 -->中间人(消息队列)-->消费者

生产者
    创建的包中的文件,必须起名为 tasks.py
    1.所谓的生产者其实就是任务,所谓的任务其实就是 函数
    2.这个函数必须要被 celery的实例对象的task装饰器装饰
    3.这个函数可以要让celery自动检测到  ,自动检测 tasks.py文件任务

中间人
消费者
    1.消费者通过一条指令, 在虚拟环境中设置就可以了
    语法:celery -A proj worker -l info
Celery 把这3者串联起来

"""
from celery import Celery
import os

# 0. 在创建Celery之前我们需要加载 django工程的配置文件
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "meiduo_mall.settings")

# 1. Celery 将3者串联起来了,先创建一个celery实例
# main 相当于给celery实例设置一个唯一的名字
# 一般我们习惯使用 包名/文件名
app = Celery(main='celery_tasks')


#2. 设置我们的中间人,让celery加载中间人配置信息
# 文件路径
app.config_from_object('celery_tasks.config')

#3.让celey自动检测我们的任务
# 列表
# 列表元素的值就是 任务的包路径
app.autodiscover_tasks(['celery_tasks.sms','celery_tasks.email'])


# 4. 运行 消费者
# 消费者通过一条指令, 在虚拟环境中设置就可以了
#     语法:celery -A proj worker -l info
# proj  指的是 celery实例对象的脚本路径
# 虚拟环境中运行该指令 ,路径是 base_dir
# celery -A celery_tasks.main worker -l info