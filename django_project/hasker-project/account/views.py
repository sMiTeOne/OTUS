from django.urls import reverse_lazy
from hasker.mixins import UnauthenticatedOnlyMixin
from account.models import User
from django.views.generic import (
    CreateView,
    UpdateView,
)
from django.contrib.auth.mixins import LoginRequiredMixin

from .forms import (
    SignupForm,
    AccountSettingsForm,
)


class AccountSettings(LoginRequiredMixin, UpdateView):
    model = User
    form_class = AccountSettingsForm
    template_name = "registration/account.html"
    success_url = reverse_lazy("account")

    def get_object(self):
        return self.request.user


class SignUp(UnauthenticatedOnlyMixin, CreateView):
    form_class = SignupForm
    success_url = reverse_lazy("login")
    template_name = "registration/signup.html"
