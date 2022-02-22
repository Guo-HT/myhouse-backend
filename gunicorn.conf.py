import logging
import logging.handlers
from logging.handlers import WatchedFileHandler
import os
import multiprocessing

bind = "0.0.0.0:8005"   #绑定的ip与端口
backlog = 512                #监听队列数量，64-2048
daemon='true'
chdir = '/home/pi/Code/Django_proj/MyHouse_Backend/'  #gunicorn要切换到的目的工作目录
worker_class = 'sync' #使用gevent模式，还可以使用sync 模式，默认的是sync模式
workers = 4  # multiprocessing.cpu_count()    #进程数
threads = 4  # multiprocessing.cpu_count()*4 #指定每个进程开启的线程数
loglevel = 'info' #日志级别，这个日志级别指的是错误日志的级别，而访问日志的级别无法设置

# access_log_format = '%(t)s %(p)s %(h)s "%(r)s" %(s)s %(L)s %(b)s %(f)s" "%(a)s"'  # 默认
accesslog = "/home/pi/Code/Django_proj/MyHouse_Backend/gunicorn_access.log"      #访问日志文件
access_log_format = '%(t)s %(p)s "%({X-Real-IP}i)s" "%(r)s" %(s)s %(L)s %(b)s "%(f)s" "%(a)s"'

errorlog = "/home/pi/Code/Django_proj/MyHouse_Backend/gunicorn_error.log"        #错误日志文件
# accesslog = "-"  #访问日志文件，"-" 表示标准输出
# errorlog = "-"   #错误日志文件，"-" 表示标准输出

pidfile = '/home/pi/Code/Django_proj/MyHouse_Backend/gunicorn.pid'
proc_name = 'MyHouse_api'   #进程名
