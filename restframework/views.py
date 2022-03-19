from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from .serializers import *
from rest_framework.permissions import IsAdminUser, BasePermission, IsAuthenticatedOrReadOnly, SAFE_METHODS, AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django_filters.rest_framework import FilterSet, DjangoFilterBackend
from .restpagination import *
from sparepart.filters import *
from rest_framework.generics import ListAPIView, ListCreateAPIView
from rest_framework import generics, status, views, permissions
from rest_framework.parsers import FormParser, MultiPartParser, FileUploadParser
import datetime
from django.contrib.sites.shortcuts import get_current_site
import qrcode
import io
from PIL import Image
from django.core.files.uploadedfile import InMemoryUploadedFile
import PIL
import sys
from django.urls import resolve
from urllib.parse import urlencode
from io import BytesIO
from django.core.files import File
from django.db.models import Count, F, Value
from rest_framework_simplejwt.tokens import RefreshToken

# Create your views here.
@api_view(['GET'])
@permission_classes([AllowAny])
def view_cart(request):
    if request.method == 'GET':
        customer = Customer.objects.all()
        order = Order.objects.get(person_responsible = request.user, request_order = False)
        orderitem = OrderItem.objects.filter(order_id = order.pk, request_order=False, paid=False)
        orderitem_serial = OrderItemSerializer(orderitem, context={'request': request}, many=True)
        customer_serial = CustomerSerializer(customer, context={'request': request}, many=True)
        response = [{'orderitem': orderitem_serial.data}] + [{'customer': customer_serial.data}]
    return Response(response)

@api_view(['GET'])
@permission_classes([AllowAny])
def all_customer(request):
    if request.method == 'GET':
        customer = Customer.objects.all()
        serial = CustomerSerializer(customer, context={'request': request}, many=True)
    return Response(serial.data)

@api_view(['GET'])
@permission_classes([AllowAny])
def all_sparepart(request):
    if request.method == 'GET':
        spare = SparePart.objects.all()
        serial = SparePartSerializer(spare, context={'request': request}, many=True)
    return Response(serial.data)

