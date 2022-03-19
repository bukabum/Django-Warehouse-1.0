from django.urls import path, re_path
from .views import *
from django.conf.urls import include, url
from django.urls import path, include
from rest_framework import routers
from rest_framework_simplejwt.views import *
from rest_framework_simplejwt import views as jwt_views

urlpatterns = [

    path('category/', category, name="category"),
    path('new/sparepart/', new_sparepart, name="new_sparepart"),
    path('customer/detail/<int:pk>/', customer_detail, name="customer_detail"),
    path('view/sparepart/<int:pk>/', view_sparepart, name="view_sparepart"),
    path('api/token/', jwt_views.TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', jwt_views.TokenRefreshView.as_view(), name='token_refresh'),
    path('new/customer/', new_customer, name="new_customer"),
    path('stock/in/<int:pk>/', stock_in, name="stock_in"),
    path('stock/out/<int:pk>/', stock_out, name="stock_out"),
    path('monthly/stock/<int:pk>/', monthly_stock, name="monthly_stock"),
    path('all/history/stock/<int:pk>/', all_history_stock, name="all_history_stock"),
    path('add/to/cart/<int:pk>/', add_to_cart, name="add_to_cart"),
    path('edit/cart/<int:pk>/', edit_cart, name="edit_cart"),
    path('view/cart/', view_cart, name="view_cart"),
    path('post/cart/', post_cart, name="post_cart"),
    path('order/detail/<int:pk>/', order_detail, name="order_detail"),
    path('invoice/<int:pk>/', invoice, name="invoice"),
    path('note/order/<int:pk>/', note_order, name="note_order"),
    path('cancel/order/<int:pk>/', cancel_order, name="cancel_order"),
    path('return/order/<int:pk>/', return_order, name="return_order"),
    path('down/payment/order/<int:pk>/', down_payment, name="down_payment"),
    path('full/paid/<int:pk>/', full_paid, name="full_paid"),
    path('all/customer/', all_customer, name="all_customer"),
    path('bulk/all/sparepart/', all_sparepart, name="all_sparepart"),
    path('bulk/in/', bulk_in, name="bulk_in"),
    path('bulk/out/', bulk_out, name="bulk_out"),
    path('bulk/out/', bulk_out, name="bulk_out"),
    path('bulk/out/', bulk_out, name="bulk_out"),
    path('bulk/cart/', bulk_cart, name="bulk_cart"),
    path('pre/order/<int:pk>/', pre_order, name="pre_order"),
    path('delete/note/order/<int:pk>/', delete_note_order, name="delete_note_order"),
    path('blacklist/', LogoutAndBlacklistRefreshTokenForUserView.as_view(), name='blacklist'),

#################### List View #################### 

    path('all/sparepart/', SparePartListView.as_view()),
    path('view/all/customer/', CustomerListView.as_view()),
    path('view/customer/order/history/<int:pk>/', CustomerHistoryOrderListView.as_view()),
    path('view/all/history/<int:pk>/', AllHistoryListView.as_view()),
    path('view/all/order/', OrderListView.as_view()),

#################### List View #################### 

]