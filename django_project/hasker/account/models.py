from account.managers import UserManager
from django.db.models import ImageField
from django.contrib.auth.models import UserManager as BaseUserManager
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    avatar = ImageField(upload_to="avatars/", blank=True)
    objects = BaseUserManager()
    users = UserManager()

    def __str__(self):
        return self.username
