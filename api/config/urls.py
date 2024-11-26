from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

urlpatterns = [
    path("admin/", admin.site.urls),
    # openapi
    path("schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "schema/swagger-ui/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    path(
        "schema/redoc/",
        SpectacularRedocView.as_view(url_name="schema"),
        name="redoc",
    ),
    # apps
    path("auth/", include("users.urls.auth_urls")),
    path("info/", include("users.urls.profile_urls")),
    path("info/", include("users.urls.info_urls")),
    path("github/", include("githubs.urls")),
    path("baekjoon/", include("baekjoons.urls")),
    path("programmers/", include("programmers.urls")),
    path("stack/", include("stacks.urls")),
    path("attendance/", include("attendances.urls")),
    path("follow/", include("follows.urls")),
    path("guestbook/", include("guestbooks.urls")),
    path("potato/", include("potatoes.urls")),
    path("coin/", include("coins.urls")),
    path("til/", include("TILs.urls")),
    path("item/", include("items.urls")),
]
