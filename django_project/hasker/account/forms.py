from django.forms import (
    CharField,
    ModelForm,
    ImageField,
)
from django.contrib.auth.forms import UserCreationForm

from .models import User


class SignupForm(UserCreationForm):
    avatar = ImageField(label="Фото профиля")

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2", "avatar")


class AccountSettingsForm(ModelForm):
    username = CharField(label="Имя пользователя", disabled=True)
    avatar = ImageField(label="Фото профиля")

    class Meta:
        model = User
        fields = ("username", "email", "avatar")
