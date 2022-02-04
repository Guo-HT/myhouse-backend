from django.http import HttpResponse
from django.utils.deprecation import MiddlewareMixin  # 1.10.x
import redis
import re
import datetime
from common.pc_or_mobile import judge_pc_or_mobile
from common.ip2loc import IpLocQuery

redis_ban_words_con = redis.StrictRedis(host="localhost", port=6379, db=3)
redis_con = redis.StrictRedis(host="localhost", port=6379, db=2)


class IpBan(MiddlewareMixin):

    def process_request(self, request):
        try:
            attack_path = redis_ban_words_con.keys("*")
            attack_path = [i.decode() for i in attack_path]
            if 'HTTP_X_FORWARDED_FOR' in request.META:
                ip = request.META['HTTP_X_FORWARDED_FOR']
            else:
                ip = request.META['REMOTE_ADDR']
            ip_c = re.match(r"(\d+?\.\d+?\.\d+?\.)", ip).group(1)
            path = request.path  # 获取请求路径
            if path == "/robots.txt":
                ua = request.META["HTTP_USER_AGENT"]
                mobile = judge_pc_or_mobile(ua)
                print(f"\n[* robots.txt, {ip}, {'移动端' if mobile else 'PC端'} *]")
                return HttpResponse(
                    """<html><head></head><body><pre style="word-wrap: break-word; white-space: pre-wrap;">User-agent: *<br>Allow: /</pre></body></html>""")

            # 如果访问的ip地址所处望断已被禁止
            if len(redis_con.keys(ip_c + "*")):
                print(f"\n[* ip: {ip} 被禁止访问！ *]")
                return HttpResponse('<h1>您的ip被禁止</h1>')

            # 如果访问路径含有攻击敏感信息
            if len([each for each in attack_path if path.find(each) != -1]):
                ip_query = IpLocQuery(ip)
                loc = ip_query.run()["data"]["location"]
                ban_ip_value = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + '\t' + loc
                redis_con.set(ip, ban_ip_value)
                print(f"\n[** 增加一个禁用ip：{ip} **]")
                return HttpResponse('<h1>您的ip被禁止</h1>')
        except Exception as e:
            print("middleware Error:", e)
