def get_login_info(request):
    if request.session.has_key("is_login"):
        is_login = request.session['is_login']
        user_id = request.session["user_id"]
        user_name = request.session['user_name']
        # print(is_login, user_name, user_id)
        return {"is_login": is_login, "user_id": user_id, "user_name": user_name}
    else:
        return {"is_login": False, "user_id": None, "user_name": None}
