from django.urls import path
from . import views

urlpatterns = [
    path('forums/',views.ForumsView.as_view(), name='forums'),
    path('forum/<int:pk>/', views.ForumDetailView.as_view(), name='forum'),
    path('topic/<int:pk>/', views.TopicDetailView.as_view(), name='topic'),
    path('topic/<int:pk>/add-message/', views.MessageAddView.as_view(), name='add-message'),
    path('forum/<int:pk>/add-topic/', views.TopicAddView.as_view(), name='add-topic'),
    path('edit-message/<int:msg_id>/', views.MessageEditView.as_view(), name='edit-message'),
    path('delete-message/<int:msg_id>/', views.MessageDeleteView.as_view(), name='delete-message'),
    path('thank-message/<int:pk>/', views.thanks, name='thank-message'),
    path('undo-thank-message/<int:pk>/', views.undo_thanks, name='undo-thank-message'),
]
