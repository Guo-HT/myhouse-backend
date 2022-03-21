from django.http import JsonResponse, Http404, QueryDict
from django.template.defaultfilters import escape
from django.db.models import Q
from django.utils.decorators import method_decorator
from django.views import View
from django.contrib.auth.hashers import check_password
from django.views.decorators.csrf import csrf_exempt
from silk.profiling.profiler import silk_profile
from Essay.models import *
from MyHouse import settings
from common.login_required import *
from common.get_ip import *

essay_count_each_search_page = 6

essay_link_each_recommend = 10

comment_each_page = 2

personal_info_count_per_page = 12


# Create your views here.
def test(request):
    return JsonResponse({"state": "OK"}, safe=False, status=302)


class EssayDetail(View):
    @silk_profile(name="文章上传")
    @method_decorator(login_required)  # 类视图装饰器
    def post(self, request):
        """上传文章"""
        from common import getLoginInfo
        title = request.POST.get("title")
        content = request.POST.get("content")
        login_info = getLoginInfo.get_login_info(request)
        user_id = login_info["user_id"]
        user = User.objects.get(id=user_id)
        Essay.objects.create(title=title, content=content, user=user)
        return JsonResponse({"state": "ok", "msg": "get"}, safe=False)

    @silk_profile(name="获取某篇文章")
    def get(self, request):
        """获取某篇文章"""
        essay_id = request.GET.get("id")
        try:
            essay = Essay.objects.get(id=essay_id, is_checked=True, is_delete=False)
        except Exception as e:
            print(e)
            return JsonResponse({"state": "fail", "msg": "not found"}, safe=False, status=404)
        else:
            ip = get_ip(request)
            if request.session.has_key("is_login"):
                user_id = request.session["user_id"]
                # 获取历史记录列表
                history_list = BrowseHistory.objects.filter(user_id=user_id).order_by("-time")
                try:
                    assert len(history_list) != 0  # 断言，历史记录不为空
                    if str(history_list[0].essay.id) != essay_id:
                        BrowseHistory.objects.create(user_id=user_id, essay_id=essay_id, ip=ip)
                    elif str(history_list[0].essay_id) == essay_id:
                        # last_history.update("time", now)  # 修改历史记录时间
                        pass
                except Exception as e:
                    # 没有历史记录,则创建历史记录
                    BrowseHistory.objects.create(user_id=user_id, essay_id=essay_id, ip=ip)

                try:
                    collection = EssayCollection.objects.get(user_id=user_id, essay_id=essay_id)
                except Exception as e:
                    is_collect = 'false'
                else:
                    is_collect = 'true'
            else:
                print("没登陆")
                BrowseHistory.objects.create(essay_id=essay_id, ip=ip)
                is_collect = 'false'
            title = essay.title
            content = essay.content
            user = essay.user.name
            create_time = essay.create_time.strftime('%Y-%m-%d %H:%M:%S')
            watch_num = essay.watch_num
            good_num = len(GoodList.objects.filter(essay_id=essay_id))
            essay.watch_num = watch_num + 1
            essay.save()
            comment_num = len(EssayComment.objects.filter(from_essay_id=essay_id))
            data = {
                "title": escape(title),
                "content": content,
                "user": user,
                "create_time": create_time,
                "watch_num": watch_num + 1,
                "good_num": good_num,
                "comment_num": comment_num,
                "is_collect": is_collect,
            }
            return JsonResponse({"state": "ok", "msg": data}, safe=False)

    @silk_profile(name="删除发布的文章")
    @method_decorator(login_required)
    def delete(self, request):
        user_id = request.session["user_id"]
        _delete = QueryDict(request.body)
        essay_id = _delete.get('essay_id')
        print(user_id, essay_id)
        this_essaies = Essay.objects.filter(user_id=user_id, id=essay_id, is_delete=False, is_checked=True)
        if len(this_essaies):
            this_essay = this_essaies[0]
            this_essay.is_delete=True
            this_essay.save()
            return JsonResponse({"state": "ok", "msg": "is delete"}, safe=False)
        else:
            return JsonResponse({"state": "fail", "msg": "not found"}, safe=False, status=404)


