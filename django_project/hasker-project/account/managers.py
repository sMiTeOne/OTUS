from django.contrib.auth.models import UserManager as BaseUserManager


class UserManager(BaseUserManager):
    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.prefetch_related("questions")
        return queryset
