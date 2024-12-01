from django.urls import path

from . import views

urlpatterns = [
    path(
        "create/",
        views.CreateGuestbookView.as_view(),
        name="create-guestbook",
    ),
    path(
        "update/<int:id>/",
        views.UpdateGuestbookView.as_view(),
        name="update-guestbook",
    ),
    path(
        "delete/<int:id>/",
        views.DeleteGuestbookView.as_view(),
        name="delete-guestbook",
    ),
    path(
        "list/<str:nickname>/",
        views.ListGuestbookView.as_view(),
        name="list-guestbook",
    ),
]