# 接受富文本编辑器的图片
@csrf_exempt
@silk_profile(name="富文本异步上传")
@login_required
def richtext_upload(request):
    import time
    if request.method == 'POST':
        callback = request.POST.get('CKEditorFuncNum')
        file_name = ''
        file_time = ''
        f = request.FILES["upload"]
        try:
            file_time = time.strftime("%Y%m%d%H%M%S", time.localtime())
            path = settings.MEDIA_ROOT + 'ckeditor/' + file_time

            file_name = path + "_" + f.name
            with open(file_name, "wb+") as des_origin_f:
                for chunk in f.chunks():
                    des_origin_f.write(chunk)
        except Exception as e:
            print(e)
        try:
            response_data = {
                "uploaded": 1,
                "fileName": f"{file_time}_{f.name}",
                "url": f"{settings.BACKEND_SITE}{settings.MEDIA_URL}ckeditor/{file_time}_{f.name}"
            }
            return JsonResponse(response_data, safe=False)
        except Exception as e:
            print(e)
            return JsonResponse({"uploaded": 0, "error": {"message": e}}, safe=False)
    else:
        raise Http404()


# 获取主页、详情页（热门、近期）的推荐列表
@silk_profile(name="获取文章列表")
def get_list(request):
    import re
    from django.core.paginator import Paginator
    global essay_count_each_search_page
    from datetime import datetime, timedelta
    from django.db import connection
    list_for = request.GET.get("list_for")
    reg = re.compile('<[^>]*>')
    if list_for == "index":
        # 获取主页列表（top 5）
        recent_five = Essay.objects.filter(is_checked=True, is_delete=False).order_by("-create_time")[0:5]
        data_list = []
        for each in recent_five:
            each_data = dict()
            each_data["id"] = each.id
            each_data["title"] = escape(each.title)
            each_data["content"] = escape(reg.sub('', each.content).replace('\n', '').replace(' ', '')[0:50])
            each_data["user"] = each.user.name
            each_data["create_time"] = each.create_time.strftime('%Y-%m-%d %H:%M:%S')
            each_data["watch_num"] = each.watch_num
            data_list.append(each_data)
        send_data = {"state": "ok", "msg": data_list}
        return JsonResponse(send_data, safe=False)
    if list_for == "recent":
        # 获取主页列表（top 5）
        recent_five = Essay.objects.filter(is_checked=True, is_delete=False).order_by("-create_time")[0:essay_link_each_recommend]
        data_list = []
        for each in recent_five:
            each_data = dict()
            each_data["id"] = each.id
            each_data["title"] = escape(each.title)
            each_data["content"] = escape(reg.sub('', each.content).replace('\n', '').replace(' ', '')[0:50])
            each_data["user"] = each.user.name
            each_data["create_time"] = each.create_time.strftime('%Y-%m-%d %H:%M:%S')
            each_data["watch_num"] = each.watch_num
            data_list.append(each_data)
        send_data = {"state": "ok", "msg": data_list}
        return JsonResponse(send_data, safe=False)
    if list_for == "hot":
        # 获取一天内浏览最多列表（top 5）
        deadline = datetime.now() - timedelta(0, 60 * 60 * 24)
        # hot_five = BrowseHistory.objects.filter(time__gt=deadline).aggregate  # 一天内浏览的
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT essay_id,  count(*) as count FROM essay_browse_history GROUP BY essay_id ORDER BY count DESC;")
            hot_five = cursor.fetchall()[0:essay_link_each_recommend]
        hot_five_essay_id = [i[0] for i in hot_five]
        data_list = []
        for each in hot_five_essay_id:
            each = Essay.objects.get(id=each, is_checked=True, is_delete=False)
            each_data = dict()
            each_data["id"] = each.id
            each_data["title"] = each.title
            each_data["content"] = escape(reg.sub('', each.content).replace('\n', '').replace(' ', '')[0:50])
            each_data["user"] = each.user.name
            each_data["create_time"] = each.create_time.strftime('%Y-%m-%d %H:%M:%S')
            each_data["watch_num"] = each.watch_num
            data_list.append(each_data)
        send_data = {"state": "ok", "msg": data_list}
        return JsonResponse(send_data, safe=False)
    elif list_for == "details":
        # 获取用户社区全部列表
        page = request.GET.get("page")
        search_str = request.GET.get("search")
        if search_str == "":  # 所有
            essay_list = Essay.objects.filter(is_checked=True, is_delete=False).order_by("-create_time")
        else:  # 搜索
            key_list = search_str.split(" ")
            q = Q()
            for key in key_list:
                q.add(("title__icontains", key), Q.OR)
                q.add(("content__icontains", key), Q.OR)
            essay_list = Essay.objects.filter(q, is_checked=True, is_delete=False).order_by("-create_time")
        data_list = []
        paginator = Paginator(essay_list, essay_count_each_search_page)
        page_num = paginator.num_pages  # 总页数
        page_list = paginator.page_range  # 页码列表
        try:
            essay_list_page = paginator.page(page).object_list
        except Exception as e:
            return JsonResponse({"state": "fail", "msg": "out of range"}, safe=False, status=500)
        else:
            for each in essay_list_page:
                each_data = dict()
                each_data["id"] = each.id
                each_data["title"] = escape(each.title)
                each_data["content"] = escape(reg.sub('', each.content).replace('\n', '').replace(' ', '')[0:50])
                each_data["user"] = each.user.name
                each_data["create_time"] = each.create_time.strftime('%Y-%m-%d %H:%M:%S')
                each_data["watch_num"] = each.watch_num
                data_list.append(each_data)
            send_data = {"state": "ok", "msg": data_list, "page_num": page_num, "total_count": len(essay_list),
                         "per_page": essay_count_each_search_page}
            return JsonResponse(send_data, safe=False)


