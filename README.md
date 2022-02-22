# MyHouse智能家居系统

## 环境：
#### 服务器硬件环境： 
- 处理器：Broadcom BCM2711（Cortex A72），4核，1.5GHz  
- 内存：2GB 
- 硬盘空间：32GB 
#### 单片机环境： 
- 单片机：ESP8266-12E NodeMCU 
- 开发环境：Arduino IDE（1.8.19） 
#### 软件环境： 
- 操作系统：Raspberry Pi OS（基于Debian11，linux5.10） 
- 编程语言：Python（3.7.9） 
- Web后端框架：django（2.2.0） 
- 分布式消息队列：Celery（5.1.0） 
- 反向代理服务器：Nginx（1.14.2） 
- Web服务器：Gunicorn（20.1.0） 
- 数据库：MariaDB（10.3） 
- 缓存：Redis（5.0.14） 
- MQTT服务器：Mosquitto（1.5.7） 
- 开发工具：PyCharm、Visual Studio Code 

## 安装：
1. 安装nginx服务器：`sudo apt-get install nginx`
2. 安装MariaDB数据库：`sudo apt-get install mysql-server`
3. 安装python3环境：`sudo apt-get install python3`
4. 安装Redis数据库：`sudo apt-get install redis-server`
5. 安装MQTT服务器（Mosquitto）：`sudo apt-get install mosquitto`
6. 安装web服务器Gunicorn：`pip install gunicorn==20.1.0`
7. 安装Django框架：`pip install django==2.2.0`
8. 安装消息队列celery：`pip install celery==5.1.0`
9. 安装django富文本编辑器：`pip install django-ckeditor==6.1.0`
10. 安装django跨域插件：`pip install django-cors-headers==3.7.0`
11. 安装django定时任务：`pip install django-crontab==0.7.1`
12. 安装redis组件：`pip install redis==3.5.3 django-redis==5.0.0 django-redis-sessions==0.6.2`
13. 安装APM组件：`pip install django-silk==4.2.0`
14. 安装后台管理组件：`pip install django-simpleui`
15. 安装WebSocket支持：`pip install dwebsocket==0.5.12`
16. 安装MQTT组件：`pip install paho-mqtt==1.6.1`
17. 安装django数据库组件：`pip install MySQL-python`
18. 安装其他：`pip install psutil platform requests getpass`


