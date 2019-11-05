#############Itsdangerous的代码################################
#加密数据的过程
#1.导入库
from meiduo_mall import settings
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer

#2.创建一个实例对象
#secret_key             秘钥,通常使用 setting 文件中的 SECRET_KEY
# expires_in=None       过期时间 默认 3600秒
s = Serializer(secret_key=settings.SECRET_KEY, expires_in=3600)
#3.有原始数据
data={
    'openid':'abcdefg'
}
#4.加密数据
s.dumps(data)
#b'eyJleHAiOjE1NzE0NzY0NDksImFsZyI6IkhTNTEyIiwiaWF0IjoxNTcxNDcyODQ5fQ.eyJvcGVuaWQiOiJhYmNkZWZnIn0.wiNiMpuBeF7jZCvbzz1Tq2K5I1FcFk9PBy5iAF3Iu2Fk9A0VOCxaw2OZ8XLpPpzrPxp9FI9W1TvkMcO35xasKg'

###############################
#解密数据的过程
#1.导入库
from meiduo_mall import settings
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
#2.创建一个实例对象,加密时候的参数要和解密的参数一致
s = Serializer(secret_key=settings.SECRET_KEY, expires_in=3600)
#3.有加密数据
secret_data='eyJleHAiOjE1NzE0NzY0NDksImFsZyI6IkhTNTEyIiwiaWF0IjoxNTcxNDcyODQ5fQ.eyJvcGVuaWQiOiJhYmNkZWZnIn0.wiNiMpuBeF7jZCvbzz1Tq2K5I1FcFk9PBy5iAF3Iu2Fk9A0VOCxaw2OZ8XLpPpzrPxp9FI9W1TvkMcO35xasKg'
#4.解密数据
s.loads(secret_data)

#######################解密数据有可能存在异常###################################

#解密数据的过程
#1.导入库
from meiduo_mall import settings
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
#2.创建一个实例对象,加密时候的参数要和解密的参数一致
s = Serializer(secret_key=settings.SECRET_KEY, expires_in=3600)
#3.有加密数据
secret_data='eyJleHAiOjE1NzE0NzY0NDksImFsZyI6IkhTNTEyIiwiaWF0IjoxNTcxNDcyODQ5fQ.eyJvcGVuaWQiOiJhYmNkZWZnIn0.wiNiMpuBeF7jZCvbzz1Tq2K5I1Fcfk9PBy5iAF3Iu2Fk9A0VOCxaw2OZ8XLpPpzrPxp9FI9W1TvkMcO35xasKg'
#4.解密数据
s.loads(secret_data)


########################如果数据过期了,也会报异常########################################
from meiduo_mall import settings
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer

#2.创建一个实例对象
#secret_key             秘钥,通常使用 setting 文件中的 SECRET_KEY
# expires_in=None       过期时间 默认 3600秒
s = Serializer(secret_key=settings.SECRET_KEY, expires_in=1)
#3.有原始数据
data={
    'openid':'abcdefg'
}
#4.加密数据
secret_data=s.dumps(data)

s.loads(secret_data)