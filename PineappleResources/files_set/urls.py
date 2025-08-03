from django.urls import path, re_path

from .views import (
    FileUploadView, FileRetrieveView, FileDeleteView, FileListView
)

urlpatterns = [
    re_path(r"^upload/$", FileUploadView.as_view(), name="file-upload"),
    re_path(r"^(?P<pk>[0-9A-Za-z_-]{22})/$", FileRetrieveView.as_view(), name="file-retrieve"),
    re_path(r"^(?P<pk>[0-9A-Za-z_-]{22})/delete/$", FileDeleteView.as_view(), name="file-delete"),
    re_path(r"list/$", FileListView.as_view(), name="file-list"),
]
