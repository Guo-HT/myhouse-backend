"""
Django settings for MyHouse project.

Generated by 'django-admin startproject' using Django 2.1.15.

For more information on this file, see
https://docs.djangoproject.com/en/2.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.1/ref/settings/
"""

import os
# import pymysql
# pymysql.version_info = (1, 3, 13, "final", 0)  # 解决mysql版本问题报错而添加的代码
# pymysql.install_as_MySQLdb()
import MySQLdb


# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'g)b=1h!@5tl0ar()@3#crta6@5zmz0*@q$59hwra&z_6+fd%vb'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = ['*', ]

# allow websocket
WEBSOCKET_ACCEPT_ALL = True
# WEBSOCKET_FACTORY_CLASS = 'dwebsocket.backends.uwsgi.factory.uWsgiWebSocketFactory'

# Application definition

INSTALLED_APPS = [
    'simpleui',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # 插件
    'corsheaders',  # 解决跨域
    # 'dwebsocket',   # 即时通信，直接使用，不需要安装
    'gunicorn',  # gunicorn服务器
    'ckeditor',     # 后台,富文本
    'ckeditor_uploader',  # 后台,富文本上传
    'silk',  # 性能监测
    # 自定义
    'UserManagement',  # 用户管理
    'Data',  # 数据管理
    'Essay',  # 文章管理
]

# 设置跨域可用
CORS_ALLOW_CREDENTIALS = True
CORS_ORIGIN_ALLOW_ALL = True
CORS_ORIGIN_WHITELIST = ('http://180.76.174.125:*', )

SESSION_COOKIE_SAMESITE = None  # response header set-cookie:samesite=lax  Default: 'Lax'
CSRF_COOKIE_SAMESITE = None

CORS_ALLOW_METHODS = (
    'DELETE',
    'GET',
    'OPTIONS',
    'PATCH',
    'POST',
    'PUT',
    'VIEW',
)

CORS_ALLOW_HEADERS = (
    'XMLHttpRequest',
    'X_FILENAME',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
    'Pragma',
)

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',  # 解决同源
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',  # CSRF防护中间件
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    # 'dwebsocket.middleware.WebSocketMiddleware',
    'silk.middleware.SilkyMiddleware',  # 性能监测
]

PASSWORD_HASHERS = (
    'django.contrib.auth.hashers.MD5PasswordHasher',  # 加密算法
    'django.contrib.auth.hashers.PBKDF2PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher',
    'django.contrib.auth.hashers.BCryptSHA256PasswordHasher',
    'django.contrib.auth.hashers.BCryptPasswordHasher',
    'django.contrib.auth.hashers.SHA1PasswordHasher',
    'django.contrib.auth.hashers.CryptPasswordHasher',
)

ROOT_URLCONF = 'MyHouse.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')]
        ,
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'MyHouse.wsgi.application'

# Database
# https://docs.djangoproject.com/en/2.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql', #设置为mysql数据库
        'NAME': 'MyHouse_cloud',  #mysql数据库名
        'USER': 'root',  #mysql用户名
        'PASSWORD': 'GuoHT990520#2',   #mysql密码
        'HOST': '',  #留空默认为localhost
        'PORT': '',  #留空默认为3306端口
    }
}

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://:guoht990520_2_redis@127.0.0.1:6379/0",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    }
}

SESSION_ENGINE = "django.contrib.sessions.backends.cache"
SESSION_REDIS_ALIAS = "default"

# Password validation
# https://docs.djangoproject.com/en/2.1/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/2.1/topics/i18n/

LANGUAGE_CODE = 'zh-hans'

TIME_ZONE = 'Asia/Shanghai'

USE_I18N = True

USE_L10N = True

USE_TZ = False

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.1/howto/static-files/

# debug=False 设置静态文件的保存目录
STATIC_ROOT = os.path.join(BASE_DIR, 'static')  # debug=False生效
# STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static'), ]  # debug=True生效

STATIC_URL = '/static/'

MEDIA_URL = '/upload_files/'  # 你的media url 在Url显示并没什么关系

MEDIA_ROOT = r"/root/project/var/UpLoadFiles/"

# ckeditor配置
CKEDITOR_JQUERY_URL = 'https://cdn.bootcdn.net/ajax/libs/jquery/2.1.4/jquery.min.js'
CKEDITOR_CONFIGS = {
    'default': {
        'toolbar': 'full',  # 工具栏全部功能
        'extraPlugins': 'codesnippet',
        'height': 500,  # 高度
        'width': 730,  # 宽度
    },
}
# 他的目录相对与media root 就是 media root + CKEDITOR_UPLOAD_PATH 不能写成"/uploads/"
CKEDITOR_UPLOAD_PATH = "admin/ckeditor/"
CKEDITOR_IMAGE_BACKEND = 'pillow'

# silk 性能监测
SILKY_PYTHON_PROFILER = True
# 生成.prof文件，silk产生的程序跟踪记录，详细记录来执行来哪个文件，哪一行，用了多少时间等信息
SILKY_PYTHON_PROFILER_BINARY = True
# .prof文件保存路径（最好不要像我这样设置在项目目录中）
# 如果没有本设置，prof文件将默认保存在MEDIA_ROOT里
SILKY_PYTHON_PROFILER_RESULT_PATH = '/root/project/var/SilkProf'
# 认证需要自己写
SILKY_AUTHENTICATION = True  # User must login
SILKY_AUTHORISATION = True  # User must have permissions  # from django.contrib.auth.models import User as admin
SILKY_PERMISSIONS = lambda user: user.is_superuser

# 邮件配置
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.qq.com'
EMAIL_PORT = 25
EMAIL_HOST_USER = '1622761893@qq.com'
EMAIL_HOST_PASSWORD = 'pwmauvnhdcpkeghj'
EMAIL_USE_TLS = True  # 这里必须是 True，否则发送不成功

# 头像大小限制
PHOTO_SIZE = 3*1024*1024
PHOTO_TYPE = ["png", "jpg", "gif"]

# 后端域
BACKEND_SITE = "http://180.76.174.125:8003"

# MQTT服务器相关
MQTT_SERVER_HOST = "180.76.174.125"
MQTT_SERVER_PORT = 1883
MQTT_USERNAME = "client"
MQTT_PASSWORD = "GuoHT990520#2"
