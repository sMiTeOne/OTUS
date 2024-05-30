import qa.views
from django.conf import settings
from django.urls import (
    path,
    include,
)
from django.contrib import admin
from django.conf.urls.static import static

urlpatterns = [
    path("", qa.views.ShowQuestions.as_view(), name="index"),
    path("account/", include("account.urls")),
    path("search/", include("search.urls")),
    path("qa/", include("qa.urls")),
    path("admin/", admin.site.urls),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
