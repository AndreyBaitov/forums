from django.shortcuts import render
from django.views import View
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth import authenticate,login, logout
from django.contrib.auth.views import LoginView, LogoutView
from app_profile.forms import *
from app_profile.models import *
from django.contrib.auth.models import User

class UserFormView(View):

    def get(self, request):
        user_form = UserForm()
        return render(request,'profile/register.html',context={'user_form':user_form})

    def post(self, request):
        user_form = UserForm(request.POST)
        if user_form.is_valid():
            # регистрируем пользователя
            username = user_form.cleaned_data['username']
            password = user_form.cleaned_data['password']
            email = user_form.cleaned_data['email']
            user_django = User.objects.create_user(username=username,password=password,email=email)
            user_django.save()  # в базе пользователей джанги
            user_form.cleaned_data['user'] = user_django
            Users.objects.create(**user_form.cleaned_data)  # в нашей базе пользователей
            return HttpResponseRedirect('/forums/')
        else:
            return render(request,'profile/register.html',context={'user_form':user_form})

class UserEditView(View):

    def get(self, request, user_id):
        user = Users.objects.get(id=user_id)
        user_form = UserForm(instance=user)
        return render(request,'profile/edit.html',context={'user_form':user_form, 'user_id': user_id})

    def post(self, request, user_id):
        user = Users.objects.get(id=user_id)
        user_form = UserForm(request.POST, instance=user)
        if user_form.is_valid():
            # сохраняем пользователя
            user.save()
        return render(request,'profile/edit.html',context={'user_form':user_form, 'user_id': user_id})

class AuthLogin(LoginView):
    template_name = 'login/login.html'
    extra_context = {'auth_form': AuthForm()}
    redirect_authenticated_user = '/forums/'
    def post(self, request, *args, **kwargs):
        response = super().post(self,request,*args, **kwargs)
        user = Users.objects.filter(username=request.user)  # проверка есть такой пользователь в базе
        if not user:
            return HttpResponseRedirect('/profile/register/')
        return response





def my_logout_view(request):
    logout(request)
    return HttpResponse ('Вы успешно вышли из системы!')



# # def auth_login(request):
# #
# #     if request.method == 'POST':
# #         auth_form = AuthForm(request.POST)
# #         if auth_form.is_valid():
# #             username = auth_form.cleaned_data['username']
# #             password = auth_form.cleaned_data['password']
# #             user = authenticate(username=username,password=password)
# #             if user:
# #                 if user.is_active:
# #                     login(request, user)
# #                     return HttpResponse('Вы успешно зашли в систему!')
# #                 else:
# #                     auth_form.add_error('__all__','Учетная запись не активна!')
# #             else:
# #                 auth_form.add_error('__all__', 'Проверьте правильность логина и пароля!')
# #     else:
# #         auth_form = AuthForm()
# #     return render(request,'login/login.html',{'auth_form': auth_form})
# #
# # def my_logout_view(request):
# #     logout(request)
# #     return HttpResponse ('Вы успешно вышли из системы!')

class MyLogout(LogoutView):
    next_page = '/forums/'