@api_view(['PUT'])
@permission_classes([AllowAny])
def post_cart(request):
    if request.method == 'PUT':
        data = request.data
        if data['customer']:
            order = Order.objects.get(person_responsible = request.user, request_order=False, paid=False)
            order.request_order = True
            order.discount = data['discount']
            order.person_responsible = request.user
            order.order_code = 1000000 + order.pk
            for orders in order.orderitem_set.all():
                serializers = ReceiptOrderItemSeializer(orders)
                if orders.preorder == False:
                    spare = SparePart.objects.get(pk=orders.parts.pk)
                    spare.stock = spare.stock - int(orders.quantity)
                    spare.save()
                    
                    EnhanceInOutStock.objects.create(
                        parts_id=orders.parts.pk, 
                        description="Penjualan Invoice - " + str(order.order_code), 
                        stockout=orders.quantity, 
                        stock=spare.stock, 
                        stockin=0, 
                        person_responsible_id = request.user, 
                        date_added=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    )

                orders.receipt = serializers.data
                if orders.parts.promo_price > 0 :
                    if orders.discount > 0:
                        price = (int(orders.parts.promo_price) - int(orders.discount)) * int(orders.quantity)
                        orders.total_price = price
                    else:
                        price = (int(orders.parts.promo_price) - int(orders.discount)) * int(orders.quantity)
                        orders.total_price = price
                elif orders.parts.promo_price == 0 :
                    if orders.discount > 0:
                        price = (int(orders.parts.price) - int(orders.discount)) * int(orders.quantity)
                        orders.total_price = price
                    else:
                        price = (int(orders.parts.price) * int(orders.quantity))
                        orders.total_price = price

                orders.save()

            totalprice = order.orderitem_set.all().aggregate(total_price=models.Sum('total_price'))
            order.customer_id = data['customer']
            order.total_amount = totalprice['total_price'] - int(data['discount'])
            order.creation_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            order.save()
            return Response(status=status.HTTP_201_CREATED)
        else:
            res = {"code": 400, "message": "Pilih Pelanggan"}
            return Response(data=res, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT', 'DELETE'])
@permission_classes([AllowAny])
def edit_cart(request, pk):
    if request.method == 'PUT':
        data = request.data
        orderitem = OrderItem.objects.get(pk = pk)
        if data['quantity']:
            if orderitem.preorder:
                orderitem.quantity = data['quantity']
            else:
                if orderitem.parts.stock >= int(data['quantity']):
                    orderitem.quantity = data['quantity']
                else: 
                    res = {"code": 400, "message": "Jumlah barang tidak boleh melebihi ketersediaan stock"}
                    return Response(data=res, status=status.HTTP_400_BAD_REQUEST)

        if data['external_note']:
            orderitem.external_note = data['external_note']
        if data['internal_note']:
            orderitem.internal_note = data['internal_note']
        orderitem.discount = data['discount']
        orderitem.save()
        return Response(status=status.HTTP_201_CREATED)
        #return Response(print(serializer.errors), status=status.HTTP_400_BAD_REQUEST)

    if request.method == 'DELETE':
        orderitem = OrderItem.objects.get(pk = pk).delete()
        return Response(status=status.HTTP_201_CREATED)
        #return Response(print(serializer.errors), status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST', 'DELETE'])
@permission_classes([AllowAny])
def pre_order(request, pk):
    if request.method == 'POST':
        order = Order.objects.filter(person_responsible = request.user, request_order = False)
        spare = SparePart.objects.get(pk = pk)
        if order:
            order_check = Order.objects.get(person_responsible = request.user, request_order = False)
            count_order = order_check.orderitem_set.all().count()
            if count_order < 50:
                orders = Order.objects.get(person_responsible = request.user, request_order = False)
                orderitem = OrderItem.objects.filter(order_id = orders.pk, parts_id = pk, request_order=False, preorder = True, paid=False).exists()
                if orderitem:
                    orders = Order.objects.get(person_responsible = request.user, request_order = False)
                    orderitem = OrderItem.objects.get(order_id = orders.pk, parts_id = pk)
                    orderitem.quantity = orderitem.quantity + 1
                    orderitem.save()
                    return Response(status=status.HTTP_201_CREATED)
                else:
                    if orders:
                        orders = Order.objects.get(person_responsible = request.user, request_order = False)
                        OrderItem.objects.create(
                            preorder = True,
                            order_id = orders.pk, 
                            parts_id = pk, 
                            person_responsible = request.user,
                            creation_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        )
                        #print("Another One")
                        return Response(status=status.HTTP_201_CREATED)
            else:
                res = {"code": 400, "message": "Maximum item di keranjang adalah 25"}
                return Response(data=res, status=status.HTTP_400_BAD_REQUEST)
        else:
            order = Order.objects.create(
                person_responsible = request.user, 
                creation_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            )
            #order.order_code = int(1000000 + order.pk),
            #order.save()
            OrderItem.objects.create(
                preorder = True,
                order_id = order.pk, 
                parts_id = pk, 
                person_responsible = request.user,
                creation_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            )
            print("Second One")
            return Response(status=status.HTTP_201_CREATED)

    else:
        return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST', 'DELETE'])
@permission_classes([AllowAny])
def add_to_cart(request, pk):
    if request.method == 'POST':
        order = Order.objects.filter(person_responsible = request.user, request_order = False)
        spare = SparePart.objects.get(pk = pk)
        if order:
            order_check = Order.objects.get(person_responsible = request.user, request_order = False)
            count_order = order_check.orderitem_set.all().count()
            if count_order < 50:
                orders = Order.objects.get(person_responsible = request.user, request_order = False)
                orderitem = OrderItem.objects.filter(order_id = orders.pk, parts_id = pk, request_order=False, paid=False).exists()
                if orderitem:
                    orders = Order.objects.get(person_responsible = request.user, request_order = False)
                    orderitem = OrderItem.objects.get(order_id = orders.pk, parts_id = pk)
                    if spare.stock == 0:
                        res = {"code": 400, "message": "Stock habis, silahkan lakukan PreOrder"}
                        return Response(data=res, status=status.HTTP_400_BAD_REQUEST)
                    elif orderitem.quantity < spare.stock:
                        orderitem.quantity = orderitem.quantity + 1
                        orderitem.save()
                        return Response(status=status.HTTP_201_CREATED)
                    else:
                        res = {"code": 400, "message": "Jumlah barang dikeranjang tidak boleh melebihi stock"}
                        return Response(data=res, status=status.HTTP_400_BAD_REQUEST)

                else:
                    if orders:
                        orders = Order.objects.get(person_responsible = request.user, request_order = False)
                        if spare.stock == 0:
                            res = {"code": 400, "message": "Stock habis, silahkan lakukan PreOrder"}
                            return Response(data=res, status=status.HTTP_400_BAD_REQUEST)
                        else:
                            OrderItem.objects.create(
                                order_id = orders.pk, 
                                parts_id = pk, 
                                person_responsible = request.user,
                                creation_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            )
                            #print("Another One")
                            return Response(status=status.HTTP_201_CREATED)
            else:
                res = {"code": 400, "message": "Maximum item di keranjang adalah 25"}
                return Response(data=res, status=status.HTTP_400_BAD_REQUEST)
        else:
            order = Order.objects.create(
                person_responsible = request.user, 
                creation_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            )
            #order.order_code = int(1000000 + order.pk),
            #order.save()
            OrderItem.objects.create(
                order_id = order.pk, 
                parts_id = pk, 
                person_responsible = request.user,
                creation_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            )
            print("Second One")
            return Response(status=status.HTTP_201_CREATED)

    else:
        return Response(status=status.HTTP_400_BAD_REQUEST)



@api_view(['GET', 'PUT'])
@permission_classes([AllowAny])
def view_sparepart(request, pk):
    if request.method == 'GET':
        sparepart = SparePart.objects.get(pk=pk)
        category = Category.objects.all()
        
        sparepart_serial = SparePartSerializer(sparepart, context={'request': request})
        category_serializer = CategorySerializer(category, context={'request': request}, many=True)
        
        response = [{'sparepart': sparepart_serial.data}] + [{'category': category_serializer.data}]
        return Response(response)

    if request.method == 'PUT':
        data = request.data
        spare = SparePart.objects.get(pk=pk)
        spare.name = data['name']
        spare.description = data['description']
        spare.price = data['price']
        spare.person_responsible_for_update = request.user
        spare.update_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if data['promo_price']:
            spare.promo_price = data['promo_price']
        else:
            spare.promo_price = 0
        if data['category']:
            category = Category.objects.get(name=data['category'])
            spare.category_id = category.pk
            spare.product_code = category.code + str(spare.id + 1000000)
        current_site = get_current_site(request)
        img = qrcode.make(current_site.domain+'/view/product/'+str(spare.id)+'/')
        type(img)  
        image_io = BytesIO()
        filenamme = spare.name + str(spare.id) + str(datetime.date.today())
        img.save(image_io, 'JPEG')
        spare.qrcode.save(filenamme, File(image_io), save = False)
        spare.save()
        return Response(status=status.HTTP_201_CREATED)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def new_sparepart(request):
    if request.method == 'POST':
        data=request.data
        spare = SparePart.objects.create(
            name = data['name'],
            description = data['description'],
            stock = data['first_stock'],
            price = data['price'],
            image = data['image'],
            category_id = data['category'],
            date_added = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            person_responsible = request.user,
            first_stock = data['first_stock'],
        )
        category = Category.objects.get(pk=data['category'])
        current_site = get_current_site(request)
        img = qrcode.make(current_site.domain+'/view/product/'+str(spare.id)+'/')
        type(img)  
        image_io = BytesIO()
        filenamme = spare.name + str(spare.id) + str(datetime.date.today())
        img.save(image_io, 'JPEG')
        spare.qrcode.save(filenamme, File(image_io), save = False)
        #spare.qrcode_s3 = spare.qrcode
        spare.product_code = category.code + str(spare.id + 1000000)
        spare.save()
        return Response(status=status.HTTP_201_CREATED)
        
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def new_customer(request):
    if request.method == 'POST':
        data=request.data
        Customer.objects.create(creation_date=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            nama_pelanggan=data['nama_pelanggan'], 
            alamat=data['alamat'], 
            no_hp=data['no_hp'], 
            kota=data['kota'], 
            provinsi=data['provinsi'], 
            catatan=data['catatan'], 
            person_responsible=request.user)            
        return Response(status=status.HTTP_201_CREATED)

        #return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def new_customer(request):
    if request.method == 'POST':
        data=request.data
        Customer.objects.create(creation_date=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            nama_pelanggan=data['nama_pelanggan'], 
            alamat=data['alamat'], 
            no_hp=data['no_hp'], 
            kota=data['kota'], 
            provinsi=data['provinsi'], 
            catatan=data['catatan'], 
            person_responsible=request.user)            
        return Response(status=status.HTTP_201_CREATED)

        #return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def stock_in(request, pk):
    if request.method == 'POST':
        data=request.data
        spare = SparePart.objects.get(pk = pk)
        spare.stock = spare.stock + int(data['stockin'])
        spare.save()
        EnhanceInOutStock.objects.create(
            stockin = data['stockin'], 
            stockout = 0,
            stock = spare.stock,
            description = data['description'], 
            date_added = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 
            parts_id = pk,
            person_responsible = request.user
        )
        return Response(status=status.HTTP_201_CREATED)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def stock_out(request, pk):
    if request.method == 'POST':
        data=request.data
        print(data)
        spare = SparePart.objects.get(pk = pk)
        spare.stock = spare.stock - int(data['stockout'])
        spare.save()
        EnhanceInOutStock.objects.create(
            stockin = 0, 
            stockout = data['stockout'],
            stock = spare.stock,
            description = data['description'], 
            date_added = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 
            parts_id = pk,
            person_responsible = request.user
        )
        return Response(status=status.HTTP_201_CREATED)

@api_view(['GET'])
@permission_classes([AllowAny])
def category(request):
    category = Category.objects.all()
    serializer = CategorySerializer(category, context={'request': request}, many=True)
    return Response(serializer.data)

class SparePartListView(generics.ListAPIView):
    permission_classes = (permissions.AllowAny,)
    serializer_class = SparePartSerializer
    pagination_class = FullPagination
    pagination_class.page_size = 20
    filter_class = RestSparePartFilter
    filter_backends = (DjangoFilterBackend, )

    def get_queryset(self):
        queryset = SparePart.objects.all().order_by('-date_added')
        return queryset

class CustomerListView(generics.ListAPIView):
    permission_classes = (permissions.AllowAny,)
    serializer_class = CustomerSerializer
    pagination_class = FullPagination
    pagination_class.page_size = 20
    filter_class = RestCustomerFilter
    filter_backends = (DjangoFilterBackend, )

    def get_queryset(self):
        queryset = Customer.objects.all().order_by('-creation_date')
        return queryset

@api_view(['GET', 'PUT'])
@permission_classes([IsAuthenticated])
def customer_detail(request, pk):
    if request.method == 'GET':
        customer = Customer.objects.get(pk=pk)
        serializer = CustomerSerializer(customer, context={'request': request})
        return Response(serializer.data)
    
    if request.method == 'PUT':
        data = request.data
        print(data)
        customer = Customer.objects.get(pk=pk)
        customer.nama_pelanggan = data['nama_pelanggan']
        customer.no_hp = data['no_hp']
        customer.alamat = data['alamat']
        #customer.kecamatan = data['kecamatan']
        customer.kota = data['kota']
        customer.provinsi = data['provinsi']
        customer.catatan = data['catatan']
        customer.save()
    return Response(status=status.HTTP_201_CREATED)


class CustomerHistoryOrderListView(generics.ListAPIView):
    permission_classes = (permissions.AllowAny,)
    serializer_class = OrderSerializer
    pagination_class = FullPagination
    pagination_class.page_size = 20
    filter_class = RestOrderFilter
    filter_backends = (DjangoFilterBackend, )

    def get_queryset(self):
        queryset = Order.objects.filter(customer = self.kwargs['pk']).order_by('-creation_date')
        return queryset

class AllHistoryListView(generics.ListAPIView):
    permission_classes = (permissions.AllowAny,)
    serializer_class = EnhanceInOutStockSerializer
    pagination_class = FullPagination
    pagination_class.page_size = 20
    filter_class = RestStockFilter
    filter_backends = (DjangoFilterBackend, )

    def get_queryset(self):
        queryset = EnhanceInOutStock.objects.filter(parts=self.kwargs['pk']).order_by('-date_added')
        #queryset = EnhanceInOutStock.objects.all()
        return queryset

class OrderListView(generics.ListAPIView):
    permission_classes = (permissions.AllowAny,)
    serializer_class = BaseOrderSerializer
    pagination_class = FullPagination
    pagination_class.page_size = 20
    filter_class = RestOrderFilter
    filter_backends = (DjangoFilterBackend, )

    def get_queryset(self):
        #queryset = Order.objects.filter(person_responsible = self.request.user).order_by('-creation_date')
        queryset = Order.objects.filter(person_responsible = self.request.user, request_order = True).order_by('-creation_date')
        #queryset = Order.objects.all().order_by('-creation_date')
        return queryset

@api_view(['GET'])
@permission_classes([AllowAny])
def all_history_stock(request, pk):
    stock = EnhanceInOutStock.objects.filter(parts = pk).order_by('-date_added')
    serializer = EnhanceInOutStockSerializer(stock, context={'request': request}, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([AllowAny])
def monthly_stock(request, pk):
    today = datetime.date.today()
    part = SparePart.objects.get(pk = pk)
    stock = EnhanceInOutStock.objects.filter(parts = pk, date_added__month=today.month).order_by('-date_added')
    stock_serial = EnhanceInOutStockSerializer(stock, context={'request': request}, many=True)
    part_serial = SparePartSerializer(part, context={'request': request})
    
    response = [{'stock': stock_serial.data}] + [{'sparepart': part_serial.data}]

    return Response(response)

@api_view(['GET'])
@permission_classes([AllowAny])
def order_detail(request, pk):
    order = Order.objects.get(pk = pk)
    orderitem = OrderItem.objects.filter(order = order)
    payment = DownPayment.objects.filter(order = order)

    payment_serial = DownPaymentSerializer(payment, context={'request': request}, many=True)
    order_serial = SingleOrderSerializer(order, context={'request': request})
    orderitem_serial = OrderItemSerializer(orderitem, context={'request': request}, many=True)

    response = [{'order': order_serial.data}] + [{'orderitem': orderitem_serial.data}] + [{'payment': payment_serial.data}]

    return Response(response)

@api_view(['GET'])
@permission_classes([AllowAny])
def invoice(request, pk):
    order = Order.objects.get(pk = pk)
    orderitem = OrderItem.objects.filter(order = order)
    logo = Logo.objects.get(pk = 1)
    promo = Promotion.objects.all()

    promo_serial = PromotionSerializer(promo, context={'request': request}, many=True)
    order_serial = BaseOrderSerializer(order, context={'request': request})
    logo_serial = LogoSerializer(logo, context={'request': request})
    orderitem_serial = OrderItemSerializer(orderitem, context={'request': request}, many=True)
    response = [{'order': order_serial.data}] + [{'orderitem': orderitem_serial.data}] + [{'logo': logo_serial.data}] + [{'promo': promo_serial.data}]

    return Response(response)

@api_view(['PUT'])
@permission_classes([AllowAny])
def cancel_order(request, pk):
    data = request.data
    if request.method == 'PUT':
        if data['reason']:
            order = Order.objects.get(pk = pk, person_responsible = request.user)
            order.cancel = True
            order.cancel_reason = data['reason']
            order.cancel_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            order.save()
            for orders in order.orderitem_set.all():
                spare = SparePart.objects.get(pk = orders.parts.pk)
                spare.stock = spare.stock + int(orders.quantity)
                spare.save()
                orders.save()
                
                EnhanceInOutStock.objects.create(
                    parts_id = orders.parts.pk, 
                    description="Pembatalan Penjualan Invoice - " + str(order.order_code), 
                    stockin = orders.quantity, 
                    stock = spare.stock, 
                    stockout = 0, 
                    person_responsible_id = request.user, 
                    date_added=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                )

            return Response(status=status.HTTP_201_CREATED)
        else: 
            res = {"code": 400, "message": "Harap Input Alasan Pembatalan"}
            return Response(data=res, status=status.HTTP_400_BAD_REQUEST)

@api_view(['PUT'])
@permission_classes([AllowAny])
def note_order(request, pk):
    data = request.data
    if request.method == 'PUT':
        if data['note']:
            order = Order.objects.get(pk = pk, person_responsible = request.user)
            order.note = data['note']
            order.save()
            return Response(status=status.HTTP_201_CREATED)
        else: 
            res = {"code": 400, "message": "Harap Input Catatan"}
            return Response(data=res, status=status.HTTP_400_BAD_REQUEST)

@api_view(['PUT'])
@permission_classes([AllowAny])
def delete_note_order(request, pk):
    data = request.data
    if request.method == 'PUT':
        order = Order.objects.get(pk = pk, person_responsible = request.user)
        order.note = ''
        order.save()
        return Response(status=status.HTTP_201_CREATED)

@api_view(['PUT'])
@permission_classes([AllowAny])
def return_order(request, pk):
    data = request.data
    if request.method == 'PUT':
        if data['reason']:
            order = Order.objects.get(pk = pk, person_responsible = request.user)
            order.retur = True
            order.retur_reason = data['reason']
            order.retur_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            order.save()
            for orders in order.orderitem_set.all():
                spare = SparePart.objects.get(pk = orders.parts.pk)
                spare.stock = spare.stock + int(orders.quantity)
                spare.save()
                orders.save()
                
                EnhanceInOutStock.objects.create(
                    parts_id = orders.parts.pk, 
                    description="Pembatalan Penjualan Invoice - " + str(order.order_code), 
                    stockin = orders.quantity, 
                    stock = spare.stock, 
                    stockout = 0, 
                    person_responsible_id = request.user, 
                    date_added=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                )

            return Response(status=status.HTTP_201_CREATED)
        else: 
            res = {"code": 400, "message": "Harap Input Alasan Retur"}
            return Response(data=res, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST', 'DELETE'])
@permission_classes([AllowAny])
def down_payment(request, pk):
    data = request.data
    if request.method == 'POST':
        order = Order.objects.filter(pk = pk, cancel = False)
        if order:
            if data['amount']:
                down = DownPayment.objects.create(
                    order_id = pk, 
                    proof = data['proof'],
                    nilai = data['amount'],
                    note = data['note'],
                    creation_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                )
                return Response(status=status.HTTP_201_CREATED)
            else: 
                res = {"code": 400, "message": "File Gagal Diunggah"}
                return Response(data=res, status=status.HTTP_400_BAD_REQUEST)
        else:
            res = {"code": 400, "message": "Pesanan sudah dibatalkan, tidak bisa mengunggah cicilan lagi"}
            return Response(data=res, status=status.HTTP_400_BAD_REQUEST)

    if request.method == 'DELETE':
        down = DownPayment.objects.get(pk = pk).delete()
        return Response(status=status.HTTP_201_CREATED)

@api_view(['PUT'])
@permission_classes([AllowAny])
def full_paid(request, pk):
    data = request.data
    if request.method == 'PUT':
        order = Order.objects.get(pk = pk, person_responsible = request.user)
        if order.paid == False:
            for orders in order.orderitem_set.all():
                if orders.preorder == False:
                    order.paid_proof = data['payment_proof']
                    order.paid_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    order.paid = True
                    order.save()
                else: 
                    spare = SparePart.objects.get(pk=orders.parts.pk)
                    if spare.stock >=  orders.quantity:
                        spare.stock = spare.stock - int(orders.quantity)
                        spare.save()
                        
                        EnhanceInOutStock.objects.create(
                            parts_id=orders.parts.pk, 
                            description="Penjualan Invoice (Pre Order) - " + str(order.order_code), 
                            stockout=orders.quantity, 
                            stock=spare.stock, 
                            stockin=0, 
                            person_responsible_id = request.user, 
                            date_added=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        )
                    else:
                        res = {"code": 400, "message": "Harap melakukan perubahan stock terlebih dahu sebelum melakukan pelunasan"}
                        return Response(data=res, status=status.HTTP_400_BAD_REQUEST)
        else:
            order.paid_proof = data['payment_proof']
            order.paid_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            order.paid = True
            order.save()
        return Response(status=status.HTTP_201_CREATED)
    else: 
        res = {"code": 400, "message": "Gagal Diupload"}
        return Response(data=res, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([AllowAny])
def bulk_in(request):
    data = request.data
    
    if request.method == 'POST':
        for bulkin in data['inputList']:
            spare = SparePart.objects.get(pk = bulkin['sparePK'])
            spare.stock = spare.stock + int(bulkin['Amount'])
            spare.save()

            EnhanceInOutStock.objects.create(
                parts_id = bulkin['sparePK'], 
                description = bulkin['Reason'], 
                stockin = bulkin['Amount'], 
                stock = spare.stock, 
                stockout = 0, 
                person_responsible_id = request.user, 
                date_added = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        return Response(status=status.HTTP_201_CREATED)
    else: 
        res = {"code": 400, "message": "Gagal Diupload"}
        return Response(data=res, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([AllowAny])
def bulk_out(request):
    data = request.data
    
    if request.method == 'POST':
        for bulkout in data['inputList']:
            spare = SparePart.objects.get(pk = bulkout['sparePK'])
            spare.stock = spare.stock - int(bulkout['Amount'])
            spare.save()

            EnhanceInOutStock.objects.create(
                parts_id = bulkout['sparePK'], 
                description = bulkout['Reason'], 
                stockout = bulkout['Amount'], 
                stock = spare.stock, 
                stockin = 0, 
                person_responsible_id = request.user, 
                date_added = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        return Response(status=status.HTTP_201_CREATED)

    else: 
        res = {"code": 400, "message": "Gagal Diupload"}
        return Response(data=res, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([AllowAny])
def bulk_cart(request):
    data = request.data
    if request.method == 'POST':
        order = Order.objects.filter(person_responsible = request.user, request_order = False)
        if order:
            order_check = Order.objects.get(person_responsible = request.user, request_order = False)
            count_order = order_check.orderitem_set.all().count()
            if count_order < 50:
                orders = Order.objects.get(person_responsible = request.user, request_order = False)
                orderitem = OrderItem.objects.filter(order_id = orders.pk, request_order=False, paid=False).exists()
                if orders:
                    orders = Order.objects.get(person_responsible = request.user, request_order = False)
                    for bulkcart in data['inputList']:
                        OrderItem.objects.create(
                            order_id = orders.pk, 
                            parts_id = bulkcart['sparePK'], 
                            quantity = bulkcart['Amount'],
                            person_responsible = request.user,
                            creation_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        )
                    return Response(status=status.HTTP_201_CREATED)
            else:
                res = {"code": 400, "message": "Maximum item di keranjang adalah 25"}
                return Response(data=res, status=status.HTTP_400_BAD_REQUEST)

        else:
            order = Order.objects.create(
                person_responsible = request.user, 
                creation_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            )
            OrderItem.objects.create(
                order_id = order.pk, 
                parts_id = bulkcart['sparePK'], 
                person_responsible = request.user,
                creation_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            )
            print("Second One")
            return Response(status=status.HTTP_201_CREATED)

    else: 
        res = {"code": 400, "message": "Gagal Diupload"}
        return Response(data=res, status=status.HTTP_400_BAD_REQUEST)

class LogoutAndBlacklistRefreshTokenForUserView(APIView):
    permission_classes = (permissions.AllowAny,)
    authentication_classes = ()

    def post(self, request):
        try:
            refresh_token = request.data["refresh_token"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST)
