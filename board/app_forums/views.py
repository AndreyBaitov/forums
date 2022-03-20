from django.shortcuts import render
from django.views import View, generic
from app_forums.forms import *
from app_forums.models import *
from app_profile.models import *
from django.http import HttpResponseRedirect
from app_forums.statistic_forums import CollectStatisticForums
from django.db.models import Q, Count, Subquery, OuterRef, DateTimeField
import datetime, math
MSG_PER_PAGE = 50
TOPIC_PER_PAGE = 15

def list_pages(page, sum):
    '''Функция выдающая список строк для отображения страниц, как тем в форме, так и сообщений в теме'''
    if sum == 1:
        return None
    if sum < 8:
        return [x for x in range(1,sum+1)]
    if page < 5:
        return [1,2,3,4,5,'...',sum]
    if page > sum-4:
        return [1,'...',sum-5,sum-4,sum-3,sum-2,sum-1,sum]
    return [1, '...', page-2, page-1, page, page+1, page+2, '...', sum]


class ForumsView(generic.ListView):
    '''Список всех форумов'''
    model = Forums
    template_name = 'forums_list.html'
    statistic = CollectStatisticForums()

    def get(self, request, *args, **kwargs):
        '''К стандартному добавляем составление актуального списка категорий и сбор статистики'''
        forums = Forums.objects.all()
        categories = Categories.objects.all() # пустота категорий проверяется в шаблоне
        self.extra_context = {'categories': categories}
        stat_data = self.statistic.run() # сбор статистики
        self.extra_context.update(stat_data)
        for forum in forums:
            topics = Topics.objects.filter(forum=forum)
            sum_msgs = 0
            for topic in topics:
                sum_msgs += topic.sum_msgs
            forum.sum_msgs = sum_msgs  # сумма сообщений на форуме
            forum.last_message = Messages.objects.filter(topic__forum=forum).order_by('created_at').last()
        self.extra_context.update({'forums':forums})
        response = super().get(self, request, *args, **kwargs)
        return response


class ForumDetailView(generic.DetailView):
    '''Отображение форума со всеми его топиками'''
    model = Forums
    template_name = 'forum.html'
    context_object_name = 'forum'

    def get(self, request, pk: int, page: int, *args, **kwargs):
        forum_id = pk
        forum = Forums.objects.get(id=forum_id)  # get возвращает только 1 объект, два не может
        all_topics = Topics.objects.filter(forum=forum).order_by('-updated_at')
        if forum.sum_topics < 16:    # Если тем меньше чем на 1 страницу, то показываем все темы
            topics = all_topics
            page = 1                # пофигу на какую страницу шел пользователь, мы его перешлём на 1
        else:                       # иначе начинаем смотреть куда шел пользователь и даём ему список тем
            try:
                topics = Topics.objects.filter(forum=forum).order_by('-updated_at')[0+(page-1)*15:15+(page-1)*15]  #  получаем из базы все темы по айди форума
            except IndexError:      # суда попадаем при краевом случае на последней странице
                topics = Topics.objects.filter(forum=forum).order_by('-updated_at')[0 + (page - 1) * 15:]
        for topic in topics:
            topic.pages = list_pages(1, math.ceil(topic.sum_msgs / MSG_PER_PAGE))
            topic.last_message = Messages.objects.filter(topic=topic).order_by('created_at').last()
        sum_pages = math.ceil(forum.sum_topics / TOPIC_PER_PAGE)
        self.extra_context = {
            'topics': topics,
            'current_page':page,
            'pages': list_pages(page,sum_pages)
                                }
        response = super().get(self, request, forum_id, page, *args, **kwargs)
        return response

class TopicDetailView(generic.DetailView):
    '''Отображение темы со всеми её сообщениями'''
    model = Topics
    template_name = 'topic.html'

    def get(self, request, pk, page, *args, **kwargs):
        topic_id = pk
        topic = Topics.objects.get(id=topic_id)
        forum = topic.forum
        if topic.sum_msgs < MSG_PER_PAGE:    # Если сообщений меньше чем на 1 страницу, то показываем все
            messages = Messages.objects.filter(topic=topic)
            page = 1                # пофигу на какую страницу шел пользователь, мы его перешлём на 1
        else:                       # иначе начинаем смотреть куда шел пользователь и даём ему список сообщений
            try:
                messages = Messages.objects.filter(topic=topic)[0+(page-1)*MSG_PER_PAGE:MSG_PER_PAGE+(page-1)*MSG_PER_PAGE]
            except IndexError:      # суда попадаем при краевом случае на последней странице
                messages = Messages.objects.filter(topic=topic)[0 + (page - 1) * MSG_PER_PAGE:]
        sum_pages = math.ceil(topic.sum_msgs / MSG_PER_PAGE)
        pages = list_pages(page,sum_pages)

        self.extra_context = {
            'messages': messages,
            'topic': topic,
            'forum':forum,
            'current_page':page,
            'pages': pages,
                                }
        response = super().get(self, request, topic_id, page, *args, **kwargs)
        topic.counted_views += 1
        topic.save()
        return response


