from django.core.exceptions import PermissionDenied
import time, os, os.path
# print(os.getcwd())
# path = os.getcwd()
# path = os.path.dirname(path)
# path = os.path.dirname(path)
# path = os.path.join(path,'app_forums')
# print(path)
# import path.models
from app_forums.models import StatUsers
from app_profile.models import Users

# class FilterIPMiddleware:
#     '''Список айпи с доступом к сайту'''
#     def __init__(self, get_response):
#         self.get_response = get_response
#
#     def __call__(self, request):
#
#         allowed_ips = ['127.0.0.1']
#         ip = request.META.get('REMOTE_ADDR')
#         if ip not in allowed_ips:
#             raise PermissionDenied
#
#         response = self.get_response(request)
#
#         return response

# class StopIPMiddleware:
#     '''Бан по айпи'''
#     def __init__(self, get_response):
#         self.get_response = get_response
#
#     def __call__(self, request):
#
#         denied_ips = ['127.0.0.2']
#         ip = request.META.get('REMOTE_ADDR')
#         if ip in denied_ips:
#             raise PermissionDenied
#         response = self.get_response(request)
#
#         return response

# class WaitingMiddleware:
#     '''При большом количестве запросов от пользователя тормозит его работу'''
#     def __init__(self, get_response):
#         self.get_response = get_response
#         self.user_list = {}
#         self.max_response = 1000
#
#     def __call__(self, request):
#
#         ip = request.META.get('REMOTE_ADDR')
#         if ip not in self.user_list.keys():
#             self.user_list[ip] = 1
#         else:
#             self.user_list[ip] += 1
#
#         if self.user_list[ip] > self.max_response:
#             time.sleep(5)
#
#         response = self.get_response(request)
#
#         return response

class DDOSMiddleware:
    '''При большом количестве запросов от пользователя банит его'''

    def __init__(self, get_response):
        self.get_response = get_response
        self.user_list = {}  # данные по юзерам по ip ключу [список времен запросов]
        self.max_response = 100  # максимум 100 запрсоов
        self.max_time = 100     # за последние 100 секунд

    def __call__(self, request):
        time_now = time.time()
        ip = request.META.get('REMOTE_ADDR')
        if ip not in self.user_list.keys():
            self.user_list[ip] = [time_now]
        else:
            count = len(self.user_list[ip])
            time_ref = self.user_list[ip][0]
            if count >= self.max_response and ((time_ref - time_now) <= self.max_time):  #слишком много запросов
                raise PermissionDenied
            elif (time_ref - time_now) <= self.max_time:  #время не кончилось, считаем запросы
                self.user_list[ip].append(time_now)
            elif (time_ref - time_now) > self.max_time:  # корректируем начальное время
                self.user_list[ip].pop(0)
                self.user_list[ip].append(time_now)

        response = self.get_response(request)
        return response

class LogMiddleware:
    '''Логирует в файле лога ip пользователя, время, урл запроса и http метод'''

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        time_now = time.ctime(time.time()-time.timezone)
        ip = request.META.get('REMOTE_ADDR')
        if request.user.is_authenticated:
            user = Users.objects.get(username=request.user)
            obj = StatUsers.objects.update_or_create(user=user, ip=ip)
        else:
            obj = StatUsers.objects.filter(ip=ip,user=None)
            if obj:
                obj[0].save()
        print(obj)
        #todo сделать проверку валидности (сохранность 5 минут) всех записей статистики, в случае просрочки удалить

        # method = request.META.get('REQUEST_METHOD')
        # url = request.path
        # path = os.path.join(os.getcwd(), 'log')
        # file_path = os.path.join(path,'log_user_request.log')
        # with open(file_path,'a', encoding='utf-8') as file:
        #     data = 'IP=' + ip + ' in ' + time_now + ' trying ' + method + ' to ' + url + '\n'
        #     file.write(data)
        response = self.get_response(request)

        return response