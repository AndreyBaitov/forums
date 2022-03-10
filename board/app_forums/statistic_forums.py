'''Собирает статистику форумов для выдачи их на главной странице'''

import time
from collections import namedtuple
from django.db.models import Max

def clock():
    '''Возврашает время в формате 12:54. Вынесено в отдельную функцию, чтобы не тащить сбор всей статистики в других обращениях'''
    today = time.gmtime(time.time() - time.timezone)
    return time.strftime('%H:%M',today)

def date():
    '''Вовзрашает дату в формате Понедельник, 5 марта 2022'''
    today = time.gmtime(time.time())
    year = today[0]
    month = today[1]
    day = today[2]
    day_week = today[6]
    month_name = ['месяц','января','февраля','марта','апреля','мая','июня','июля','августа','сентября','октября','ноября','декабря']
    day_week_name = ['Понедельник', 'Вторник', 'Среда', 'Четверг','Пятница', 'Суббота', 'Воскресенье']
    month = month_name[month]
    day_week = day_week_name[day_week]
    return day_week + ', ' + str(day) + ' ' + month + ' ' + str(year)

def last_enter_datetime(user_last_activity):
    '''Вовзрашает дату и время в формате ('Понедельник, 5 марта 2022', '17:20') '''
    ula = user_last_activity  # для сушки кода
    # преобразовываем хранимый в базе формат даты и времени в struct_time формат
    when_is_done = namedtuple('overdue_time', 'tm_year tm_mon tm_mday tm_hour tm_min tm_sec tm_wday tm_yday tm_isdst')
    when_is_done = time.mktime(when_is_done(tm_year=ula.year, tm_mon=ula.month, tm_mday=ula.day, tm_hour=ula.hour, tm_min=ula.minute,
                     tm_sec=ula.second, tm_wday=0, tm_yday=0, tm_isdst=0))
    this_day = time.gmtime(when_is_done - time.timezone)
    year = this_day[0]
    month = this_day[1]
    day = this_day[2]
    day_week = this_day[6]
    month_name = ['месяц','января','февраля','марта','апреля','мая','июня','июля','августа','сентября','октября','ноября','декабря']
    day_week_name = ['Понедельник', 'Вторник', 'Среда', 'Четверг','Пятница', 'Суббота', 'Воскресенье']
    month = month_name[month]
    day_week = day_week_name[day_week]
    last_enter_time = time.strftime('%H:%M', this_day)
    last_enter_date = day_week + ', ' + str(day) + ' ' + month + ' ' + str(year)
    return (last_enter_time, last_enter_date)





class CollectStatisticForums:
    '''Возвращает словарь данных в атрибуте data'''

    def __init__(self):
        self.data = {}
        self.data['date'] = date()
        self.data['time'] = clock()
        self.clean_db_stat()       # очистка базы от старых записей
        self.data['users'] = self.users()
        self.data['guests'] = self.guests()
        self.data['auth_users'] = self.data['users'] - self.data['guests']
        self.data['hidd_users'] = self.hidd_users()
        self.data['total_messages'] = self.total_messages()
        self.data['total_topics'] = self.total_topics()
        self.data['total_users'] = self.total_users()
        self.data['new_user'] = self.new_user()
        self.data['list_max_acknowledgements'] = self.list_max_acknowledgements()

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
                    print(user.user.last_activity)
                user.delete()

    def users(self):
        '''Возвращает число всех авторизованных пользователей'''
        from app_forums.models import StatUsers  # импортируем здесь, иначе взаимная блокировка импортов
        return StatUsers.objects.count()

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
    print(stat.date())
    print(stat.time())