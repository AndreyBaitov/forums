from django.contrib import admin

from .models import *

class UsersAdmin(admin.ModelAdmin):
    '''Админка пользователей'''
    # list_display = ['id', 'username', 'password', 'first_name','second_name','last_name','avatar','birthday','region', 'email', 'status', 'created_at','ninja','last_activity','msgs','acknowledgements']
    list_filter = ['status']  # справа будет возможность выбрать фильтрацию по всем возможным статусам
    fieldsets = (('Данные для логина',{'fields': ('username','password')}),
                 ('Форумные данные',{'fields': ('status','ninja','user','acknowledgements','thanks', 'last_activity','avatar','msgs'), 'description': 'Форумные данные пользователя'}),
                 ('Личные данные', {'fields':('first_name','second_name','last_name','region'), 'description':'Личные данные пользователя'}),
                 ('Контактные данные', {'fields':('email','birthday'),'classes':['collapse']}),
    )
    # list_editable = ['email']
    readonly_fields = ['last_activity']
    list_per_page = 10

class RegionsAdmin(admin.ModelAdmin):
    '''Админка регионов'''
    list_display = ['id','name']

admin.site.register(Users, UsersAdmin)
admin.site.register(Regions, RegionsAdmin)