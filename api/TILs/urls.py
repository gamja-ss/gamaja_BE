from django.urls import path

from .views import (
    CreateTILAPI,
    DeleteTempImageAPI,
    DeleteTILAPI,
    UpdateTILAPI,
    UploadTempImageAPI,
)

urlpatterns = [
    path("upload/image/", UploadTempImageAPI.as_view(), name="upload_temp_image"),
    path("delete/image", DeleteTempImageAPI.as_view(), name="delete_temp_image"),
    path("create/", CreateTILAPI.as_view(), name="create-til"),
    path("update/<int:pk>/", UpdateTILAPI.as_view(), name="update-til"),
    path("delete/<int:pk>/", DeleteTILAPI.as_view(), name="delete-til"),
]
