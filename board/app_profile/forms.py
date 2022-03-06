from django import forms
import datetime
from django.core.exceptions import ValidationError
from app_profile.models import *

class UserForm(forms.ModelForm):

    class Meta:
        model = Users
        fields = ['username','password','first_name','second_name','last_name','email','birthday','region']


    # записи, если наследоваться от forms.Form
    # username = forms.CharField()
    # password = forms.CharField()
    # first_name = forms.CharField()
    # second_name = forms.CharField()
    # last_name = forms.CharField()
    # email = forms.EmailField()
    # birthday = forms.DateField()

    # Методы самостоятельной валидации полей
    # def clean_birthday(self):
    #     '''Проверка только 1 поля по названию функции "clean_" регистрируемого пользователя'''
    #     data = self.cleaned_data['birthday']
    #     today = datetime.date.today()
    #     age = (today - data).days / 365
    #     if age < 18:
    #         raise ValidationError('Регистрироваться могут только люди старше 18 лет')
    #     return data
    #
    # def clean(self):
    #     '''Проверка всех полей, но после автопроверки самого джанго'''
    #     cleaned_data = super(UserForm,self).clean()  # проверка самого джанго
    #     first_name = cleaned_data.get('first_name')
    #     second_name = cleaned_data.get('second_name')
    #     if first_name == 'Иван' and second_name == 'Иванов':
    #         msg = 'Иванам Ивановым регистрироваться запрещено!'
    #         self.add_error('first_name',msg)
    #         self.add_error('second_name', msg)
    #     return cleaned_data

class AuthForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)


