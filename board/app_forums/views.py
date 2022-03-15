from django.shortcuts import render
from django.views import View, generic
from app_forums.forms import *
from app_forums.models import *
from app_profile.models import *
from django.http import HttpResponseRedirect
from app_forums.statistic_forums import CollectStatisticForums
from django.db.models import Q, Count, Subquery, OuterRef, DateTimeField
import datetime, math


class ForumsView(generic.ListView):
    '''Список всех форумов'''
    model = Forums
    template_name = 'forums_list.html'
    statistic = CollectStatisticForums()

    def get(self, request, *args, **kwargs):
        '''К стандартному добавляем составление актуального списка категорий и сбор статистики'''
        forums = Forums.objects.all()
        categories = {}  # собираем список имеющихся в данный момент категорий форумов, чтобы не показывать пустые
        for forum in forums:
            categories[forum.category.id] = forum.category.name
        ordered_categories = {}
        for key in sorted(list(categories.keys())):  # сортируем по id список этих форумов в виде словаря
            ordered_categories[key] = categories[key]
        self.extra_context = {'categories': ordered_categories}
        stat_data = self.statistic.run() # сбор статистики
        self.extra_context.update(stat_data)
        for forum in forums:
            topics = Topics.objects.filter(forum=forum)
            sum_msg = 0
            for topic in topics:
                sum_msg += len(Messages.objects.filter(topic=topic))
            forum.sum_msg = sum_msg  # сумма сообщений на форуме
            forum.sum_topics = len(Topics.objects.filter(forum=forum))  # сумма тем на форуме
            forum.last_message = Messages.objects.filter(topic__forum=forum).order_by('-created_at').first()
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
        sum_topics_on_forum = len(all_topics)
        if sum_topics_on_forum < 16:    # Если тем меньше чем на 1 страницу, то показываем все темы
            topics = all_topics
            page = 1                # пофигу на какую страницу шел пользователь, мы его перешлём на 1
        else:                       # иначе начинаем смотреть куда шел пользователь и даём ему список тем
            try:
                topics = Topics.objects.filter(forum=forum).order_by('-updated_at')[0+(page-1)*15:15+(page-1)*15]  #  получаем из базы все темы по айди форума
            except IndexError:      # суда попадаем при краевом случае на последней странице
                topics = Topics.objects.filter(forum=forum).order_by('-updated_at')[0 + (page - 1) * 15:]
        for topic in topics:
            topic.messages = len(Messages.objects.filter(topic=topic))-1
            topic.pages = list_pages(1, math.ceil(topic.messages / 50))
            topic.last_message = Messages.objects.filter(topic=topic).order_by('created_at').last()
        sum_pages = math.ceil(sum_topics_on_forum / 15)
        pages = list_pages(page,sum_pages)
        self.extra_context = {
            'topics': topics,
            'current_page':page,
            'sum_topics_on_forum':sum_topics_on_forum,
            'sum_ending':theme_ending(sum_topics_on_forum),
            'sum_pages':sum_pages,
            'pages': pages
                                }
        response = super().get(self, request, forum_id, page, *args, **kwargs)
        return response

def theme_ending(number:int)->str:
    '''Функция возвращающая строковую переменную окончания слова тем__ в зависимости от количества'''
    endings = {'1':'а','2':'ы','3':'ы','4':'ы','5':'','6':'','7':'','8':'','9':'','0':''}
    if number > 5 and number < 20:
        ending = ''
    else:
        ending = endings[str(number)[-1]]
    return ending

def msg_ending(number:int)->str:
    '''Функция возвращающая строковую переменную окончания слова сообщен__ в зависимости от количества'''
    endings = {'1':'ие','2':'ия','3':'ия','4':'ия','5':'ий','6':'ий','7':'ий','8':'ий','9':'ий','0':'ий'}
    if number > 5 and number < 20:
        ending = 'ий'
    else:
        ending = endings[str(number)[-1]]
    return ending

def case_ending(number:int)->str:
    '''Функция возвращающая строковую переменную окончания слова раз___ в зависимости от количества'''
    endings = {'1':'','2':'а','3':'а','4':'а','5':'','6':'','7':'','8':'','9':'','0':''}
    if number > 5 and number < 20:
        ending = ''
    else:
        ending = endings[str(number)[-1]]
    return ending

def list_pages(page, sum):
    '''Функция выдающая список строк для отображения страниц, как тем в форме, так и сообщений в теме'''
    if sum == 1:
        return None
    if sum < 8:
        return [(str(x),x) for x in range(1,sum+1)]
    if page < 5:
        return [('1',1),('2',2),('3',3),('4',4),('5',5),('...',0),(str(sum),sum)]
    if page > sum-4:
        return [('1',1),('...',0),(str(sum-5),sum-5),(str(sum-4),sum-4),(str(sum-3),sum-3),(str(sum-2),sum-2),(str(sum-1),sum-1),(str(sum),sum)]
    return [('1',1), ('...',0), (str(page-2),page-2), (str(page-1),page-1), (str(page),page), (str(page+1),page+1), (str(page+2),page+2), ('...',0),(str(sum),sum)]




