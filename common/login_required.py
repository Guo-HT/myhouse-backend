from django.http import JsonResponse


def login_required(view_func):
    def wrapper(requests, *view_args, **kwargs):
        # 判断用户是否登录
        if requests.session.has_key('is_login'):
            # 已登录，调用对应视图
            return view_func(requests, *view_args, **kwargs)
        else:
            # 未登录，调转到登录页
            return JsonResponse({"state": "fail", "msg": "jump to login"}, safe=False, status=403)

    return wrapper