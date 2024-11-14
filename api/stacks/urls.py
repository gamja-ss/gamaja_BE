from django.urls import path

from .views import StackListView

urlpatterns = [
    path("", StackListView.as_view(), name="stack-list"),
]