# 文章点赞
@silk_profile(name="文章点赞")
@login_required
def do_good(request):
    """文章点赞"""
    essay_id = request.POST.get("id")
    user_id = request.session["user_id"]
    # print(essay_id, user_id)
    try:
        essay = Essay.objects.get(id=essay_id, is_checked=True, is_delete=False)
    except Exception as e:
        # print(e)
        return JsonResponse({"state": "fail", "msg": "404 not fount"}, safe=False, status=404)
    else:
        try:
            good_mem = GoodList.objects.get(user_id=user_id, essay_id=essay_id)  # 点过赞，删除该条记录
        except Exception as e:
            # 没有给这篇文章点过赞
            # print(e)
            GoodList.objects.create(user_id=user_id, essay_id=essay_id)
        else:
            good_mem.delete()
        finally:
            good_num = len(GoodList.objects.filter(essay_id=essay_id))
            return JsonResponse({"state": "ok", "msg": {"id": essay_id, "good_num": good_num}}, safe=False)


# 文章收藏
@silk_profile(name="文章收藏")
@login_required
def do_collect(request):
    """文章收藏"""
    essay_id = request.POST.get("id")
    user_id = request.session["user_id"]
    # print(essay_id, user_id)
    collect_state = ""
    try:
        essay = Essay.objects.get(id=essay_id, is_checked=True, is_delete=False)
    except Exception as e:
        # print(e)
        return JsonResponse({"state": "fail", "msg": "404 not fount"}, status=404)
    else:
        try:
            good_mem = EssayCollection.objects.get(user_id=user_id, essay_id=essay_id)  # 已收藏，删除该条记录
        except Exception as e:
            # 没有给这篇文章点过赞
            # print(e)
            EssayCollection.objects.create(user_id=user_id, essay_id=essay_id)
            collect_state = "true"
        else:
            good_mem.delete()
            collect_state = "false"
        finally:
            collect_num = len(EssayCollection.objects.filter(essay_id=essay_id))
            return JsonResponse(
                {"state": "ok", "msg": {"id": essay_id, "collect_state": collect_state, "collect_num": collect_num}},
                safe=False)


