from django.core.mail import send_mail
from django.http import HttpResponse, JsonResponse
from django.template.defaultfilters import escape
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q
from django.views import View
from django.contrib.auth.hashers import check_password
from UserManagement.models import *
from common import getLoginInfo
from common.login_required import *
from MyHouse import settings
import json

email_body_reg = '''Email 地址验证

        尊敬的用户：

            这封信是由 《MyHouse智能家居》 发送的。

            您收到这封邮件，是由于在 《MyHouse智能家居》 进行了新用户注册，使用了这个邮箱地址。如果您并没有访问过 《MyHouse智能家居》，或没有进行上述操作，请忽略这封邮件。您不需要退订或进行其他进一步的操作。

            注册验证码：  {verify_code}

            请谨慎操作。

            最后，祝您学业有成、工作顺利。

            '''

email_body_change = '''Email 地址验证

        尊敬的用户：

            这封信是由 《MyHouse智能家居》 发送的。

            您收到这封邮件，是由于在 《MyHouse智能家居》 进行了密码找回，使用了这个邮箱地址。如果您并没有访问过 《MyHouse智能家居》，或没有进行上述操作，请忽略这封邮件。您不需要退订或进行其他进一步的操作。

            修改密码验证码：  {verify_code}

            请谨慎操作。

            最后，祝您学业有成、工作顺利。

            '''


# Create your views here.
def test(request):
    return JsonResponse({"state": "ok"}, safe=False)


# 用户注册
class Reg(View):
    def post(self, request):
        """用户注册，需要的数据：用户名，密码，邮箱，验证码，头像"""
        from datetime import datetime, timedelta
        name = request.POST.get("name")
        passwd = request.POST.get("passwd")
        email = request.POST.get("email")
        verify = request.POST.get("verify")
        existed_user = User.objects.filter(Q(name=name) | Q(email=email))  # 用户名、邮箱 是否注册
        if len(existed_user) == 0:
            # 未注册，可以注册
            deadline = datetime.now() - timedelta(0, 60 * 5)
            email_history = EmailVerify.objects.filter(email_addr=email, verify_code=verify, send_time__gt=deadline,
                                                       aim="r")

            if len(email_history) != 0:
                # 如果发送成功，保存发送消息
                user_reg = User.objects.create(name=name, passwd=passwd, email=email, is_active=True)
                print("数据保存成功！")
                return JsonResponse({"state": "ok", "msg": "welcome!"})
            else:
                return JsonResponse({"state": "fail", "msg": "wrong or timeout"})
        else:
            return JsonResponse({"state": 'fail', "msg": "user has existed"}, safe=False)

    def get(self, request):
        """发送验证码，进行邮箱验证"""
        global email_body_reg
        email_title = '来自 《毕业设计》 的验证信息'
        verify_code = create_verify_code()
        email_body = email_body_reg.format(verify_code=verify_code)
        email = request.GET.get("email")
        email_exist = User.objects.filter(email=email)
        if len(email_exist) == 0:
            send_status = send_mail(email_title, email_body, settings.EMAIL_HOST_USER, [email])
            if send_status:
                # 发送成功
                verify = EmailVerify()  # 实例化存储对象
                verify.email_addr = email
                verify.verify_code = verify_code
                verify.aim = "r"
                try:
                    verify.save()
                except Exception as e:
                    print("邮件发送成功，数据存储失败")
                    print(e)
                    return JsonResponse({"state": "fail", "msg": "database save failed"}, safe=False)
                print("send_to:", email, "   verify_code:", verify_code, "邮件发送成功，数据保存完成！")
                return JsonResponse({"state": "ok", "msg": "success"}, safe=False)
            else:
                print("出现问题，邮件状态码：", send_status)
                return JsonResponse({"state": "fail", "msg": "send failed"}, safe=False)
        else:
            print('邮箱被使用，退回！')
            return JsonResponse({"state": "fail", "msg": "email exist"})

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
            response = JsonResponse({"state": "ok", "msg": "user is not active"}, safe=False)
            response.delete_cookie("sessionid")
            return response
        except Exception as e:
            return JsonResponse({"state": "fail", "msg": "error"}, safe=False)

    @method_decorator(login_required)
    def put(self, request):
        """信息修改"""
        pass


