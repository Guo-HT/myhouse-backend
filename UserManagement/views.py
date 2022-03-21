from django.core.mail import send_mail
from django.http import HttpResponse, JsonResponse
from django.template.defaultfilters import escape
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from silk.profiling.profiler import silk_profile
from django.db.models import Q
from django.views import View
from django.contrib.auth.hashers import check_password
from UserManagement.models import *
from common import getLoginInfo
from common.login_required import *
from MyHouse import settings
import json
import re
import redis


redis_pool_register = redis.ConnectionPool(host="127.0.0.1", port="6379", db=6, password="guoht990520_2_redis", decode_responses=True)
redis_pool_change = redis.ConnectionPool(host="127.0.0.1", port="6379", db=7, password="guoht990520_2_redis", decode_responses=True)


# Create your views here.
def test(request):
    return JsonResponse({"state": "ok"}, safe=False)


# 生成验证码
def create_verify_code():
    """生成6位验证码"""
    from random import choice
    word_list = ['1','2','3','4','5','6','7','8','9','0','a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z']
    verify_str=""
    for i in range(6):
        verify_str += choice(word_list)
    print(verify_str)
    # 返回值为str类型
    return verify_str


# 用户注册
class Reg(View):
    @silk_profile(name="用户注册")
    def post(self, request):
        """用户注册，需要的数据：用户名，密码，邮箱，验证码，头像"""
        from datetime import datetime, timedelta
        conn_register = redis.Redis(connection_pool=redis_pool_register)  # 建立redis连接
        name = request.POST.get("name")
        passwd = request.POST.get("passwd")
        email = request.POST.get("email")
        verify = request.POST.get("verify")

        name_result = re.match(r"^\w+$", name)
        passwd_result = re.match(r"^(?![a-zA-Z]+$)(?![A-Z0-9]+$)(?![A-Z._~!@#$^&*]+$)(?![a-z0-9]+$)(?![a-z._~!@#$^&*]+$)(?![0-9._~!@#$^&*]+$)[a-zA-Z0-9._~!@#$^&*]{8,}$", passwd)
        email_result = re.match(r"^([A-Za-z0-9_\-\.])+\@([A-Za-z0-9_\-\.])+\.([A-Za-z]{2,4})$", email)
        if  (name_result is None or len(name) <= 8 or passwd_result is None or email_result is None):
            return JsonResponse({"state":"fail", "msg":"format error"}, safe=False, status=403)

        existed_user = User.objects.filter(Q(name=name) | Q(email=email))  # 用户名、邮箱 是否注册
        if len(existed_user) == 0:
            # 未注册，可以注册
            # deadline = datetime.now() - timedelta(0, 60 * 5)
            # email_history = EmailVerify.objects.filter(email_addr=email, verify_code=verify, send_time__gt=deadline,
            #                                            aim="r")
            sended_verify_code_history = conn_register.keys(email+"-*")  # 通过redis取验证信息
            sended_verify_code_list = conn_register.mget(sended_verify_code_history)            
            if verify in sended_verify_code_list:
                # 如果发送成功，保存发送消息
                user_reg = User.objects.create(name=name, passwd=passwd, email=email, is_active=True)
                print("数据保存成功！")
                return JsonResponse({"state": "ok", "msg": "welcome!"})
            else:
                return JsonResponse({"state": "fail", "msg": "wrong or timeout"}, safe=False, status=403)
        else:
            return JsonResponse({"state": 'fail', "msg": "user has existed"}, safe=False, status=403)

    @silk_profile(name="用户注册获取验证码")
    def get(self, request):
        import datetime
        from celery_tasks import email_task
        """发送验证码，进行邮箱验证"""
        conn_register = redis.Redis(connection_pool=redis_pool_register)  # 建立redis连接
        verify_code = create_verify_code()  # 生成验证码
        email = request.GET.get("email")
        email_exist = User.objects.filter(email=email)  # 判断有无注册过
        if len(email_exist) == 0:  # 如果无，则允许发送，注册
            email_task.send_mail_register.delay(email, verify_code)  # 发送给消息队列
            conn_register.set(email+f"-{datetime.datetime.now().strftime('%Y-%m-%d-%H:%M:%S')}", verify_code, ex=60*5)  # 放入redis缓存
            # 发送成功
            verify = EmailVerify()  # 实例化存储对象
            verify.email_addr = email
            verify.verify_code = verify_code
            verify.aim = "r"
            try:
                verify.save()
                return JsonResponse({"state": "ok", "msg": "success"}, safe=False)
            except Exception as e:
                print("邮件发送成功，数据存储失败")
                print(e)
                return JsonResponse({"state": "fail", "msg": "database save failed"}, safe=False, status=500)
        else:
            print('邮箱被使用，退回！')
            return JsonResponse({"state": "fail", "msg": "email exist"}, safe=False, status=403)

    @silk_profile(name="用户注销")
    @method_decorator(login_required)
    def delete(self, request):
        """用户注销"""
        login_info = getLoginInfo.get_login_info(request)
        user_id = login_info['user_id']
        try:
            user = User.objects.get(id=user_id)
            user.is_active = False
            user.save()
            request.session.clear()  # .flush()
            request.session.flush()  # .flush()
            response = JsonResponse({"state": "ok", "msg": "user is not active"}, safe=False, status=403)
            response.delete_cookie("sessionid")
            return response
        except Exception as e:
            return JsonResponse({"state": "fail", "msg": "error"}, safe=False, status=500)

    @silk_profile(name="用户信息修改")
    @method_decorator(login_required)
    def put(self, request):
        """信息修改"""
        pass


