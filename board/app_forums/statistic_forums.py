'''Собирает статистику форумов для выдачи их на главной странице'''

import time

class CollectStatisticForums:
    '''Возвращает словарь данных в атрибуте data'''
    def __init__(self):
        self.data = {}
        self.data['date'] = self.date()
        self.data['time'] = self.time()
        # self.data['auth_users'] = self.auth_users()
        # self.data['hidd_users'] = self.hidd_users()
        # self.data['guests'] = self.guests()
        # self.data['users'] = self.data['guests'] + self.data['hidd_users'] + self.data['auth_users']
        # self.data['total_messages'] = self.total_messages()
        # self.data['total_topics'] = self.total_topics()
        # self.data['total_users'] = self.total_users()
        # self.data['new_user'] = self.new_user()

    def date(self):
        '''Вовзрашает дату'''
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

    def time(self):
        '''Вовзрашает время'''
        today = time.gmtime(time.time()-time.timezone)
        hour = today[3]
        minute = today[4]
        return str(hour) + ':' + str(minute)

    def auth_users(self):
        '''Возвращает число всех авторизованных пользователей'''

if __name__ == '__main__':
    stat = CollectStatisticForums()
    print(stat.date())
    print(stat.time())
