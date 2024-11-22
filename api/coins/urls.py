from django.urls import path

from .views import UserCoinLogView, UserTotalCoinsView

urlpatterns = [
    path("total/", UserTotalCoinsView.as_view(), name="user-total-coins"),
    path("log/", UserCoinLogView.as_view(), name="user-coin-log"),
]
