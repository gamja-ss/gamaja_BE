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
        "delete/guest/<int:id>/",
        views.DeleteGuestbookByGuestView.as_view(),
        name="delete-guestbook-guest",
    ),
    path(
        "delete/host/<int:id>/",
        views.DeleteGuestbookByHostView.as_view(),
        name="delete-guestbook-host",
    ),
    path("list/", views.ListGuestbookView.as_view(), name="list-guestbook"),
]