class TopicDetailView(generic.DetailView):
    '''Отображение темы со всеми её сообщениями'''
    model = Topics
    template_name = 'topic.html'

    def get(self, request, pk, page, *args, **kwargs):
        topic_id = pk
        topic = Topics.objects.get(id=topic_id)
        topic.messages = Messages.objects.filter(topic=topic).order_by('created_at')
        forum = topic.forum
        all_messages = Messages.objects.filter(topic=topic)  #  получаем из базы все сообщения по айди темы
        sum_msg_on_topic = len(all_messages)

        if sum_msg_on_topic < 50:    # Если сообщений меньше чем на 1 страницу, то показываем все
            messages = all_messages
            page = 1                # пофигу на какую страницу шел пользователь, мы его перешлём на 1
        else:                       # иначе начинаем смотреть куда шел пользователь и даём ему список сообщений
            try:
                messages = Messages.objects.filter(topic=topic).order_by('-created_at')[0+(page-1)*50:50+(page-1)*50]
            except IndexError:      # суда попадаем при краевом случае на последней странице
                messages = Messages.objects.filter(topic=topic).order_by('-created_at')[0 + (page - 1) * 50:]
        sum_pages = math.ceil(sum_msg_on_topic / 50)
        pages = list_pages(page,sum_pages)

        for msg in messages:        # расставляем окончания
            msg.thanks_ending = case_ending(msg.user.thanks)
            print(msg.thanks_ending)
            msg.acknowledgements_ending = case_ending(msg.user.acknowledgements)
            print(msg.acknowledgements_ending)

        self.extra_context = {
            'messages': messages,
            'topic': topic,
            'forum':forum,
            'current_page':page,
            'sum_msg_on_topic':sum_msg_on_topic,
            'sum_ending':msg_ending(sum_msg_on_topic),
            'sum_pages':sum_pages,
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
                msg = Messages.objects.create(**msg_form.cleaned_data)
                topic.updated_at = msg.created_at
                topic.save()
                user.msgs += 1
                user.save()
                return HttpResponseRedirect(f'/topic/{topic_id}/page/1/')
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
            return HttpResponseRedirect(f'/topic/{topic.id}/page/1/')
        msg_form = MessageForm(instance=msg)  # заполняем форму уже имеющимися данными
        return render(request, 'edit-message.html', context={'msg_form': msg_form, 'msg_id': msg_id,'topic': topic})

    def post(self, request, msg_id):
        msg = Messages.objects.get(id=msg_id)
        topic = msg.topic
        msg_form = MessageForm(request.POST, instance=msg)
        if msg_form.is_valid():
            msg.updated_at = datetime.datetime.now()
            msg.save()
            return HttpResponseRedirect(f'/topic/{topic.id}/page/1/')
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
            return HttpResponseRedirect(f'/topic/{topic.id}/page/1/')
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
        all_msg = Messages.objects.filter(topic=topic)
        msg.user.msgs -= 1
        msg.user.save()
        if len(all_msg) == 1:  # это единственное сообщение в теме
            msg.delete()
            topic.delete()
            return HttpResponseRedirect(f'/forum/{forum.id}/page/1/')
        else:
            msg.delete()
            return HttpResponseRedirect(f'/topic/{topic.id}/page/1/')

def thanks(request, pk):
    '''Функция обработки объявления благодарности сообщения'''
    msg = Messages.objects.get(id=pk)
    topic = msg.topic
    if not request.user.is_authenticated: # Если благодаришь незалогинившись. Хотя этой иконки не должно быть
        return HttpResponseRedirect(f'/topic/{topic.id}/page/1/')
    user = request.user.app_user
    if user == msg.user:  # Если благодаришь сам себя, то редирект. Хотя этой иконки не должно быть
        return HttpResponseRedirect(f'/topic/{topic.id}/page/1/')
    if user in msg.thankers.all():  # Если уже благодарил, то редирект. Хотя этой иконки не должно быть
        return HttpResponseRedirect(f'/topic/{topic.id}/page/1/')
    # все условия соблюдены
    msg.thankers.add(user)
    msg.save()
    msg.user.acknowledgements += 1
    msg.user.save()
    user.thanks += 1
    user.save()
    return HttpResponseRedirect(f'/topic/{topic.id}/page/1/')

def undo_thanks(request, pk):
    '''Функция обработки снятия благодарности сообщения'''
    msg = Messages.objects.get(id=pk)
    topic = msg.topic
    if not request.user.is_authenticated: # Незалогинившись. Хотя этой иконки не должно быть
        return HttpResponseRedirect(f'/topic/{topic.id}/page/1/')
    user = request.user.app_user
    if user == msg.user:  # Если это ты же сам. Хотя этой иконки не должно быть
        return HttpResponseRedirect(f'/topic/{topic.id}/page/1/')
    if not user in msg.thankers.all():  # Если тебя нет в списке благодаривших, то редирект. Хотя этой иконки не должно быть
        return HttpResponseRedirect(f'/topic/{topic.id}/page/1/')
    # все условия соблюдены
    msg.thankers.remove(user)
    msg.save()
    msg.user.acknowledgements -= 1
    msg.user.save()
    user.thanks -= 1
    user.save()
    return HttpResponseRedirect(f'/topic/{topic.id}/page/1/')