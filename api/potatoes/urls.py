from django.urls import path

from .views import (
    UserPotatoPresetApplyView,
    UserPotatoPresetCreateView,
    UserPotatoPresetDetailView,
    UserPotatoPresetListView,
    UserPotatoPresetUpdateView,
    UserPotatoView,
)

urlpatterns = [
    path("", UserPotatoView.as_view(), name="user_potato_info"),
    path("preset/", UserPotatoPresetListView.as_view(), name="user_potato_list"),
    path(
        "preset/create/",
        UserPotatoPresetCreateView.as_view(),
        name="user_potato_create",
    ),
    path(
        "preset/<int:preset_id>/",
        UserPotatoPresetDetailView.as_view(),
        name="user_potato_detail",
    ),
    path(
        "preset/<int:preset_id>/update/",
        UserPotatoPresetUpdateView.as_view(),
        name="user_potato_update",
    ),
    path(
        "preset/<int:preset_id>/apply/",
        UserPotatoPresetApplyView.as_view(),
        name="user_potato_apply",
    ),
]
