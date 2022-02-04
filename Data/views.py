from django.http import HttpResponse, JsonResponse, QueryDict
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from dwebsocket.decorators import accept_websocket
from Data.models import *
from UserManagement.models import *
from paho.mqtt import client as mqtt
from MyHouse import settings
from common.login_required import *
from common.get_ip import *
import json
import time
import redis

link_count_each_page = 2


# Create your views here.
def test(request):
    return JsonResponse({"state": "OK"}, safe=False)


class Machines(View):
    @method_decorator(login_required)
    def post(self, request):
        """绑定设备"""
        user_id = request.session["user_id"]  # 登录用户id
        sn = request.POST.get("sn")  # sn码，暂时为mac地址
        work_type = request.POST.get("work_type")
        machine_name = request.POST.get("machine_name")

        if machine_name is None:
            return JsonResponse({"state": "fail", "msg": "need machine_name"}, safe=False, status=500)

        try:
            machine = Machine.objects.get(mac_addr=sn.upper())
            if machine.user_belong_id is not None and machine.user_belong_id != user_id:
                return JsonResponse({"state": "fail", "msg": "belong to else"}, safe=False)
            elif machine.user_belong_id == user_id:
                return JsonResponse({"state": "fail", "msg": "already bind"}, safe=False)
            elif machine.work_type == work_type:
                machine.user_belong_id = user_id
                machine.machine_name = machine_name
                machine.save()
                return JsonResponse({"state": "ok", "msg": "ok"}, safe=False)
            else:
                return JsonResponse({"state": "fail", "msg": "type not ok"}, safe=False)
        except Exception as e:
            return JsonResponse({"state": "fail", "msg": "machine not exist"}, safe=False)

    @method_decorator(login_required)
    def get(self, request):
        user_id = request.session["user_id"]
        machine_list = Machine.objects.filter(user_belong_id=user_id)

        data_list = []
        for each in machine_list:
            data = dict()
            data['id'] = each.id
            data['sn'] = each.mac_addr
            data['is_online'] = each.is_online
            data['work_type'] = each.work_type
            data['machine_name'] = each.machine_name
            data_list.append(data)

        return JsonResponse({"state": "ok", "msg": data_list}, safe=False)


@login_required
def cut_bind(request):
    machine_id = request.POST.get("id")
    machine_type = request.POST.get("type")
    machine = Machine.objects.get(id=machine_id)
    if machine.work_type != machine_type:
        return JsonResponse({"state": "fail", "msg": "type error"}, safe=False)
    else:
        machine.user_belong = None
        machine.save()
        return JsonResponse({"state": "ok", "msg": "ok"}, safe=False)


@login_required
def status(request):
    user_id = request.session["user_id"]
    machine_list = Machine.objects.filter(user_belong_id=user_id)
    data = dict()
    for each in machine_list:
        data[each.id] = each.is_online
    return JsonResponse({"state": "ok", "msg": data}, safe=False)


@csrf_exempt
@login_required
def get_data(request):
    import json
    user_id = request.session["user_id"]
    machine_type = request.GET.get("type")
    machine_id = request.GET.get("id")

    recent_data = MachineData.objects.filter(machine_id=machine_id, machine__work_type=machine_type).order_by(
        "-upload_time")
    if len(recent_data) == 0:
        return JsonResponse({"state": "ok", "msg": "no data"}, safe=False)
    else:
        data_list = [json.loads(each.data) for each in recent_data[0:20]]

    return JsonResponse({"state": "ok", "msg": data_list}, safe=False)


@login_required
def get_machines_data(request):
    import json
    user_id = request.session["user_id"]
    machine_list = Machine.objects.filter(user_belong_id=user_id)
    data_list = []
    for each in machine_list:
        last_data = MachineData.objects.filter(machine_id=each.id).order_by("-upload_time")
        each_data = dict()
        each_data["id"] = each.id
        each_data['work_type'] = each.work_type
        each_data["name"] = each.machine_name
        if len(last_data) == 0:
            each_data["last_data"] = None
        else:
            each_data["last_data"] = json.loads(last_data[0].data)
        data_list.append(each_data)
    return JsonResponse({"state": "ok", "msg": data_list}, safe=False)


