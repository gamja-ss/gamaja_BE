from django.urls import path

from . import views

urlpatterns = [
    path(
        "guestbook/create/",
        views.CreateGuestbookView.as_view(),
        name="create-guestbook",
    ),
    path(
        "guestbook/update/<int:id>/",
        views.UpdateGuestbookView.as_view(),
        name="update-guestbook",
    ),
    path(
        "guestbook/delete/guest/<int:id>/",
        views.DeleteGuestbookByGuestView.as_view(),
        name="delete-guestbook-guest",
    ),
    path(
        "guestbook/delete/host/<int:id>/",
        views.DeleteGuestbookByHostView.as_view(),
        name="delete-guestbook-host",
    ),
    path("guestbook/list/", views.ListGuestbookView.as_view(), name="list-guestbook"),
]
