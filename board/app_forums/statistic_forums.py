'''Собирает статистику форумов для выдачи их на главной странице'''

import time, datetime
from collections import namedtuple


class CollectStatisticForums:
    '''Возвращает словарь данных в атрибуте data'''

    def __init__(self):
        self.data = {}

    def run (self):
        self.clean_db_stat()       # очистка базы от старых записей
        self.data['now_users'] = self.now_users()
        self.data['users'] = self.users()
        self.data['guests'] = self.guests()
        self.data['auth_users'] = self.data['now_users'] - self.data['guests']
        self.data['hidd_users'] = self.hidd_users()
        self.data['total_messages'] = self.total_messages()
        self.data['total_topics'] = self.total_topics()
        self.data['total_users'] = self.total_users()
        self.data['new_user'] = self.new_user()
        self.data['list_max_acknowledgements'] = self.list_max_acknowledgements()
        try:
            if self.data['max_users'] < self.data['now_users']:
                self.data['max_users'] = self.data['now_users']
                self.data['datetime_of_max_users'] = datetime.datetime.now()
        except KeyError:
            self.data['max_users'] = self.data['now_users']
            self.data['datetime_of_max_users'] = datetime.datetime.now()
        return self.data

    def clean_db_stat(self):
        '''Проверяет не устарели ли записи в таблице StatUsers'''
        from app_forums.models import StatUsers  # импортируем здесь, иначе взаимная блокировка импортов
        TIME_OF_STATISTIC = 5 * 60  # 5 минут
        now = time.time() # поскольку в базе время хранится в UTC без +3 часа, поэтому тут поправку не делаем
        users = StatUsers.objects.all()
        for user in users:
            uet = user.enter_time  # для сушки кода
            # преобразовываем хранимый в базе формат даты и времени в struct_time формат
            when_is_done = namedtuple('overdue_time', 'tm_year tm_mon tm_mday tm_hour tm_min tm_sec tm_wday tm_yday tm_isdst')
            when_is_done = time.mktime(when_is_done(tm_year=uet.year, tm_mon=uet.month, tm_mday=uet.day, tm_hour=uet.hour, tm_min=uet.minute,
                 tm_sec=uet.second, tm_wday=0, tm_yday=0, tm_isdst=0))
            if when_is_done < (now - TIME_OF_STATISTIC):  # Значит запись уже устарела и её надо удалить
                if user.user:
                    user.user.last_activity = uet
                    user.user.save()
                user.delete()

    def now_users(self):
        '''Возвращает число всех авторизованных пользователей'''
        from app_forums.models import StatUsers  # импортируем здесь, иначе взаимная блокировка импортов
        return StatUsers.objects.count()

    def users(self):
        '''Возвращает список всех авторизованных, но не прячушихся пользователей'''
        from app_forums.models import StatUsers  # импортируем здесь, иначе взаимная блокировка импортов
        users = StatUsers.objects.exclude(user=None).exclude(user__ninja=True)
        return users

    def hidd_users(self):
        '''Возвращает число всех спрятанных пользователей'''
        from app_forums.models import StatUsers  # импортируем здесь, иначе взаимная блокировка импортов
        return len(StatUsers.objects.filter(user__ninja=True))

    def guests(self):
        '''Возвращает число всех незарегистрированных пользователей'''
        from app_forums.models import StatUsers  # импортируем здесь, иначе взаимная блокировка импортов
        return len(StatUsers.objects.filter(user=None))

    def total_messages(self):
        '''Возвращает число всех сообщений на форумах'''
        from app_forums.models import Messages  # импортируем здесь, иначе взаимная блокировка импортов
        return Messages.objects.count()

    def total_topics(self):
        '''Возвращает число всех тем на форумах'''
        from app_forums.models import Topics  # импортируем здесь, иначе взаимная блокировка импортов
        return Topics.objects.count()

    def total_users(self):
        '''Возвращает число всех зарегистрированных на форумах'''
        from app_profile.models import Users  # импортируем здесь, иначе взаимная блокировка импортов
        return Users.objects.count()

    def new_user(self):
        '''Возвращает ник последнего зарегистрированного пользователя'''
        from app_profile.models import Users  # импортируем здесь, иначе взаимная блокировка импортов
        return Users.objects.order_by('created_at').last()

    def list_max_acknowledgements(self):
        '''Возвращает список кортежей имя пользователя/его id/количество спасибо с максимальным количеством благодарностей'''
        from app_profile.models import Users  # импортируем здесь, иначе взаимная блокировка импортов
        res = []
        try:
            users = Users.objects.order_by('acknowledgements')
            for i in range(1,6):
                user = users[len(users)-i]
                res.append((user.username, user.id, user.acknowledgements))
        except Exception as exc:  # если пользователей меньше 5
            pass
        return res

if __name__ == '__main__':
    stat = CollectStatisticForums()