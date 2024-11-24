from django.urls import path

from .views import CreateTILAPI, DeleteTILAPI, UpdateTILAPI

urlpatterns = [
    path("create/", CreateTILAPI.as_view(), name="create-til"),
    path("update/<int:pk>/", UpdateTILAPI.as_view(), name="update-til"),
    path("delete/<int:pk>/", DeleteTILAPI.as_view(), name="delete-til"),
]