@login_required
def get_command_history(request):
    machine_type = request.GET.get("type")
    machine_id = request.GET.get("id")

    command_history = CommandHistory.objects.filter(machine_id=machine_id, machine__work_type=machine_type).order_by(
        "-time")[0:20]
    command_list = [{"command": each.command, "time": str(each.time)} for each in command_history]
    return JsonResponse({"state": "ok", "msg": command_list}, safe=False)


# 给设备发送指令
@login_required
def mqtt_ctrl(request):
    command = request.POST.get("command")
    machine_id = request.POST.get("id")
    machine_type = request.POST.get("type")
    # print(command, machine_id, machine_type)
    client = mqtt.Client("django_backend_server_pc_pub", clean_session=False)
    client.on_connect = on_connect
    client.on_message = on_message
    client.on_disconnect = on_disconnect
    connect_mqtt_server(client)
    machine = Machine.objects.get(id=machine_id, work_type=machine_type)
    if machine.is_online:
        client.publish(topic=f"esp8266/{machine.mac_addr}/ctrl", payload=command, qos=1, retain=False)
        CommandHistory.objects.create(machine_id=machine_id, command=command)
        client.disconnect()
        return JsonResponse({"state": "ok", "msg": "ok"}, safe=False)
    else:
        return JsonResponse({"state": "fail", "msg": "offline"}, safe=False)


# 以下是即时通信
online_user = set()
online_service = set()
redis_pool_from_user = redis.ConnectionPool(host="127.0.0.1", port="6379", db=4, decode_responses=False)
redis_pool_from_service = redis.ConnectionPool(host="127.0.0.1", port="6379", db=5, decode_responses=False)


@login_required
def chat_file(request):
    import time

    conn_from_user = redis.Redis(connection_pool=redis_pool_from_user)  # 连接redis
    conn_from_service = redis.Redis(connection_pool=redis_pool_from_service)  # 连接redis

    user_id = request.session["user_id"]
    user_name = request.session["user_name"]
    user_type = request.session["user_type"]
    send_time = request.POST.get("time")
    to = request.POST.get("to")
    file_type = request.POST.get("type")
    file = request.FILES["chat_file"]
    file_time = time.strftime("%Y%m%d%H%M%S", time.localtime())
    file_name = f"{file_time}_{file.name}"
    file_path = settings.MEDIA_ROOT + "chat_file/" + file_name
    file_url = f"{settings.MEDIA_URL}chat_file/{file_name}"
    print(file_path)
    print(file_url)
    try:
        with open(file_path, "wb+") as f:
            for chunk in file.chunks():
                f.write(chunk)
        # 发送方用户名、发送方id、发送时间、发送内容、头像url
        msg_redis = {
            "from_id": user_id,
            "from_name": user_name,
            "time": send_time,
            # "file_name": file_name,
            "text": file_url,
            "to": to,
            "type": file_type,
        }
        msg_send = msg_redis
        # conn.hmset(str(time.time()), msg_redis)  # 写入redis
        # ChatHistory.objects.create(time=msg_redis["time"], from_user_id=msg_redis["from_id"], text=msg_redis["text"], to_user_id=msg_redis["to"], content_type=msg_redis["type"])
        if user_type == 'user':
            conn_from_user.hmset(str(time.time()), msg_redis)  # 写入redis
            ChatHistory.objects.create(time=msg_redis["time"], user_id=msg_redis["from_id"],
                                       text=msg_redis["text"], service_id=msg_redis["to"],
                                       content_type=msg_redis["type"], from_type=user_type)
        elif user_type == "service":
            conn_from_service.hmset(str(time.time()), msg_redis)  # 写入redis
            ChatHistory.objects.create(time=msg_redis["time"], user_id=msg_redis["to"],
                                       text=msg_redis["text"], service_id=msg_redis["from_id"],
                                       content_type=msg_redis["type"], from_type=user_type)
        msg_send["file_name"] = file_name
        return JsonResponse({"state": "ok", "msg": msg_send}, safe=False)
    except Exception as e:
        print(e)
        print(e.__traceback__.tb_lineno)
        return JsonResponse({"state": "fail", "msg": "fail"}, safe=False)


