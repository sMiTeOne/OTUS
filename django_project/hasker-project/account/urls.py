from django.urls import path
from django.contrib.auth.views import (
    LoginView,
    LogoutView,
)

from .views import (
    SignUp,
    AccountSettings,
)

urlpatterns = [
    path("signup/", SignUp.as_view(), name="signup"),
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(next_page="index"), name="logout"),
    path("", AccountSettings.as_view(), name="account"),
]
