# 此文件中内容为配置中需要修改的敏感信息

# django secret key
SECRET_KEY = ''

# url路径，不能加后'/'，如："http://127.0.0.1"
BACKEND_URL = ""
BACKEND_PORT = ""  

# mysql连接配置
mysql_conn = {
    "db_name":"",
    "user":"",
    "password":"",
    "host":"",
    "port":"",
}

# redis连接配置，redis://:password@ip:port/db
redis_conn = {
    "host": "",
    "port": "",
    "password": "",
}

# MQTT连接配置
mqtt_conn = {
    "MQTT_SERVER_HOST": "",
    "MQTT_SERVER_PORT": 1883,  # 默认1883
    "MQTT_USERNAME": "",
    "MQTT_PASSWORD": "",
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
    "EMAIL_HOST": '',
    "EMAIL_HOST_USER": '',
    "EMAIL_HOST_PASSWORD": '',
}

# 媒体文件存储的绝对路径,eg:"/root/proj/uploadfiles/"
MEDIA_ROOT = r""

# Silk性能监测平台日志存放目录,eg:"/root/proj/silkprof"
SILKY_PYTHON_PROFILER_RESULT_PATH = r''
