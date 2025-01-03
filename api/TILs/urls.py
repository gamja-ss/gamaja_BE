from django.urls import path

from .views import (
    CreateTILAPI,
    DeleteTempImagesAPI,
    DeleteTILAPI,
    UpdateTILAPI,
    UploadTempImagesAPI,
)

urlpatterns = [
    path("upload/images/", UploadTempImagesAPI.as_view(), name="upload_temp_images"),
    path("delete/images/", DeleteTempImagesAPI.as_view(), name="delete_temp_images"),
    path("create/", CreateTILAPI.as_view(), name="create-til"),
    path("update/<int:pk>/", UpdateTILAPI.as_view(), name="update-til"),
    path("delete/<int:pk>/", DeleteTILAPI.as_view(), name="delete-til"),
]
