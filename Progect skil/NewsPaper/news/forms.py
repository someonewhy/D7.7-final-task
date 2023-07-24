from allauth.account.forms import SignupForm
from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from .models import Post,Author




class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = [ 'author','title', 'content', 'post_type']
        author = forms.ModelChoiceField(queryset=Author.objects.all(), label='Автор')


User = get_user_model()

class BasicSignupForm(SignupForm):
    email = forms.EmailField(label="Email")
    first_name = forms.CharField(label="Имя")
    last_name = forms.CharField(label="Фамилия")

    def save(self, request):
        user = super().save(request)
        basic_group = Group.objects.get(name='common')
        basic_group.user_set.add(user)
        return user
