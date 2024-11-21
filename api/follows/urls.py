from django.urls import path

from . import views

urlpatterns = [
    path("search/", views.UserSearchView.as_view(), name="user-search"),
    path("follow/<str:nickname>/", views.FollowView.as_view(), name="follow"),
    path("unfollow/<str:nickname>/", views.UnfollowView.as_view(), name="unfollow"),
    path(
        "remove/<str:nickname>/",
        views.RemoveFollowerView.as_view(),
        name="remove-follower",
    ),
    path(
        "follower/<str:nickname>/",
        views.UserFollowerListView.as_view(),
        name="follower-list",
    ),
    path(
        "following/<str:nickname>/",
        views.UserFollowingListView.as_view(),
        name="following-list",
    ),
    path("follower/", views.OwnFollowerListView.as_view(), name="own-follower-list"),
    path("following/", views.OwnFollowingListView.as_view(), name="own-following-list"),
]