@login_required
@accept_websocket
def wstest(request):
    global redis_pool_from_service
    global redis_pool_from_user
    global online_user
    global online_service

    conn_from_user = redis.Redis(connection_pool=redis_pool_from_user)
    conn_from_service = redis.Redis(connection_pool=redis_pool_from_service)

    user_id = request.session["user_id"]
    user_type = request.session["user_type"]
    user = ''
    username = ''
    if user_type == "user":
        user = User.objects.get(id=user_id)
        username = user.name
        print('用户', username, "上线")
        online_user.add(user_id)
    elif user_type == "service":
        user = Service.objects.get(id=user_id)
        username = user.name
        print('客服', username, "上线")
        online_service.add(user_id)

    if request.is_websocket():
        print("websocket connecting……")
        try:
            while True:
                msg = request.websocket.read()
                try:  # 接收到消息
                    # recv_msg = msg.decode()
                    recv_msg = msg
                    recv_dict = json.loads(recv_msg)
                    recv_dict["from_id"] = user_id
                    recv_dict["from_name"] = username
                    str_new = ""
                    for i in recv_dict["text"]:
                        if i in ["\n", "\a", "\b", "\v", "\t", "\r", "\f"]:
                            str_new += "<br>"
                        else:
                            str_new += i
                    recv_dict["text"] = str_new
                    print(type(recv_dict), recv_dict, type(recv_dict["from_id"]), recv_dict["from_id"])
                    if user_type == 'user':
                        conn_from_user.hmset(str(time.time()), recv_dict)  # 写入redis
                        ChatHistory.objects.create(time=recv_dict["time"], user_id=recv_dict["from_id"],
                                                   text=recv_dict["text"], service_id=recv_dict["to"],
                                                   content_type=recv_dict["type"], from_type=user_type)
                    elif user_type == "service":
                        conn_from_service.hmset(str(time.time()), recv_dict)  # 写入redis
                        ChatHistory.objects.create(time=recv_dict["time"], user_id=recv_dict["to"],
                                                   text=recv_dict["text"], service_id=recv_dict["from_id"],
                                                   content_type=recv_dict["type"], from_type=user_type)
                except Exception as e:  # 未接收到消息
                    # print(e)
                    # print(e.__traceback__.tb_lineno)
                    pass
                finally:
                    if user_type == 'user':  # 当前是用户
                        recv = conn_from_service.keys("*")  # 提取库中所有键值对
                        print("用户:", online_user)
                        print(recv)
                        for obj_name in recv:  # 便利
                            obj = conn_from_service.hgetall(obj_name)
                            if obj[b"to"].decode() == str(user_id):
                                # 发送方用户名、发送方id、发送时间、发送内容、头像url
                                send_data = b'{"name": "' + obj[b"from_name"] + b'", "id": "' + obj[
                                    b"from_id"] + b'", "time": "' + obj[b"time"] + b'", "content": "' + obj[
                                                b"text"] + b'", "head": "' + "head_photo/default-head.png".encode() + b'", "media_url": "' + settings.MEDIA_URL.encode() + b'", "type": "' + \
                                            obj[b"type"] + b'"}'
                                print(send_data)
                                request.websocket.send(send_data)
                                conn_from_service.delete(obj_name)
                    elif user_type == "service":  # 当前是客服
                        recv = conn_from_user.keys("*")  # 提取库中所有键值对
                        print("客服:", online_service)
                        print(recv)
                        for obj_name in recv:  # 便利
                            obj = conn_from_user.hgetall(obj_name)
                            if obj[b"to"].decode() == str(user_id):
                                # 发送方用户名、发送方id、发送时间、发送内容、头像url
                                send_data = b'{"name": "' + obj[b"from_name"] + b'", "id": "' + obj[
                                    b"from_id"] + b'", "time": "' + obj[b"time"] + b'", "content": "' + obj[
                                                b"text"] + b'", "head": "' + str(User.objects.get(id=obj[
                                    b"from_id"]).head_photo).encode() + b'", "media_url": "' + settings.MEDIA_URL.encode() + b'", "type": "' + \
                                            obj[b"type"] + b'"}'
                                print(send_data)
                                request.websocket.send(send_data)
                                conn_from_user.delete(obj_name)
                    time.sleep(1)
        except Exception as e:
            print(e)
            print(e.__traceback__.tb_lineno)
            if user_type == "user":
                online_user.discard(username)
            elif user_type == "service":
                online_service.discard(username)
            request.websocket.close()
            print("关闭连接")