# 用户登录
class Log(View):
    @silk_profile(name="用户登录")
    def post(self, request):
        """用户登录"""
        name = request.POST.get("name")
        passwd = request.POST.get("passwd")
        is_remember = request.POST.get("is_remember")

        name_result = re.match(r"(^\w+$)|(^([A-Za-z0-9_\-\.])+\@([A-Za-z0-9_\-\.])+\.([A-Za-z]{2,4}))$", name)
        passwd_result = re.match(r"^(?![a-zA-Z]+$)(?![A-Z0-9]+$)(?![A-Z._~!@#$^&*]+$)(?![a-z0-9]+$)(?![a-z._~!@#$^&*]+$)(?![0-9._~!@#$^&*]+$)[a-zA-Z0-9._~!@#$^&*]{8,}$", passwd)

        if  (name_result is None or passwd_result is None):
            return JsonResponse({"state":"fail", "msg":"format error"}, safe=False, status=403)

        users = User.objects.filter((Q(name=name) | Q(email=name)) & Q(is_active=True))  # 用户输入用户名为用户名或邮箱
        if not len(users):
            # 用户不存在
            return JsonResponse({'state': 'fail', "msg": "user not exist"}, safe=False, status=403)
        elif len(users) >= 1:
            # 理论上不会重复，故数量 ≥1 即可
            try:
                assert check_password(passwd, users[0].passwd)
                request.session['is_login'] = True
                request.session['user_id'] = users[0].id
                request.session['user_name'] = users[0].name
                request.session['user_type'] = "user"
                request.session.set_expiry(value=2 * 7 * 24 * 3600)  # session的过期时间为2周
                response = JsonResponse({"state": "ok", "msg": "login success"})
                response.set_cookie("is_login", "true", expires=2 * 7 * 24 * 3600)
                response.set_cookie("user_type", "user", expires=2 * 7 * 24 * 3600)
                if is_remember == "true":
                    response.set_cookie("user_id", users[0].id, expires=2 * 7 * 24 * 3600)
                    response.set_cookie("user_name", users[0].name, expires=2 * 7 * 24 * 3600)
                    return response
                else:
                    return response  # 登录成功
            except Exception as e:
                print(e)
                return JsonResponse({"state": "fail", "msg": "password error"}, safe=False, status=403)

    @silk_profile(name="用户退出登录")
    def get(self, request):
        """用户登出"""
        request.session.clear()  # .flush()
        request.session.flush()  # .flush()
        response = JsonResponse({"state": "ok", "msg": "logout success"}, safe=False)
        response.delete_cookie("sessionid")
        response.set_cookie("is_login", "false")
        return response


