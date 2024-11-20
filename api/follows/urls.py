from django.urls import path

from . import views

urlpatterns = [
    path("search/", views.UserSearchAPIView.as_view(), name="user-search"),
    path("follow/<str:nickname>/", views.FollowAPIView.as_view(), name="follow"),
    path("unfollow/<str:nickname>/", views.UnfollowAPIView.as_view(), name="unfollow"),
    path(
        "followers/<str:nickname>/",
        views.UserFollowerListAPIView.as_view(),
        name="followers-list",
    ),
    path(
        "following/<str:nickname>/",
        views.UserFollowingListAPIView.as_view(),
        name="following-list",
    ),
    path(
        "followers/", views.OwnFollowerListAPIView.as_view(), name="own-followers-list"
    ),
    path(
        "following/", views.OwnFollowingListAPIView.as_view(), name="own-following-list"
    ),
]
