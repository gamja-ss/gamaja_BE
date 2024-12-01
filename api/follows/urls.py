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
        "followers/<str:nickname>/",
        views.UserFollowersListView.as_view(),
        name="user-followers-list",
    ),
    path(
        "following/<str:nickname>/",
        views.UserFollowingListView.as_view(),
        name="user-following-list",
    ),
    path("followers/", views.OwnFollowersListView.as_view(), name="own-followers-list"),
    path("following/", views.OwnFollowingListView.as_view(), name="own-following-list"),
]