# 修改密码
class ChgPwd(View):
    @silk_profile(name="用户修改密码")
    def post(self, request):
        """修改密码"""
        from datetime import datetime, timedelta

        global redis_pool_change
        conn_change = redis.Redis(connection_pool=redis_pool_change)  # 建立redis连接
        
        email = request.POST.get("email")
        verify_code = request.POST.get("verify_code")
        new_passwd = request.POST.get("new_passwd")

        passwd_result = re.match(r"^(?![a-zA-Z]+$)(?![A-Z0-9]+$)(?![A-Z._~!@#$^&*]+$)(?![a-z0-9]+$)(?![a-z._~!@#$^&*]+$)(?![0-9._~!@#$^&*]+$)[a-zA-Z0-9._~!@#$^&*]{8,}$", new_passwd)
        email_result = re.match(r"^([A-Za-z0-9_\-\.])+\@([A-Za-z0-9_\-\.])+\.([A-Za-z]{2,4})$", email)
        print(passwd_result, email_result)
        if passwd_result is None or email_result is None:
            return JsonResponse({"state":"fail", "msg":"format error"}, safe=False, status=403)

        try:
            cur_user = User.objects.get(email=email)
            print(cur_user.email)
        except Exception as e:
            return JsonResponse({"state": "fail", "msg": "user not exist"}, safe=False, status=403)
        else:
            # deadline = datetime.now() - timedelta(0, 60 * 5)
            # verify_check = EmailVerify.objects.filter(email_addr=email, verify_code=verify_code, send_time__gt=deadline,
            #                                           aim="c")
            sended_verify_code_history = conn_change.keys(email+"-*")
            send_verify_code_list = conn_change.mget(sended_verify_code_history)
            if verify_code in send_verify_code_list:
                print(cur_user)
                cur_user.passwd = new_passwd
                try:
                    cur_user.save()
                    print("保存成功！！！")
                    return JsonResponse({"state": "ok", "msg": "ok"}, safe=False)
                except Exception as e:
                    print("密码更改失败", e)
                    return JsonResponse({"state": "fail", "msg": "database save failed"}, safe=False, status=500)
            else:
                return JsonResponse({"state": "fail", "msg": "not verified"}, safe=False, status=403)

    @silk_profile(name="用户修改密码邮箱验证")
    def get(self, request):
        """邮箱验证"""
        from celery_tasks import email_task
        import datetime

        global redis_pool_change
        conn_change = redis.Redis(connection_pool=redis_pool_change)  # 建立redis连接

        email = request.GET.get("email")
        email_exist = User.objects.filter(email=email)
        if len(email_exist) != 0:
            # 频率限制
            send_history = EmailVerify.objects.filter(email_addr=email).order_by("-send_time")
            time_delta = datetime.datetime.now() - send_history[0].send_time
            if time_delta.seconds < 60:
                return JsonResponse({"state":"fail", "msg":"wait"}, status=403, safe=False)
            verify_code = create_verify_code()
            email_task.send_mail_change_pwd.delay(email, verify_code)
            conn_change.set(email+f"-{datetime.datetime.now().strftime('%Y-%m-%d-%H:%M:%S')}", verify_code, ex=60*5)
            # 发送成功
            verify = EmailVerify()  # 实例化存储对象
            verify.email_addr = email
            verify.verify_code = verify_code
            verify.aim = "c"
            try:
                verify.save()
                return JsonResponse({"state": "ok", "msg": "success"}, safe=False)
            except Exception as e:
                print("邮件发送成功，数据存储失败")
                print(e)
                return JsonResponse({"state": "fail", "msg": "database save failed"}, safe=False, status=500)
        else:
            print('邮箱被使用，退回！')
            return JsonResponse({"state": "fail", "msg": "user not exist"}, safe=False, status=403)


