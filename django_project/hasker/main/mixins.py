from django.shortcuts import redirect
from django.contrib.auth.mixins import AccessMixin


class UnauthenticatedOnlyMixin(AccessMixin):
    def dispatch(self, request, *args, **kwargs):
        """

        :param request:
        :type request: HttpRequest
        :param args:
        :param kwargs:
        :return:
        """

        if request.user.is_authenticated:
            return redirect("account")
        return super().dispatch(request, *args, **kwargs)
