from django.urls import path

from . import views

app_name = "wiki"

urlpatterns = [
    path("", views.index, name="index"),
    path("edit/<str:entry>", views.edit, name="edit"),
    path("new", views.new, name="new"),
    path("random", views.random, name="random"),
    path("<str:entry>", views.entry, name="entry")
]
