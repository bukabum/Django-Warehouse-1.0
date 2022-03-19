"""warehouse URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from sparepart.views import *
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls import include
from restframework import urls
urlpatterns = [
    path('rest/', include('restframework.urls')),

    path('accounts/', include('django.contrib.auth.urls')),
    path('admin/', admin.site.urls),
    path('', product_list, name='product_list'),
    path('add/product/', add_product, name='add_product'),
    path('view/product/<int:pk>/', view_saprepart, name='view_saprepart'),
    #path('delete/product/<int:pk>/', delete_product, name='delete_product'),
    path('update/product/<int:pk>/', update_product, name='update_product'),
    path('increase/product/stock/<int:pk>/', stock_in, name='stock_in'),
    path('decrease/product/stock/<int:pk>/', stock_out, name='stock_out'),
    path('increase/product/stock/bulk/', stock_in_bulk, name='stock_in_bulk'),
    path('stock/history/<int:pk>/', stock_history, name='stock_history'),
    path('all/stock/history/<int:pk>/', all_stock_history, name='all_stock_history'),
    path('add/to/cart/<int:pk>/', add_to_cart, name='add_to_cart'),
    path('cart/', cart, name='cart'),
    path('update/cart/<int:pk>/', update_cart, name='update_cart'),
    path('request/order/', request_order, name='request_order'),
    path('list/order/', list_order, name='list_order'),
    path('view/order/<int:pk>/', view_order, name='view_order'),
    path('return/order/<int:pk>/', return_order, name='return_order'),
    path('cancel/order/<int:pk>/', cancel_order, name='cancel_order'),
    path('invoice/<int:pk>/', invoice, name='invoice'),
    path('pdf/receipt/<int:pk>/', pdf_receipt, name='pdf_receipt'),
    path('upload/payment/<int:pk>/', upload_payment_proof, name='upload_payment_proof'),
    path('update/user/profile/<int:pk>/', update_user_profile, name='update_user_profile'),
    path('remove/from/cart/<int:pk>/', remove_from_cart, name='remove_from_cart'),
    path('list/customer/', list_customer, name='list_customer'),
    path('create/customer/', create_customer, name='create_customer'),
    path('view/customer/<int:pk>/', view_customer, name='view_customer'),
]
if settings.DEBUG: 
        urlpatterns += static(settings.MEDIA_URL, 
                              document_root=settings.MEDIA_ROOT) 
