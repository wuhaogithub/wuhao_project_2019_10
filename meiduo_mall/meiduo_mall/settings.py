"""
Django settings for meiduo_mall project.

Generated by 'django-admin startproject' using Django 1.11.11.

For more information on this file, see
https://docs.djangoproject.com/en/1.11/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.11/ref/settings/
"""
import datetime

"""
git:    https://gitee.com/itcastitheima/meiduo_46.git
tel/微信: 18310820688
"""

import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.11/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '8f%zh3u8*72(ljqo1#4=o6cf)tpajo6o#^sbr730f8_hqn2+v!'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# 允许以哪些主机方式来访问,
# 默认是 127.0.0.1
# 如果我们以 域名的形式访问,就把 域名 以字符串的形式添加就可以
# 添加了域名之后,默认的127 就不能访问了
ALLOWED_HOSTS = ['www.meiduo.site','127.0.0.1','192.168.229.148']


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    #'users',        #错误的
    # 'apps.users', #正确的
    'apps.users.apps.UsersConfig', # = 'users'
    'apps.oauth',
    'apps.areas',
    'apps.contents',
    'apps.goods',
    'apps.orders',
    'apps.payment',
    'apps.meiduo_admin',
    'django_crontab',
    'corsheaders',
    'rest_framework''',

]

CRONJOBS = [
    # 每1分钟生成一次首页静态文件
    # 参数1:  定时任务的频次
    # 参数2:  定时任务,所谓的定时任务就是函数
    # 参数3:  日志
    ('*/1 * * * *', 'apps.contents.crons.generate_static_index_html', '>> ' + os.path.join(BASE_DIR, 'logs/crontab.log'))
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'corsheaders.middleware.CorsMiddleware',
]

ROOT_URLCONF = 'meiduo_mall.urls'