class MessageAddView(generic.DetailView):
    '''topic/<int:pk>/add-message/'''
    model = Topics
    template_name = 'add-message.html'
    context_object_name = 'topic'

    def get(self, request, pk, *args, **kwargs):
        topic_id = pk
        topic = Topics.objects.get(id=topic_id)
        messages = Messages.objects.filter(topic=topic)  #  получаем из базы все сообщения по айди темы
        msg_form = MessageForm()
        self.extra_context = {'messages': messages,'msg_form':msg_form}
        response = super().get(self, request, topic_id, *args, **kwargs)
        print(msg_form.as_p())
        return response

    def post(self, request, pk):
        msg_form = MessageForm(request.POST)
        if request.user.is_authenticated:
            if msg_form.is_valid():
                # заносим в базу
                user = request.user.app_user  # ищем Юзера
                msg_form.cleaned_data['user'] = user
                topic_id = pk                               # ищем тему в которой сделан пост
                topic = Topics.objects.get(id=topic_id)
                msg_form.cleaned_data['topic'] = topic
                msg_form.cleaned_data['number'] = topic.sum_msgs + 1
                msg = Messages.objects.create(**msg_form.cleaned_data)
                topic.updated_at = msg.created_at
                topic.sum_msgs += 1
                topic.save()
                user.msgs += 1
                user.save()
                page = math.ceil(topic.sum_msgs / MSG_PER_PAGE)
                return HttpResponseRedirect(f'/topic/{topic_id}/page/{page}/#{msg.number}')
            else:
                return render(request, 'add-message.html', context={'msg_form': msg_form})
        else:
            return HttpResponseRedirect('/login/')

class TopicAddView(generic.DetailView):
    '''forum/<int:pk>/add-topic/'''
    model = Forums
    template_name = 'add-topic.html'
    context_object_name = 'forum'

    def get(self, request, pk, *args, **kwargs):
        forum_id = pk  # DetailView требует обязательного имени pk в урле
        forum = Forums.objects.get(id=forum_id)
        topics = Topics.objects.filter(forum=forum)  #  получаем из базы все темы по айди форума
        msg_form = MessageForm()
        topic_form = TopicForm()
        self.extra_context = {'topics': topics,'msg_form':msg_form,'topic_form':topic_form}
        response = super().get(self, request, forum_id, *args, **kwargs)
        return response

    def post(self, request, pk):
        msg_form = MessageForm(request.POST)
        topic_form = TopicForm(request.POST)
        if request.user.is_authenticated:
            forum_id = pk  # ищем форрум в котором делается тема
            forum = Forums.objects.get(id=forum_id)
            if msg_form.is_valid() and topic_form.is_valid() and msg_form.cleaned_data['title']:  # Поскольку мы в форме title темы не оставили, чтобы не было дубляжа
                                                                                                    # тут мы проверяем, что он не пустой, так как у самой формы MSG он не обязателен
                user = request.user.app_user  # ищем Юзера
                topic_form.cleaned_data['user'] = user      # связываем тему с пользователем и форумом
                topic_form.cleaned_data['forum'] = forum
                topic_form.cleaned_data['title'] = msg_form.cleaned_data['title']  #копируем титул сообщения, так как мы не заполняли титул темы
                topic = Topics.objects.create(**topic_form.cleaned_data)
                topic.updated_at = topic.created_at
                topic.save()
                topic.forum.sum_topics += 1
                topic.forum.save()

                msg_form.cleaned_data['user'] = user  # связываем сообщение с пользователем и темой и ставим флаг для но_делит
                msg_form.cleaned_data['topic'] = topic
                msg_form.cleaned_data['topic_start'] = True
                msg = Messages.objects.create(**msg_form.cleaned_data)
                msg.updated_at = msg.created_at
                msg.save()
                user.msgs += 1
                user.save()
                return HttpResponseRedirect(f'/forum/{forum_id}/page/1/')
            else:
                topics = Topics.objects.filter(forum=forum)
                return render(request, 'add-topic.html', context={'topics': topics,'msg_form':msg_form,'topic_form':topic_form})
        else:
            return HttpResponseRedirect('/login/')


