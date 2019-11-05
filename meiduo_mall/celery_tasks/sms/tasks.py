"""

生产者
    创建的包中的文件,必须起名为 tasks.py
    1.所谓的生产者其实就是任务,所谓的任务其实就是 函数
    2.这个函数必须要被 celery的实例对象的task装饰器装饰
    3.这个函数可以要让celery自动检测到  ,自动检测 tasks.py文件任务
"""
from libs.yuntongxun.sms import CCP
from celery_tasks.main import app

"""
bind=True 是表示 任务的第一个参数永远 是self self 是表示任务本身
重试时间        default_retry_delay
重试次数        max_retries
"""
@app.task(bind=True,default_retry_delay=10)
def send_sms_code(self,mobile,sms_code):
    # 没有的变量,以参数的形式传递
    try:
        rect=CCP().send_template_sms(mobile, [sms_code, 5], 1)
    except Exception as e:
        raise self.retry(exc=e,max_retries=3)

    if rect != 0:
        #重试
        raise self.retry(exc=Exception('发送失败'),max_retries=3)
