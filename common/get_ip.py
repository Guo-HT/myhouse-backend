def get_ip(request):
    # 获取ip地址
    if 'HTTP_X_FORWARDED_FOR' in  request.META:
        ip =  request.META['HTTP_X_FORWARDED_FOR']
    else:
        ip = request.META['REMOTE_ADDR']
    return ip