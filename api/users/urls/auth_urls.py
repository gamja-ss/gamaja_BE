from django.urls import path
from users.views import user_auth_views

urlpatterns = [
    path("login/", user_auth_views.GithubLogin.as_view(), name="login"),
    path(
        "login/callback/",
        user_auth_views.GithubLoginCallback.as_view(),
        name="login-callback",
    ),
    path(
        "token/verify/",
        user_auth_views.UserTokenVerifyView.as_view(),
        name="token_verify",
    ),
    path(
        "token/refresh/",
        user_auth_views.UserTokenRefreshView.as_view(),
        name="token_refresh",
    ),
    path("logout/", user_auth_views.UserLogoutView.as_view(), name="user_logout"),
    path("delete/", user_auth_views.UserDeleteView.as_view(), name="user_delete"),
]
