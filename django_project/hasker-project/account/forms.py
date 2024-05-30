from django.forms import (
    CharField,
    ModelForm,
)
from django.contrib.auth.forms import UserCreationForm

from .models import User


class SignupForm(UserCreationForm):
    username = CharField(label="Login")
    email = CharField(label="Email")

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2", "avatar")


class AccountSettingsForm(ModelForm):
    username = CharField(label="Login", disabled=True)
    email = CharField(label="Email")

    class Meta:
        model = User
        fields = ("username", "email", "avatar")
