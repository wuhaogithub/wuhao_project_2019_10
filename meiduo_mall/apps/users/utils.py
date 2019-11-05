#'http://www.meiduo.site:8000/emailsactive/?token=%s'%token

from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from meiduo_mall import settings
from itsdangerous import BadData

def generic_active_email_url(id,email):

    #1.创建加密实例对象
    s = Serializer(secret_key=settings.SECRET_KEY,expires_in=3600)
    #2.组织数据
    data = {
        'id':id,
        'email':email  #可有可无
    }
    #3.加密
    serect_data=s.dumps(data)

    #4.返回加密数据
    return 'http://www.meiduo.site:8000/emailsactive/?token=%s'%serect_data.decode()


def check_active_token(token):

    #1.创建实例对象
    s = Serializer(secret_key=settings.SECRET_KEY, expires_in=3600)
    #2.解密(解密过程有可能有异常)
    try:
        data=s.loads(token)
    except BadData:
        return None
    #3.返回数据
    return data
    # return data.get('id'),data.get('email')