class MessageEditView(View):
    '''редактирование сообщения'''

    def get(self, request, msg_id):
        msg = Messages.objects.get(id=msg_id)  # получаем из базы сообщение по айди
        topic = msg.topic
        user = request.user.app_user
        if user != msg.user and (user.status != 'admin'):  # Если Вы редактируете не своё сообщение и вы не админ, то нельзя
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        msg_form = MessageForm(instance=msg)  # заполняем форму уже имеющимися данными
        return render(request, 'edit-message.html', context={'msg_form': msg_form, 'msg_id': msg_id,'topic': topic})

    def post(self, request, msg_id):
        msg = Messages.objects.get(id=msg_id)
        topic = msg.topic
        msg_form = MessageForm(request.POST, instance=msg)
        if msg_form.is_valid():
            msg.updated_at = datetime.datetime.now()
            msg.save()
            page = math.ceil(topic.sum_msgs / MSG_PER_PAGE)
            return HttpResponseRedirect(f'/topic/{topic_id}/page/{page}/#{msg.number}')
        return render(request, 'edit-message.html', context={'msg_form': msg_form, 'msg_id': msg_id, 'topic': topic})

class MessageDeleteView(View):
    '''удаление сообщения'''

    def get(self, request, msg_id):
        msg = Messages.objects.get(id=msg_id)  # получаем из базы сообщение по айди
        topic = msg.topic
        forum = topic.forum
        if not request.user.is_authenticated:  # сначала проверяем, а зареген ли юзер
            return HttpResponseRedirect('/login/')
        user = request.user.app_user
        if (user.status == 'admin') or (user in forum.moderators.all()):  # модераторам и админам можно всё
            return render(request, 'delete-message.html', context={'msg': msg, 'topic': topic})
        # теперь проверка может ли простой юзер это делать
        if (request.user.app_user != msg.user) or (msg.status=='closed'):  # Если Вы удаляете не своё сообщение, то нельзя
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        # проверка пройдена
        return render(request, 'delete-message.html', context={'msg': msg,'topic': topic})

    def post(self, request, msg_id, reasondelete=''):
        msg = Messages.objects.get(id=msg_id)
        topic = msg.topic
        forum = topic.forum
        if not request.user.is_authenticated:
            return HttpResponseRedirect('/login/')
        user = request.user.app_user
        # проверка не требуется, поскольку она уже пройдена в методе get
        msg.user.msgs -= 1
        if topic.sum_msgs == 1:  # это единственное сообщение в теме
            topic.forum.sum_topics -= 1
            topic.forum.save()
            for user in msg.thankers.all():  # стираем все благодарности и пользователям и юзеру
                msg.user.acknowledgements -= 1
                user.thanks -= 1
                user.save()
            msg.user.save()
            msg.delete()
            topic.delete()
            return HttpResponseRedirect(f'/forum/{forum.id}/page/1/')
        else:
            topic.sum_msgs -=1
            topic.save()
            number = msg.number
            msgs = Messages.objects.filter(number__gt=msg.number)
            for item in msgs:
                item.number -= 1
                item.save()
            for user in msg.thankers.all():  # стираем все благодарности и пользователям и юзеру
                msg.user.acknowledgements -= 1
                user.thanks -= 1
                user.save()
            msg.user.save()
            msg.delete()
            page = math.ceil(topic.sum_msgs / MSG_PER_PAGE)
            return HttpResponseRedirect(f'/topic/{topic.id}/page/{page}/#{number}')

def thanks(request, pk):
    '''Функция обработки объявления благодарности сообщения'''
    msg = Messages.objects.get(id=pk)
    topic = msg.topic
    if not request.user.is_authenticated: # Если благодаришь незалогинившись. Хотя этой иконки не должно быть
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    user = request.user.app_user
    if user == msg.user:  # Если благодаришь сам себя, то редирект. Хотя этой иконки не должно быть
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    if user in msg.thankers.all():  # Если уже благодарил, то редирект. Хотя этой иконки не должно быть
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    # все условия соблюдены
    msg.thankers.add(user)
    msg.save()
    msg.user.acknowledgements += 1
    msg.user.save()
    user.thanks += 1
    user.save()
    page = math.ceil(msg.number / MSG_PER_PAGE)
    return HttpResponseRedirect(f'/topic/{topic.id}/page/{page}/#{msg.number}')

def undo_thanks(request, pk):
    '''Функция обработки снятия благодарности сообщения'''
    msg = Messages.objects.get(id=pk)
    topic = msg.topic
    if not request.user.is_authenticated: # Незалогинившись. Хотя этой иконки не должно быть
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    user = request.user.app_user
    if user == msg.user:  # Если это ты же сам. Хотя этой иконки не должно быть
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    if not user in msg.thankers.all():  # Если тебя нет в списке благодаривших, то редирект. Хотя этой иконки не должно быть
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    # все условия соблюдены
    msg.thankers.remove(user)
    msg.save()
    msg.user.acknowledgements -= 1
    msg.user.save()
    if user.thanks != 0:
        user.thanks -= 1
    else:
        user.thanks = 0
    user.save()
    page = math.ceil(msg.number / MSG_PER_PAGE)
    return HttpResponseRedirect(f'/topic/{topic.id}/page/{page}/#{msg.number}')