@login_required
def get_chat_history(request):
    user_id = request.session["user_id"]
    user_type = request.session["user_type"]
    history = []
    if user_type == "user":
        history = ChatHistory.objects.filter(user_id=user_id).order_by("-time")[0:20]
        data = []
        for each in history:
            each_his = dict()
            each_his["time"] = each.time
            each_his["content"] = each.text
            each_his["content_type"] = each.content_type
            if each.from_type == "user":
                each_his["type"] = "send"
                each_his["media_url"] = settings.MEDIA_URL
                each_his["head"] = str(each.user.head_photo)
            elif each.from_type == "service":
                each_his["type"] = "recv"
            data.append(each_his)
        return JsonResponse({"state": "ok", "msg": data}, safe=False)

    elif user_type == "service":
        history = ChatHistory.objects.filter(service_id=user_id).order_by("-time")[0:20]
        data = dict()
        for each in history:
            user_id = each.user.id
            if user_id not in data.keys():  # 已经有了这个用户的其他记录：
                data[user_id] = {"head": str(each.user.head_photo), "name": each.user.name,
                                 "media_url": settings.MEDIA_URL, "his": []}
            each_his = dict()
            each_his["time"] = each.time
            each_his["content"] = each.text
            each_his["content_type"] = each.content_type

            if each.from_type == "user":
                each_his["type"] = "recv"
            elif each.from_type == "service":
                each_his["type"] = "send"
            data[user_id]["his"].append(each_his)
        return JsonResponse({"state": "ok", "msg": data}, safe=False)


class GetMachineLink(View):
    @method_decorator(login_required)
    def post(self, request):
        upper_machine_id = request.POST.get("upper_machine_id")
        condition = request.POST.get("condition")
        data_item = request.POST.get("data_item")
        condition_num = request.POST.get("condition_num")
        lower_machine_id = request.POST.get("lower_machine_id")
        command = request.POST.get("command")
        command_num = request.POST.get("command_num")

        print(upper_machine_id, condition, data_item, condition_num, lower_machine_id, command, command_num)
        MachineLink.objects.create(upper_id=upper_machine_id, lower_id=lower_machine_id,
                                   data_item=data_item, condition=condition, condition_num=condition_num,
                                   command=command, command_num=command_num)
        return JsonResponse({"state": "ok", "msg": "msg"}, safe=False)

    @method_decorator(login_required)
    def get(self, request):
        from django.core.paginator import Paginator

        page = request.GET.get("page")
        user_id = request.session['user_id']
        machine_links = MachineLink.objects.filter(upper__user_belong_id=user_id).order_by("-id")

        paginator = Paginator(machine_links, link_count_each_page)
        page_num = paginator.num_pages  # 总页数
        page_list = paginator.page_range  # 页码列表

        try:
            machine_links_page = paginator.page(page).object_list
        except Exception as e:
            return JsonResponse({"state": "fail", "msg": "out of range"}, safe=False, status=500)

        link_list = []
        for each_link in machine_links_page:
            each_dict = dict()
            each_dict["link_id"] = each_link.id
            each_dict["upper_id"] = each_link.upper.id
            each_dict["upper_name"] = each_link.upper.machine_name
            each_dict["lower_id"] = each_link.lower.id
            each_dict["lower_name"] = each_link.lower.machine_name
            each_dict["data_item"] = each_link.data_item
            each_dict["condition"] = each_link.condition
            each_dict["condition_num"] = each_link.condition_num
            each_dict["command"] = each_link.command
            each_dict["command_num"] = each_link.command_num
            link_list.append(each_dict)
        return JsonResponse({"state": "ok", "msg": link_list, "page_num": page_num, "total_count": len(machine_links),
                             "per_page": link_count_each_page}, safe=False)

    @method_decorator(login_required)
    def delete(self, request):
        DELETE = QueryDict(request.body)
        link_id = DELETE.get('link_id')
        MachineLink.objects.get(id=link_id).delete()
        return JsonResponse({"state": "ok", "msg": link_id})

# ############## MQTT操作 ##################
def connect_mqtt_server(client):
    client.username_pw_set(settings.MQTT_USERNAME, settings.MQTT_PASSWORD)
    client.connect(settings.MQTT_SERVER_HOST, settings.MQTT_SERVER_PORT, 60)
    # client.loop_start()


def on_connect(client, userData, flags, rc):
    print("Connected with result code " + str(rc))
    client.subscribe(topic="esp8266-mqtt-test-ledState-E8:DB:84:9D:23:A3")


def on_message(client, userData, msg):
    print(msg.topic + " == " + str(msg.payload))


def on_disconnect(client, userData, rc):
    print("MQTT控制 断开连接")
