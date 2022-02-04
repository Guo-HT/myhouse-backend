import requests
import json
from pprint import pprint

class IpLocQuery:
    def __init__(self, ip) -> None:
        self.url = "https://sp1.baidu.com/8aQDcjqpAAV3otqbppnN2DJv/api.php"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36 Edg/92.0.902.84"
        }
        self.params = {
            "query": ip,
            # "co": '',
            "resource_id": "5809",
            # "t": "1630683021392",
            "ie": "utf8",
            "oe": "gbk",
            # "cb": "op_aladdin_callback",
            "format": "json",
            # "tn": "baidu",
            # "cb": "jQuery1102030039352407967623_1630683007061",
            # "_": "1630683007062"
        }

    def run(self):
        response = requests.get(self.url, params=self.params, headers=self.headers)
        data_str = response.content.decode('gbk')
        data_json = json.loads(data_str)
        try:
            query_ip = data_json['data'][0]['OriginQuery']
            query_location = data_json['data'][0]['location']
            ip2loc = {"success":1, "data": {"ip": query_ip, "location": query_location}, "msg": ""}
            return ip2loc
        except Exception as e:
            return {"success":0, "data": {}, "msg": e}


if __name__ == "__main__":
    while True:
        ip = input("查询ip地址：")
        ipquery = IpLocQuery(ip)
        result = ipquery.run()
        print(result, end="\n\n")
        del ipquery