@silk_profile(name="用户头像上传")
@login_required
def add_photo(request):
    """用户上传头像"""
    import datetime
    login_info = getLoginInfo.get_login_info(request)
    user_id = login_info["user_id"]  # 获取session中存储的用户信息
    photo_file = request.FILES["photo"]  # 提取文件对象
    file_name_list = photo_file.name.split(".")
    file_type = file_name_list[len(file_name_list) - 1].lower()  # 提取文件类型，且转小写
    if file_type not in settings.PHOTO_TYPE:  # 文件类型
        return JsonResponse({"state": "fail", "msg": "file type not allowed"}, safe=False, status=403)
    elif photo_file.size > settings.PHOTO_SIZE:  # 文件过大
        return JsonResponse({"state": "fail", "msg": "size too large"}, safe=False, status=403)

    file_time = datetime.datetime.now().strftime('%Y%m%d%H%M%S%f')  # 基于时间的文件名，避免重复
    file_path = f"head_photo/{file_time}.{file_type}"  # 路径&文件名
    save_file(photo_file, file_path)  # 保存文件
    user = User.objects.get(id=user_id)
    user.head_photo = file_path
    user.save()
    del photo_file
    return JsonResponse({"state": "ok", "msg": {"url": f"{settings.MEDIA_URL}{file_path}"}}, safe=False)


# 获取用户状态
@silk_profile(name="获取用户在线状态")
def user_status(request):
    user_info = getLoginInfo.get_login_info(request)
    user_info["media_url"] = settings.MEDIA_URL
    if user_info["is_login"]:
        user = User.objects.get(id=user_info["user_id"])  # 数据库查询
        head_photo = user.head_photo  # 信息提取
        user_info['head_photo'] = str(head_photo)
    else:
        user_info['head_photo'] = None
    return JsonResponse(user_info, safe=False)


# 保存文件
def save_file(file_object, file_path):
    """
    讲用户上传的文件保存到服务器文件系统中
    :param file_object: 文件对象
    :param file_path: 文件相对于MEDIA_ROOT的路径
    :return: None
    """
    # 创建文件
    file_path = f"{settings.MEDIA_ROOT}/{file_path}"
    print(file_path)
    with open(file_path, 'wb') as f:
        # 获取文件上传内容，写入文件
        for content in file_object.chunks():
            f.write(content)


# 获取用户信息
@silk_profile(name="获取用户信息")
@login_required
def get_info(request):
    user_id = request.session["user_id"]
    user = User.objects.get(id=user_id)
    data = {
        "username": user.name,
        "id": user.id,
        "email": user.email,
        "reg_time": user.reg_time.strftime("%Y-%m-%d %H:%M:%S"),
        "photo": str(user.head_photo),
        "media_url": settings.MEDIA_URL,
    }
    return JsonResponse({"state": "ok", "msg": data}, safe=False)


# 客服登录
class ServiceLog(View):
    @silk_profile(name="客服登录")
    @csrf_exempt
    def post(self, request):
        """客服登录"""
        name = request.POST.get("name")
        passwd = request.POST.get("passwd")
        is_remember = request.POST.get("is_remember")
        users = Service.objects.filter((Q(name=name) | Q(email=name)) & Q(is_active=True))  # 用户输入用户名为用户名或邮箱
        print(users)
        if not len(users):
            # 用户不存在
            return JsonResponse({'state': 'fail', "msg": "user not exist"}, safe=False, status=403)
        elif len(users) >= 1:
            # 理论上不会重复，故数量 ≥1 即可
            try:
                assert check_password(passwd, users[0].passwd)
                request.session['is_login'] = True
                request.session['user_id'] = users[0].id
                request.session['user_name'] = users[0].name
                request.session['user_type'] = "service"
                request.session.set_expiry(value=2 * 7 * 24 * 3600)  # session的过期时间为2周
                response = JsonResponse({"state": "ok", "msg": "login success"})
                response.set_cookie("service_is_login", "true", expires=2 * 7 * 24 * 3600)
                response.set_cookie("service_user_type", "service", expires=2 * 7 * 24 * 3600)
                if is_remember == "true":
                    response.set_cookie("service_user_id", users[0].id, expires=2 * 7 * 24 * 3600)
                    response.set_cookie("service_user_name", users[0].name, expires=2 * 7 * 24 * 3600)
                    return response
                else:
                    return response  # 登录成功
            except Exception as e:
                print(e)
                return JsonResponse({"state": "fail", "msg": "password error"}, safe=False, status=403)

    @silk_profile(name="客服登出")
    def get(self, request):
        """客服登出"""
        request.session.clear()  # .flush()
        request.session.flush()  # .flush()
        response = JsonResponse({"state": "ok", "msg": "logout success"}, safe=False)
        response.delete_cookie("sessionid")
        response.set_cookie("service_is_login", "false")
        return response
