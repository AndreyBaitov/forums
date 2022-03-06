from django.urls import path
from . import views

urlpatterns = [
    path('profile/register/',views.UserFormView.as_view()),
    path('profile/<int:user_id>/edit/', views.UserEditView.as_view()),
    path('login/', views.AuthLogin.as_view()),
    path('logout/', views.MyLogout.as_view()),
]



