from django import forms
from app_forums.models import *

class TopicForm(forms.ModelForm):

    class Meta:
        model = Topics
        fields = []  # Чтобы не было дубляжа title с сообщением при создании новой темы. В соответствующем виде они приравниваются


class MessageForm(forms.ModelForm):

    class Meta:
        model = Messages
        fields = ['title', 'message']