class Comment(View):
    @silk_profile(name="发表评论")
    @method_decorator(login_required)
    def post(self, request):
        """发表评论"""
        import datetime
        user_id = request.session["user_id"]
        user_name = request.session["user_name"]
        history = EssayComment.objects.filter(user_id=user_id).order_by("-create_time")
        if len(history):
            time_delta = datetime.datetime.now() - history[0].create_time
            if time_delta.seconds < 60:
                # 频率控制
                return JsonResponse({"state": "fail", "msg": "wait"}, status=403, safe=False)

        comment_content = request.POST.get("content")
        essay_id = request.POST.get("for")
        user = User.objects.get(id=user_id)
        comment = EssayComment()
        comment.comment = escape(comment_content)
        comment.user = user
        comment.from_essay_id = essay_id
        comment.save()
        data = dict()
        data["user_name"] = user_name
        data["user_id"] = user_id
        data["head_path"] = str(user.head_photo)
        data["time"] = comment.create_time.strftime("%Y-%m-%d %H:%M:%S")
        data["good_num"] = comment.good_num
        data["comment"] = comment.comment
        data["upload_file"] = settings.MEDIA_URL
        data["comment_id"] = comment.id
        return JsonResponse({"state": "ok", 'msg': data}, safe=False)

    @silk_profile(name="获取所有评论及回复")
    def get(self, request):
        """获取所有评论及回复"""
        import datetime
        from django.core.paginator import Paginator
        essay_id = request.GET.get("for")
        page = request.GET.get("page")
        comments = EssayComment.objects.filter(from_essay_id=essay_id).order_by("-create_time")

        paginator = Paginator(comments, comment_each_page)
        page_num = paginator.num_pages  # 总页数
        page_list = paginator.page_range  # 页码列表
        total_count = len(comments)
        comments_page = paginator.page(page).object_list
        data_list = []
        for comment in comments_page:
            data = dict()
            data["user_name"] = comment.user.name
            data["user_id"] = comment.user.id
            data["head_path"] = str(comment.user.head_photo)
            data["time"] = comment.create_time.strftime("%Y-%m-%d %H:%M:%S")
            data["good_num"] = comment.good_num
            data["comment"] = escape(comment.comment)
            data["upload_file"] = settings.MEDIA_URL
            data["comment_id"] = comment.id

            # 获取回复
            replies = EssayCommentReply.objects.filter(from_comment_id=comment.id).order_by("-create_time")
            reply_list = []
            for reply in replies:
                replay_data = dict()
                replay_data["user_name"] = reply.user.name
                replay_data["reply_to"] = reply.reply_to.name
                replay_data["user_id"] = reply.user.id
                replay_data["head_path"] = str(reply.user.head_photo)
                replay_data["time"] = datetime.datetime.strftime(reply.create_time, "%Y-%m-%d %H:%M:%S")
                replay_data["good_num"] = reply.good_num
                replay_data["comment"] = escape(reply.reply)
                replay_data["comment_id"] = reply.id
                reply_list.append(replay_data)
            data["reply"] = reply_list
            data_list.append(data)
        return JsonResponse({"state": "ok", 'msg': data_list, "page_num": page_num, "per_page": comment_each_page,
                             "total_count": total_count}, safe=False)


