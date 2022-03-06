from django.db import models

class Users(models.Model):
    '''Класс пользователей'''
    STATUS_CHOICE = [('admin', 'admin'), ('redactor', 'redactor'),('simple_user', 'simple_user')]
    username = models.CharField(max_length=20, unique=True, db_index=True, verbose_name='Ник на форуме')
    password = models.CharField(max_length=20, verbose_name='Пароль')
    first_name = models.CharField(max_length=20, verbose_name='Имя')
    second_name = models.CharField(max_length=20, null=True, verbose_name='Отчетство')
    last_name = models.CharField(max_length=30, verbose_name='Фамилия')
    email = models.EmailField(verbose_name='Электронная почта', unique=True)
    birthday = models.DateField(verbose_name='День рождения')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата регистрации')
    status = models.CharField(max_length=20, choices=STATUS_CHOICE, default='simple_user')
    region = models.ForeignKey('Regions', null=True, on_delete=models.PROTECT,
                                related_name='regions', blank=True)
    ninja = models.BooleanField(verbose_name='Скрытность пользователя', default=False)

    def __str__(self):
        return self.username

    class Meta:
        db_table = 'users'
        verbose_name_plural = 'Пользователи'
        verbose_name = 'Пользователь'
        ordering = ['-created_at']

class Regions(models.Model):
    '''Регионы, откуда пользователи'''
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'Регионы'
        verbose_name = 'Регион'
        ordering = ['name']
