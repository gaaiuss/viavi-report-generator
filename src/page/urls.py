from django.urls import path

from page.views import index

app_name = "page"

urlpatterns = [
    path("", index, name="index"),
]
