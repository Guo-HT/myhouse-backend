from django.utils.deprecation import MiddlewareMixin
from django.http import HttpResponse,JsonResponse, QueryDict
from Data.models import BanIp as ban_ip_model
import redis
import re
import datetime


# 建立redis连接池
redis_pool_ban_words = redis.ConnectionPool(host="127.0.0.1", port="6379", db=3, password="guoht990520_2_redis", decode_responses=False)
redis_pool_ban_ip = redis.ConnectionPool(host="127.0.0.1", port="6379", db=2, password="guoht990520_2_redis", decode_responses=False)

class BanIp(MiddlewareMixin):
    def process_request(self, request):
        global redis_pool_ban_ip
        global redis_pool_ban_words
        # 建立连接
        ban_words_con = redis.Redis(connection_pool=redis_pool_ban_words)  # 连接redis
        ban_ip_con = redis.Redis(connection_pool=redis_pool_ban_ip)  # 连接redis
        
        # 获取敏感路径词汇
        attack_path = ban_words_con.keys("*") 
        attack_path = [i.decode() for i in attack_path]
        
        # 获取源ip
        if 'HTTP_X_FORWARDED_FOR' in  request.META:
            ip =  request.META['HTTP_X_FORWARDED_FOR']
        else:
            ip = request.META['REMOTE_ADDR']
        ip_c = re.match(r"(\d+?\.\d+?\.\d+?\.)", ip).group(1)
        
        # 如果访问的ip地址所处望断已被禁止
        if len(ban_ip_con.keys(ip_c+"*")):
            # print(f"\n[* ip: {ip} 被禁止访问！ *]")
            return JsonResponse({'state': "fail", "msg":"ban"}, status=403, safe=False)
        
        # 获取请求路径
        path = request.path
        
        # 获取请求参数
        request_args_head = request.META['QUERY_STRING']
        request_args_body = request.body.decode(errors="ignore")
        # request_args = request_args_head + '\r\n\r\n' + request_args_body
        request_args = request_args_body
        if len([each for each in attack_path if request_args.find(each)!=-1]):
            # print("敏感")
            banip_value = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            ban_ip_con.set(ip, banip_value, ex=60)
            # 查看数据库种有无禁用记录，没有则新建
            banned = ban_ip_model.objects.filter(ip_addr=ip).first()
            if banned:
                banned.times += 1
                banned.save()
            else:
                banned = ban_ip_model.objects.create(ip_addr=ip, times=1)
            return JsonResponse({'state': "fail", "msg":"query string error"}, status=403, safe=False)
