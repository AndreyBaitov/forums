from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
class Categories(models.Model):
    '''Категории форумов: Барахолка, Общение, Судомоделизм'''
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'Категории форумов'
        verbose_name = 'Категория'
        ordering = ['name']

class Forums(models.Model):
    STATUS_CHOICE = [('opened', 'opened'), ('closed', 'closed'), ('hiddened', 'hiddened')]
    name = models.CharField(max_length=100, db_index=True, verbose_name='Название форума')
    description = models.CharField(max_length=200, default='', verbose_name='Краткое описание темы форума')
    category = models.ForeignKey(Categories, on_delete=models.PROTECT,
                                related_name='category', blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICE,default='opened')
    moderators = models.ManyToManyField('app_profile.Users', verbose_name='Модераторы форума', related_name='moderators', blank=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'forums'
        verbose_name_plural = 'Форумы'
        verbose_name = 'Форум'
        ordering = ['name']

    def list_moderators(self):
        '''Функция для отображения списка модераторов в админке, потому что это модель ManyToMany'''
        return ", ".join([x.username for x in self.moderators.all()])

def check_title_topic(title: str):
    print(title)
    if title.isdigit():
        raise ValidationError('Заголовок не может состоять только из одних цифр!')

class Topics(models.Model):
    '''Класс тем'''
    STATUS_CHOICE = [('opened', 'opened'), ('closed', 'closed'),('hiddened', 'hiddened')]
    TYPE_CHOICE = [('simple', 'simple'), ('important', 'important'),('attention', 'attention')]
    title = models.CharField(max_length=100, verbose_name='Заголовок темы', validators=[check_title_topic])
    user = models.ForeignKey('app_profile.Users', db_index=True, null=True, on_delete=models.PROTECT,
                             related_name='topic_users', blank=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата публикации')
    forum = models.ForeignKey('Forums', null=True, on_delete=models.PROTECT,
                                related_name='forums', blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICE, default='opened')
    type = models.CharField(max_length=10, choices=TYPE_CHOICE, default='simple')
    counted_views = models.IntegerField(verbose_name='Количество просмотров', default=0)
    updated_at = models.DateTimeField(default=timezone.now, verbose_name='Дата последней записи')

    def __str__(self):
        return self.title +' in forum: ' + self.forum.name

    class Meta:
        db_table = 'topics'
        verbose_name_plural = 'Темы'
        verbose_name = 'Тема'
        ordering = ['-created_at']


class Messages(models.Model):
    '''Класс сообщений на форумах'''
    STATUS_CHOICE = [('editable', 'editable'), ('closed', 'closed'),('hiddened', 'hiddened')]
    user = models.ForeignKey('app_profile.Users', db_index=True, null=True, on_delete=models.PROTECT,
                                related_name='message_users', blank=True)
    title = models.CharField(max_length=100, null=True, blank=True, default='', validators=[check_title_topic], verbose_name='Заголовок сообщения')
    message = models.TextField(default='', verbose_name='Сообщение')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата публикации')
    updated_at = models.DateTimeField(default=timezone.now, verbose_name='Дата редактирования')
    topic = models.ForeignKey('Topics', null=True, on_delete=models.CASCADE,
                                related_name='topics', blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICE,default='editable')
    topic_start = models.BooleanField(verbose_name='Первое сообщение темы', null=True, blank=True, default=False)
    thankers = models.ManyToManyField('app_profile.Users', verbose_name='Сказавшие спасибо',
                                        related_name='thankers', blank=True)

    def __str__(self):
        return self.user.username +' in topic: ' + self.topic.title

    class Meta:
        db_table = 'messages'
        verbose_name_plural = 'Сообщения'
        verbose_name = 'Сообщение'
        ordering = ['created_at']

    def list_thankers(self):
        '''Функция для отображения списка благодаривших в админке, потому что это модель ManyToMany'''
        return ", ".join([x.username for x in self.thankers.all()])


class StatUsers(models.Model):
    '''База, содержащая записи тех пользователей, которые сейчас на форуме.'''
    user = models.ForeignKey('app_profile.Users', db_index=True, null=True, on_delete=models.PROTECT,
                             related_name='stat_users', related_query_name='statuser', blank=True)
    enter_time = models.DateTimeField(auto_now=True, verbose_name='Время захода')
    ip = models.GenericIPAddressField(protocol='both', unpack_ipv4=True)
    forum = models.ForeignKey(Forums, null=True, on_delete=models.PROTECT, related_name='forum_stat_users', blank=True)
    topic = models.ForeignKey(Topics, null=True, on_delete=models.PROTECT, related_name='topic_stat_users', blank=True)


    def __str__(self):
        return self.ip

    class Meta:
        db_table = 'statusers'
        verbose_name_plural = 'Статистика пользователей на сайте'
        verbose_name = 'Статистика пользователей на сайте'
        ordering = ['-enter_time']
        unique_together = ['ip','user']