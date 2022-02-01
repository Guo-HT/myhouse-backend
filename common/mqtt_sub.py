import os
import sys
import django

# 第一个参数固定，第二个参数是工程名称.settings
os.environ.setdefault('DJANGO_SETTING_MODULE', 'MyHouse.settings')
django.setup()

from MyHouse import settings
from paho.mqtt import client as mqtt
import threading
from Data.models import *
import time, datetime
import json
import re


# 建立链接后的回调
def on_connect(client, userData, flags, rc):
    print("MQTT connected with result code " + str(rc))
    client.subscribe(topic="esp8266/+/state")
    client.subscribe(topic="esp8266/+/will")


# 收到消息后的回调
def on_message(client, userData, msg):
    # print(msg.topic + " == " + msg.payload.decode())
    ret = re.match(r"^esp8266/(.*?)/(\w*)$", msg.topic)
    machine_mac = ret.group(1)  # 设备mac地址
    machine_func = ret.group(2)  # topic中获取的主题功能：will->上下线, state->状态, ctrl->控制
    payload = msg.payload.decode()
    payload_json = json.loads(payload)
    print(msg.topic, machine_mac, machine_func, payload_json)
    try:
        machine = Machine.objects.get(mac_addr=machine_mac)  # 查看是否存储该设备
    except Exception as e:
        print("新设备")
        new_machine = Machine()
        new_machine.mac_addr = machine_mac
        try:
            new_machine.work_type = payload_json["WORK_TYPE"]
        except:
            pass
        new_machine.save()
        return
    else:
        # print("已知设备")
        if machine_func == "state" and machine.user_belong is not None:
            # print("已知设备，已绑定用户")
            machine_data = MachineData()
            machine_data.machine = machine
            machine_data.data = payload
            machine_data.upload_time = datetime.datetime.strptime(payload_json["time"], "%Y-%m-%d %H:%M:%S")
            machine_data.save()
            machine.is_online = True
            machine.save()
        elif machine_func == "will":
            # print("遗嘱功能")
            if payload_json["state"] == "CLIENT-OFFLINE":
                machine.is_online = False
                machine.work_type = payload_json["WORK_TYPE"]
                machine.save()

            elif payload_json["state"] == "CLIENT-ONLINE":
                machine.is_online = True
                machine.work_type = payload_json["WORK_TYPE"]
                machine.save()


# 订阅成功后的回调
def on_subscribe(client, userData, mid, QoS):
    print(mid, QoS)


# # 链接失败后的回调
# def on_connect_fail(client, userData):
#     print(userData)


def mqtt_function():
    global client
    client.loop_forever()


client = mqtt.Client(client_id="django_backend_server_pc_sub", clean_session=False)


# 链接mqtt服务器
def connect_mqtt_server():
    global client
    print("正在连接 MQTT Mosquitto 服务器")
    client.on_connect = on_connect  # 链接成功的回调
    client.on_message = on_message  # 收到消息的回调
    client.on_subscribe = on_subscribe  # 订阅成功的回调
    # client.on_connect_fail = on_connect_fail  # 链接失败的回调
    client.username_pw_set(settings.MQTT_USERNAME, settings.MQTT_PASSWORD)  # 用户名、密码
    client.connect(settings.MQTT_SERVER_HOST, settings.MQTT_SERVER_PORT, 60)  # 建立链接

    mqtt_thread = threading.Thread(target=mqtt_function)
    mqtt_thread.start()
