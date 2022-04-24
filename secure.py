# 此文件中内容为配置中需要修改的敏感信息

# django secret key
SECRET_KEY = 'g)b=1h!@5tl0ar()@3#crta6@5zmz0*@q$59hwra&z_6+fd%vb'

# url路径，不能加后'/'
BACKEND_URL = "http://180.76.174.125"
BACKEND_PORT = "8003"  

# mysql连接配置
mysql_conn = {
    "db_name":"MyHouse_cloud",
    "user":"root",
    "password":"GuoHT990520#2",
    "host":"127.0.0.1",
    "port":"3306",
}

# redis连接配置，eg: redis://:password@ip:port/db
redis_conn = {
    "host": "127.0.0.1",
    "port": "6379",
    "password": "guoht990520_2_redis",
}

# MQTT连接配置
mqtt_conn = {
    "MQTT_SERVER_HOST": "180.76.174.125",
    "MQTT_SERVER_PORT": 1883,
    "MQTT_USERNAME": "client",
    "MQTT_PASSWORD": "GuoHT990520#2",
}

essay_count = {
    # 文章列表，一页几个
    "essay_count_each_search_page": 5,

    # 文章推荐，一栏几个
    "essay_link_each_recommend": 10,
    
    # 文章评论，一页几个
    "comment_each_page": 2,

    # 个人主页，历史记录，一页几个
    "personal_info_count_per_page": 12,
}

# 邮件服务器配置
email_setting = {
    "EMAIL_HOST": 'smtp.qq.com',
    "EMAIL_HOST_USER": '1622761893@qq.com',
    "EMAIL_HOST_PASSWORD": 'pwmauvnhdcpkeghj',
}

# 媒体文件存储的绝对路径
MEDIA_ROOT = r"/root/project/var/UpLoadFiles/"

# Silk性能监测平台日志存放目录
SILKY_PYTHON_PROFILER_RESULT_PATH = r'/root/project/var/SilkProf'