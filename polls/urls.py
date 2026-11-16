
from django.urls import path

from . import views

app_name = "polls"

urlpatterns = [
    path("", views.index, name="index"),
    path("<int:question_id>/", views.detail, name="detail"),
    path("<int:question_id>/results/", views.results, name="results"),
    path("<int:question_id>/vote/", views.vote, name="vote"),
    path(
        "<int:question_id>/comment/",
        views.add_comment,
        name="add_comment",
    ),
    path(
        "comment/<int:comment_id>/edit/",
        views.edit_comment,
        name="edit_comment",
    ),
    path(
        "comment/<int:comment_id>/delete/",
        views.delete_comment,
        name="delete_comment",
    ),
    path("upload/", views.upload_file, name="upload_file"),
    path("weather/", views.weather, name="weather"),
]
