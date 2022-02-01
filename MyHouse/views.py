from django.http import JsonResponse
from django.middleware.csrf import get_token


def csrf_token(request):
    token = get_token(request)
    return JsonResponse({'token': token})
