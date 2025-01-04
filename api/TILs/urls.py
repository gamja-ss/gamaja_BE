from django.urls import path

from .views import (
    CreateTILView,
    DeleteTempImagesView,
    DeleteTILView,
    TILDetailView,
    TILListView,
    UpdateTILView,
    UploadTempImagesView,
)

urlpatterns = [
    path("upload/images/", UploadTempImagesView.as_view(), name="upload_temp_images"),
    path("delete/images/", DeleteTempImagesView.as_view(), name="delete_temp_images"),
    path("create/", CreateTILView.as_view(), name="create-til"),
    path("update/<int:pk>/", UpdateTILView.as_view(), name="update-til"),
    path("delete/<int:pk>/", DeleteTILView.as_view(), name="delete-til"),
    path("list/<str:nickname>/", TILListView.as_view(), name="til-list"),
    path("<int:id>/", TILDetailView.as_view(), name="til-detail"),
]