# 用户登录
class Log(View):
    def post(self, request):
        """用户登录"""
        name = request.POST.get("name")
        passwd = request.POST.get("passwd")
        is_remember = request.POST.get("is_remember")
        users = User.objects.filter((Q(name=name) | Q(email=name)) & Q(is_active=True))  # 用户输入用户名为用户名或邮箱
        if not len(users):
            # 用户不存在
            return JsonResponse({'state': 'fail', "msg": "user not exist"}, safe=False)
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
                return JsonResponse({"state": "fail", "msg": "password error"}, safe=False)

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
    def post(self, request):
        from datetime import datetime, timedelta
        """修改密码"""
        email = request.POST.get("email")
        verify_code = request.POST.get("verify_code")
        new_passwd = request.POST.get("new_passwd")

        try:
            cur_user = User.objects.get(email=email)
            print(cur_user.email)
        except Exception as e:
            return JsonResponse({"state": "fail", "msg": "user not exist"}, safe=False)
        else:
            deadline = datetime.now() - timedelta(0, 60 * 5)
            verify_check = EmailVerify.objects.filter(email_addr=email, verify_code=verify_code, send_time__gt=deadline,
                                                      aim="c")
            if len(verify_check):
                print(cur_user)
                cur_user.passwd = new_passwd
                try:
                    cur_user.save()
                    print("保存成功！！！")
                    return JsonResponse({"state": "ok", "msg": "ok"}, safe=False)
                except Exception as e:
                    print("密码更改失败", e)
                    return JsonResponse({"state": "fail", "msg": "database save failed"}, safe=False)
            else:
                return JsonResponse({"state": "fail", "msg": "not verified"}, safe=False)

    def get(self, request):
        """邮箱验证"""
        global email_body_change
        email_title = "来自 《毕业设计》 的验证信息"
        verify_code = create_verify_code()
        email_body = email_body_change.format(verify_code=verify_code)
        email = request.GET.get("email")
        email_exist = User.objects.filter(email=email)
        if len(email_exist) != 0:
            send_status = send_mail(email_title, email_body, settings.EMAIL_HOST_USER, [email])
            if send_status:
                # 发送成功
                verify = EmailVerify()  # 实例化存储对象
                verify.email_addr = email
                verify.verify_code = verify_code
                verify.aim = "c"
                try:
                    verify.save()
                except Exception as e:
                    print("邮件发送成功，数据存储失败")
                    print(e)
                    return JsonResponse({"state": "fail", "msg": "database save failed"}, safe=False)
                print("send_to:", email, "   verify_code:", verify_code, "邮件发送成功，数据保存完成！")
                return JsonResponse({"state": "ok", "msg": "success"}, safe=False)
            else:
                print("出现问题，邮件状态码：", send_status)
                return JsonResponse({"state": "fail", "msg": "send failed"}, safe=False)
        else:
            print('邮箱被使用，退回！')
            return JsonResponse({"state": "fail", "msg": "user not exist"}, safe=False)


@login_required
def add_photo(request):
    """用户上传头像"""
    import datetime
    login_info = getLoginInfo.get_login_info(request)
    user_id = login_info["user_id"]  # 获取session中存储的用户信息
    photo_file = request.FILES["photo"]  # 提取文件对象
    file_name_list = photo_file.name.split(".")
    file_type = file_name_list[len(file_name_list) - 1]  # 提取文件类型
    if file_type not in settings.PHOTO_TYPE:  # 文件类型
        return JsonResponse({"state": "fail", "msg": "file type not allowed"}, safe=False)
    elif photo_file.size > settings.PHOTO_SIZE:  # 文件过大
        return JsonResponse({"state": "fail", "msg": "size too large"}, safe=False)

    file_time = datetime.datetime.now().strftime('%Y%m%d%H%M%S%f')  # 基于时间的文件名，避免重复
    file_path = f"head_photo/{file_time}.{file_type}"  # 路径&文件名
    save_file(photo_file, file_path)  # 保存文件
    user = User.objects.get(id=user_id)
    user.head_photo = file_path
    user.save()
    del photo_file
    return JsonResponse({"state": "ok", "msg": {"url": f"{settings.MEDIA_URL}{file_path}"}}, safe=False)


# 获取用户状态
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


# 生成验证码
def create_verify_code():
    """生成6位验证码"""
    from random import randint
    verify_list = []
    for i in range(6):
        verify_list.append(str(randint(0, 9)))
    verify_code = ''.join(verify_list)
    print(verify_code)
    # 返回值为str类型
    return verify_code


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
            return JsonResponse({'state': 'fail', "msg": "user not exist"}, safe=False)
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
                return JsonResponse({"state": "fail", "msg": "password error"}, safe=False)

    def get(self, request):
        """客服登出"""
        request.session.clear()  # .flush()
        request.session.flush()  # .flush()
        response = JsonResponse({"state": "ok", "msg": "logout success"}, safe=False)
        response.delete_cookie("sessionid")
        response.set_cookie("service_is_login", "false")
        return response
