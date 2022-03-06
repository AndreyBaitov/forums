from django.contrib import admin

from .models import *

class CategoriesAdmin(admin.ModelAdmin):
    '''Админка категорий форумов'''
    list_display = ['id', 'name']

class ForumsAdmin(admin.ModelAdmin):
    '''Админка форумов'''
    list_display = ['id','name','category','status','list_moderators']  # показать в админке только эти поля
    actions = ['mark_as_opened','mark_as_closed','mark_as_hiddened']  # список функций
    list_filter = ['status']  # справа будет возможность выбрать фильтрацию по всем возможным статусам

    def mark_as_opened(self, request, queryset):  # Перевести все выбранные в статус открыто
        queryset.update(status='opened')

    def mark_as_closed(self, request, queryset):
        queryset.update(status='closed')

    def mark_as_hiddened(self, request, queryset):
        queryset.update(status='hiddened')

    mark_as_opened.short_description = 'Открыть форумы'
    mark_as_closed.short_description = 'Закрыть форумы'
    mark_as_hiddened.short_description = 'Спрятать форумы'

class TopicsAdmin(admin.ModelAdmin):
    '''Админка тем'''
    list_display = ['id', 'title', 'forum', 'type', 'status']  # показать в админке только эти поля
    actions = ['mark_as_opened', 'mark_as_closed', 'mark_as_hiddened']  # список функций
    list_filter = ['status','type']  # справа будет возможность выбрать фильтрацию по всем возможным статусам

    def mark_as_opened(self, request, queryset):  # Перевести все выбранные в статус открыто
        queryset.update(status='opened')

    def mark_as_closed(self, request, queryset):
        queryset.update(status='closed')

    def mark_as_hiddened(self, request, queryset):
        queryset.update(status='hiddened')

    mark_as_opened.short_description = 'Открыть темы'
    mark_as_closed.short_description = 'Закрыть темы'
    mark_as_hiddened.short_description = 'Спрятать темы'

# class MessagesInline(admin.TabularInline):
#     '''Чтобы комменты можно было редактировать прямо при редактировании самой темы в админке'''
#     model = Messages

class MessagesAdmin(admin.ModelAdmin):
    '''Админка тем'''
    list_display = ['id', 'title','topic', 'status']  # показать в админке только эти поля
    actions = ['mark_as_editable', 'mark_as_closed', 'mark_as_hiddened', 'admin_deleted']  # список функций
    list_filter = ['status']  # справа будет возможность выбрать фильтрацию по всем возможным статусам
    # inlines = [MessagesInline]

    def mark_as_editable(self, request, queryset):  # Перевести все выбранные в статус editable
        queryset.update(status='editable')

    def mark_as_closed(self, request, queryset):
        queryset.update(status='closed')

    def mark_as_hiddened(self, request, queryset):
        queryset.update(status='hiddened')

    mark_as_editable.short_description = 'Открыть сообщения для редактирования'
    mark_as_closed.short_description = 'Закрыть сообщения'
    mark_as_hiddened.short_description = 'Спрятать сообщения'

    def admin_deleted(self, request, queryset):
        queryset.update(message='Удалено администратором')
    admin_deleted.short_description = 'Заменить текст выбранных сообщений на Удалено администратором'

class StatUsersAdmin(admin.ModelAdmin):
    '''Админка статистики по пользователям'''
    list_display = ['id', 'user','ip', 'enter_time']  # показать в админке только эти поля
    list_filter = ['ip']  # справа будет возможность выбрать фильтрацию по всем возможным статусам

admin.site.register(Forums, ForumsAdmin)
admin.site.register(Categories, CategoriesAdmin)
admin.site.register(Topics, TopicsAdmin)
admin.site.register(Messages, MessagesAdmin)
admin.site.register(StatUsers, StatUsersAdmin)