class Reply(View):
    @silk_profile(name="评论回复")
    @method_decorator(login_required)
    def post(self, request):
        """评论回复"""
        import datetime
        user_name = request.session["user_name"]
        user_id = request.session["user_id"]
        history = EssayCommentReply.objects.filter(user_id=user_id).order_by("-create_time")
        if len(history):
            time_delta = datetime.datetime.now() - history[0].create_time
            if time_delta.seconds < 60:
                # 频率控制
                return JsonResponse({"state": "fail", "msg": "wait"}, status=403, safe=False)
        reply_content = request.POST.get("reply_content")
        root_id = request.POST.get("root_id")
        reply_id = request.POST.get("reply_id")
        reply_type = request.POST.get("reply_type")
        essay_id = request.POST.get("essay_id")

        comment = EssayComment.objects.get(id=root_id)  # root

        if reply_type == "root":
            reply_to_user = comment.user
        elif reply_type == "child":
            reply_to_user = EssayCommentReply.objects.get(id=reply_id).user
        else:
            return JsonResponse({}, status=500)

        reply = EssayCommentReply.objects.create(reply=escape(reply_content), from_comment=comment, user_id=user_id,
                                                 reply_to=reply_to_user)
        cur_user = User.objects.get(id=user_id)
        data = {
            "state": "ok",
            "msg": {
                "head_path": str(cur_user.head_photo),
                "user_name": user_name,
                "reply_to": reply_to_user.name,
                "time": datetime.datetime.strftime(reply.create_time, "%Y-%m-%d %H:%M:%S"),
                "comment": reply.reply,
                "good_num": reply.good_num,
                "upload_file": settings.MEDIA_URL,
                "comment_id": reply.id,
            }
        }
        return JsonResponse(data, safe=False)


@silk_profile(name="评论、回复点赞")
@login_required
def comment_reply_good(request):
    """评论回复的点赞"""
    comment_type = request.POST.get("comment_type")
    comment_id = request.POST.get("comment_id")

    if comment_type == "child":
        comment = EssayCommentReply.objects.get(id=comment_id)
        comment.good_num = comment.good_num + 1
        comment.save()
    else:
        # elif comment_type == "root":
        comment = EssayComment.objects.get(id=comment_id)
        comment.good_num = comment.good_num + 1
        comment.save()

    return JsonResponse({"state": "ok", "msg": {"good_num": comment.good_num}}, safe=False)


@silk_profile(name="获取社区个人信息")
@login_required
def get_per_info_list(request):
    from django.core.paginator import Paginator
    import re

    page = request.GET.get("page")
    info_type = request.GET.get("type")
    user_id = request.session["user_id"]

    if info_type == "collections":
        query_list = EssayCollection.objects.filter(user_id=user_id, essay__is_delete=False, essay__is_checked=True).order_by("-time")
    elif info_type == "history":
        query_list = BrowseHistory.objects.filter(user_id=user_id, essay__is_delete=False, essay__is_checked=True).order_by("-time")
    elif info_type == "good":
        query_list = GoodList.objects.filter(user_id=user_id, essay__is_delete=False, essay__is_checked=True).order_by("-time")
    elif info_type == "upload":
        query_list = Essay.objects.filter(user_id=user_id, is_delete=False, is_checked=True).order_by("-create_time")
    else:
        return JsonResponse({"state": "fail", "msg": "get away"}, safe=False, status=403)


    paginator = Paginator(query_list, personal_info_count_per_page)
    page_num = paginator.num_pages  # 总页数
    page_list = paginator.page_range  # 页码列表
    total_count = len(query_list)
    collect_page = paginator.page(page).object_list

    data_list = []
    reg = re.compile('<[^>]*>')
    if  info_type=='upload':
        for each in collect_page:
            data=dict()
            data["title"] = escape(each.title)
            data["id"] = each.id
            data["content"] = escape(reg.sub('', each.content).replace('\n', '').replace(' ', '')[0:50])
            data_list.append(data)
    else:
        for each in collect_page:
            data = dict()
            data["title"] = escape(each.essay.title)
            data["id"] = each.essay.id
            data["content"] = escape(reg.sub('', each.essay.content).replace('\n', '').replace(' ', '')[0:50])
            data_list.append(data)
    # print(data_list)
    return JsonResponse(
        {"state": "ok", "msg": data_list, "page_num": page_num, "per_page": personal_info_count_per_page,
         "total_count": total_count}, safe=False)
