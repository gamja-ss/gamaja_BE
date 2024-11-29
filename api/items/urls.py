from django.urls import path

from .views.admin_item_views import (
    AdminItemDetailView,
    AdminItemImageUploadView,
    AdminItemListView,
)
from .views.user_item_views import (
    ItemDetailView,
    ItemListView,
    ItemPurchaseView,
    UserItemPurchaseLogView,
)

urlpatterns = [
    path("admin/", AdminItemListView.as_view(), name="admin_item_list"),
    path(
        "admin/<int:item_id>/image/",
        AdminItemImageUploadView.as_view(),
        name="item_admin_image_upload",
    ),
    path(
        "admin/<int:item_id>/", AdminItemDetailView.as_view(), name="admin_item_detail"
    ),
    path("shop/", ItemListView.as_view(), name="item_list"),
    path("shop/<int:item_id>/", ItemDetailView.as_view(), name="item_detail"),
    path(
        "shop/<int:item_id>/purchase/", ItemPurchaseView.as_view(), name="item_purchase"
    ),
    path(
        "shop/purchase/",
        UserItemPurchaseLogView.as_view(),
        name="user_item_purchase_log",
    ),
]