# Jinja2模板 想使用 Django的过滤器(函数)
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.jinja2.Jinja2',
        'DIRS': [os.path.join(BASE_DIR,'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            #'environment':'jinja2.Environment',#默认配置
            'environment':'utils.jinja2_env.environment',#默认配置

            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'meiduo_mall.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.11/ref/settings/#databases

DATABASES = {
    'default': {  #主服务器
        'ENGINE': 'django.db.backends.mysql', # 数据库引擎
        'HOST': '127.0.0.1', # 数据库主机
        'PORT': 3306, # 数据库端口
        'USER': 'root', # 数据库用户名
        'PASSWORD': 'mysql', # 数据库用户密码
        'NAME': 'meiduo_mall_46' # 数据库名字
    },
    # 'slave': {
    #     'ENGINE': 'django.db.backends.mysql', # 数据库引擎
    #     'HOST': '127.0.0.1', # 数据库主机
    #     'PORT': 8306, # 数据库端口
    #     'USER': 'root', # 数据库用户名
    #     'PASSWORD': 'mysql', # 数据库用户密码
    #     'NAME': 'meiduo_mall_46' # 数据库名字
    # },
}
# DATABASE_ROUTERS = ['utils.db_router.MasterSlaveDBRouter']


# Password validation
# https://docs.djangoproject.com/en/1.11/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/1.11/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.11/howto/static-files/

STATIC_URL = '/static/'
# 静态资源
STATICFILES_DIRS=[
    os.path.join(BASE_DIR,'static'),
]

#################redis##########################
CACHES = {
    "default": {  #预留 保存其他的数据
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379/1",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    },
    "session": {  #保存session信息
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379/2",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    },
    "code": {  # 保存session信息
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379/3",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    },
    "history": {  # 保存session信息
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379/4",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    },
    "carts": {  # 保存session信息
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379/5",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    },
}
SESSION_ENGINEFastDFS = "django.contrib.sessions.backends.cache"
SESSION_CACHE_ALIAS = "session"


#############日志############################
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,  # 是否禁用已经存在的日志器
    'formatters': {  # 日志信息显示的格式
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(lineno)d %(message)s'
        },
        'simple': {
            'format': '%(levelname)s %(module)s %(lineno)d %(message)s'
        },
    },
    'filters': {  # 对日志进行过滤
        'require_debug_true': {  # django在debug模式下才输出日志
            '()': 'django.utils.log.RequireDebugTrue',
        },
    },
    'handlers': {  # 日志处理方法
        'console': {  # 向终端中输出日志
            'level': 'INFO',
            'filters': ['require_debug_true'],
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
        'file': {  # 向文件中输出日志
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(BASE_DIR, 'logs/meiduo.log'),  # 日志文件的位置
            'maxBytes': 300 * 1024 * 1024,
            'backupCount': 10,
            'formatter': 'verbose'
        },
    },
    'loggers': {  # 日志器
        'django': {  # 定义了一个名为django的日志器
            'handlers': ['console', 'file'],  # 可以同时向终端与文件中输出日志
            'propagate': True,  # 是否继续传递日志信息
            'level': 'INFO',  # 日志器接收的最低日志级别
        },
    }
}

#########替换系统的User###############################
#
# 指定使用我们的用户模型
# AUTH_USER_MODEL = '子应用名.模型类名'
AUTH_USER_MODEL = 'users.User'


###############认证后端####################################
AUTHENTICATION_BACKENDS = [
    # 'django.contrib.auth.backends.ModelBackend' #默认配置
    'utils.users.UsernameMobileModelBackend',
]


##############未登录跳转到指定登陆页面################################
# LOGIN_URL='/accounts/login/' #默认值

LOGIN_URL='/login/'


#############QQ登陆使用的信息########################################

QQ_CLIENT_ID = '101518219'

QQ_CLIENT_SECRET = '418d84ebdc7241efb79536886ae95224'

QQ_REDIRECT_URI = 'http://www.meiduo.site:8000/oauth_callback/'

##########发送邮件相关#############################

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.163.com'
EMAIL_PORT = 25
#发送邮件的邮箱
EMAIL_HOST_USER = 'qi_rui_hua@163.com'
#在邮箱中设置的客户端授权密码
EMAIL_HOST_PASSWORD = '123456abc'

"""
暂时理解:
    Docker 是一个没有可视化界面的虚拟机


    1.必须要在主机中 安装 Docker
    2.Docker 是一个客户端-服务端(C/S)架构程序
        只需要安装 客户端
        服务器已经安装好了,例如:https://hub.docker.com/
    3.Docker 包括三个基本概念
        ① 镜像（Image）       需要的环境包
        ② 容器（Container）   运行起来的镜像叫做容器
        ③ 仓库（Repository）

"""

#############自定义文件存储##################################

# 指定自定义的Django文件存储类
DEFAULT_FILE_STORAGE = 'utils.storage.MyStorage'

##############AliPay#################################

ALIPAY_APPID = '2016091600523030'
ALIPAY_DEBUG = True
ALIPAY_URL = 'https://openapi.alipaydev.com/gateway.do'
ALIPAY_RETURN_URL = 'http://www.meiduo.site:8000/payment/status/'
APP_PRIVATE_KEY_PATH = os.path.join(BASE_DIR, 'apps/payment/keys/app_private_key.pem')
ALIPAY_PUBLIC_KEY_PATH = os.path.join(BASE_DIR, 'apps/payment/keys/alipay_public_key.pem')


"""

Nginx 擅长处理 静态资源(html,css,js,png,.avi)

用户请求(登陆) --> Nginx --> uWSGI  -->Django -->路由引导到登陆视图





uWSGI  -->Django -->路由引导到登陆视图


http --> uWSGI  -->Django -->路由引导到相应视图
"""

# CORS
CORS_ORIGIN_WHITELIST = (
    'http://127.0.0.1:8080',
    'http://localhost:8080',
    'http://www.meiduo.site:8080',
    'http://api.meiduo.site:8000'
)
CORS_ALLOW_CREDENTIALS = True  # 允许携带cookie

REST_FRAMEWORK = {
    # 权限认证
    'DEFAULT_AUTHENTICATION_CLASSES': (
        # Jwt认证
        'rest_framework_jwt.authentication.JSONWebTokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.BasicAuthentication',
    ),
}

JWT_AUTH = {
    'JWT_EXPIRATION_DELTA': datetime.timedelta(days=1),
    'JWT_RESPONSE_PAYLOAD_HANDLER':
    'apps.meiduo_admin.utils.jwt_response_payload_handler',

}