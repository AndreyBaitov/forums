from django.shortcuts import render
from django.views import View, generic
from app_forums.forms import *
from app_forums.models import *
from app_profile.models import *
from django.http import HttpResponseRedirect
from app_forums.statistic_forums import CollectStatisticForums

class ForumsView(generic.ListView):
    '''Список всех форумов'''
    model = Forums
    template_name = 'forums_list.html'
    context_object_name = 'forums'

    def get(self, request, *args, **kwargs):
        '''К стандартному добавляем составление актуального списка категорий и сбор статистики'''
        queryset = Forums.objects.all()
        categories = {}  # собираем список имеющихся в данный момент категорий форумов, чтобы не показывать пустые
        for forum in queryset:
            categories[forum.category.id] = forum.category.name
        ordered_categories = {}
        for key in sorted(list(categories.keys())):  # сортируем по id список этих форумов в виде словаря
            ordered_categories[key] = categories[key]
        self.extra_context = {'categories': ordered_categories}
        statistic = CollectStatisticForums() # сбор статистики
        self.extra_context.update(statistic.data)
        print(statistic.data)
        response = super().get(self, request, *args, **kwargs)
        return response


class ForumDetailView(generic.DetailView):
    '''Отображение форума со всеми его топиками'''
    model = Forums
    template_name = 'forum.html'
    context_object_name = 'forum'

    def get(self, request, pk, *args, **kwargs):
        forum_id = pk
        forum = Forums.objects.get(id=forum_id)  # get возвращает только 1 объект, два не может
        topics = Topics.objects.filter(forum=forum)  #  получаем из базы все темы по айди форума
        self.extra_context = {'topics': topics}
        response = super().get(self, request, forum_id, *args, **kwargs)
        # ваш код с куками подсчета просмотров
        return response

class TopicDetailView(generic.DetailView):
    '''Отображение темы со всеми её сообщениями'''
    model = Topics
    template_name = 'topic.html'
    context_object_name = 'topic'

    def get(self, request, pk, *args, **kwargs):
        topic_id = pk
        topic = Topics.objects.get(id=topic_id)
        forum = topic.forum
        messages = Messages.objects.filter(topic=topic)  #  получаем из базы все сообщения по айди темы
        self.extra_context = {'messages': messages,'forum':forum}
        response = super().get(self, request, topic_id, *args, **kwargs)
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
            username = request.user
            if msg_form.is_valid():
                # заносим в базу
                user = Users.objects.get(username=username)  # ищем Юзера по базе юзеров, опиралась на совпадающий ник логина
                msg_form.cleaned_data['user'] = user
                topic_id = pk                               # ищем тему в которой сделан пост
                topic = Topics.objects.get(id=topic_id)
                msg_form.cleaned_data['topic'] = topic
                Messages.objects.create(**msg_form.cleaned_data)
                return HttpResponseRedirect(f'/topic/{topic_id}/')
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
                user = Users.objects.get(username=request.user)  # ищем Юзера по базе юзеров, опиралась на совпадающий ник логина, потому что напрямую
                topic_form.cleaned_data['user'] = user      # связываем тему с пользователем и форумом
                topic_form.cleaned_data['forum'] = forum
                topic_form.cleaned_data['title'] = msg_form.cleaned_data['title']  #копируем титул сообщения, так как мы не заполняли титул темы
                topic = Topics.objects.create(**topic_form.cleaned_data)
                msg_form.cleaned_data['user'] = user  # связываем сообщение с пользователем и темой и ставим флаг для но_делит
                msg_form.cleaned_data['topic'] = topic
                msg_form.cleaned_data['topic_start'] = True
                Messages.objects.create(**msg_form.cleaned_data)
                return HttpResponseRedirect(f'/forum/{forum_id}/')
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
        user = Users.objects.get(username=str(request.user))
        if (str(request.user) != str(msg.user)) and (user.status != 'admin'):  # Если Вы редактируете не своё сообщение и вы не админ, то нельзя
            return HttpResponseRedirect(f'/topic/{topic.id}/')
        msg_form = MessageForm(instance=msg)  # заполняем форму уже имеющимися данными
        return render(request, 'edit-message.html', context={'msg_form': msg_form, 'msg_id': msg_id,'topic': topic})

    def post(self, request, msg_id):
        msg = Messages.objects.get(id=msg_id)
        topic = msg.topic
        msg_form = MessageForm(request.POST, instance=msg)
        if msg_form.is_valid():
            msg.save()
            return HttpResponseRedirect(f'/topic/{topic.id}/')
        return render(request, 'edit-message.html', context={'msg_form': msg_form, 'msg_id': msg_id, 'topic': topic})

class MessageDeleteView(View):
    '''удаление сообщения'''

    def get(self, request, msg_id):
        msg = Messages.objects.get(id=msg_id)  # получаем из базы сообщение по айди
        topic = msg.topic
        forum = topic.forum
        if not request.user.is_authenticated:  # сначала проверяем, а зареген ли юзер
            return HttpResponseRedirect('/login/')
        user = Users.objects.get(username=str(request.user))
        if (user.status != 'admin') or (user in forum.moderators.all()):  # модераторам и админам можно всё
            return render(request, 'delete-message.html', context={'msg': msg, 'topic': topic})
        # теперь проверка может ли простой юзер это делать
        if (str(request.user) != str(msg.user)) or (msg.status=='closed'):  # Если Вы удаляете не своё сообщение, то нельзя
            return HttpResponseRedirect(f'/topic/{topic.id}/')
        # проверка пройдена
        return render(request, 'delete-message.html', context={'msg': msg,'topic': topic})

    def post(self, request, msg_id, reasondelete=''):
        msg = Messages.objects.get(id=msg_id)
        topic = msg.topic
        forum = topic.forum
        if not request.user.is_authenticated:
            return HttpResponseRedirect('/login/')
        user = Users.objects.get(username=str(request.user))
        # проверка не требуется, поскольку она уже пройдена в методе get
        all_msg = Messages.objects.filter(topic=topic)
        if len(all_msg) == 1:  # это единственное сообщение в теме
            msg.delete()
            topic.delete()
            return HttpResponseRedirect(f'/forum/{forum.id}/')
        else:
            msg.delete()
            return HttpResponseRedirect(f'/topic/{topic.id}/')


