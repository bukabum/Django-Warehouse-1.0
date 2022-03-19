from django.shortcuts import render, redirect
from django.http import HttpResponse
from .forms import * 
import qrcode
import io
from PIL import Image
from django.core.files.uploadedfile import InMemoryUploadedFile
import PIL
import sys
import datetime
from django.urls import resolve
from django.contrib.sites.shortcuts import get_current_site
from django.core.paginator import Paginator
from django.db.models import Count, F, Value
from .filters import * 
from urllib.parse import urlencode
from django.contrib.auth.decorators import login_required
from decouple import config 
from io import BytesIO
import boto3
import json
from django.core.files import File
from .models import *
from .serializers import *
from django_xhtml2pdf.utils import generate_pdf
from django_xhtml2pdf.utils import pdf_decorator
from django.template.loader import render_to_string
from weasyprint import HTML
import tempfile
from xhtml2pdf import pisa
from django.template.loader import get_template

# Create your views here.
@login_required
def add_product(request, *args, **kwargs):
    spare = SparePart.objects.all()
    form = SparePartForm(request.POST, request.FILES)
    if request.method == 'POST':
        form = SparePartForm(request.POST, request.FILES)
        current_site = get_current_site(request)
        if form.is_valid():
            print("kakak")
            category = Category.objects.get(name=form.cleaned_data['category'])
            spare = SparePart.objects.create(
                name = form.cleaned_data['name'],
                description = form.cleaned_data['description'],
                stock = form.cleaned_data['stock'],
                price = form.cleaned_data['price'],
                image = form.cleaned_data['image'],
                category_id = category.pk,
                date_added = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                person_responsible = request.user,
                first_stock = form.cleaned_data['stock'],
            )
            category = Category.objects.get(name=form.cleaned_data['category'])
            #img = qrcode.make(form.cleaned_data['name'] + (form.cleaned_data['product_code']))
            img = qrcode.make(current_site.domain+'/view/product/'+str(spare.id)+'/')
            type(img)  
            image_io = BytesIO()
            filenamme = spare.name + str(spare.id) + str(datetime.date.today())
            img.save(image_io, 'JPEG')
            spare.qrcode.save(filenamme, File(image_io), save = False)
            #spare.qrcode_s3 = spare.qrcode
            spare.product_code = category.code + str(spare.id + 1000000)

            spare.save()
            return redirect('add_product')
        else:
            print(form.errors)
    context = {'form':form, 'spare':spare}
    return render (request, 'spare/newsparepart.html', context)

def product_list(request, *args, **kwargs):
    spare = SparePart.objects.all().order_by('-date_added')
    spare_filter = SparePartFilter(request.GET, queryset=spare)
    spare_list = spare_filter.qs
    
    paginator = Paginator(spare_list, 20)
    page = request.GET.get('page')

    gt = request.GET.copy()
    if 'page' in gt:
        del gt['page']

    try:
        posts = paginator.get_page(page)  # returns the desired page object
    except PageNotAnInteger:
        # if page_number is not an integer then assign the first page
        posts = paginator.page(1)
    except EmptyPage:
        # if page is empty then return last page
        posts = paginator.page(paginator.num_pages)

    context = {'spare':posts, "spare_filter": spare_filter, "params": urlencode(gt)}
    return render (request, 'spare/home.html', context)

def view_saprepart(request, pk, *args, **kwargs):
    category = Category.objects.all()
    spare = SparePart.objects.get(id=pk)
    context = {'spare':spare, 'category': category}
    return render (request, 'spare/view_sparepart.html', context)

@login_required
def add_to_cart(request, pk, *args, **kwargs):
    order = Order.objects.filter(person_responsible = request.user, request_order = False).exists()    
    if order:
        orders = Order.objects.get(person_responsible = request.user, request_order = False)
        orderitem = OrderItem.objects.filter(order_id = orders.pk, parts_id = pk, request_order=False, paid=False).exists()
        if orderitem:
            OrderItem.objects.filter(order_id = orders.pk, parts_id = pk, request_order=False, paid=False).update(quantity =+ 1)
        else:
            orders = Order.objects.get(person_responsible = request.user, request_order = False)
            OrderItem.objects.create(
                order_id = orders.pk, 
                parts_id = pk, 
                person_responsible = request.user,
                creation_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            )
    else:
        order = Order.objects.create(
            person_responsible = request.user, 
            creation_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        )
        OrderItem.objects.create(
            order_id = order.pk, 
            parts_id = pk, 
            person_responsible = request.user,
            creation_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        )
    return redirect('cart')

@login_required
def cart(request, *args, **kwargs):
    order = Order.objects.filter(person_responsible = request.user, request_order = False)
    orderitem =  OrderItem.objects.filter(order__in = order) 
    customer = Customer.objects.all()       
    context = {'orderitem':orderitem, "customer":customer}
    return render (request, 'spare/cart.html', context)

@login_required
def update_cart(request, pk, *args, **kwargs):
    orderitem = OrderItem.objects.get(pk=pk)
    if request.method == 'POST':
        orderitem.quantity = request.POST.get('quantity')
        orderitem.internal_note = request.POST.get('catatan')
        orderitem.save()
        return redirect('cart')
    return redirect('cart')

@login_required
def all_stock_history(request, pk, *args, **kwargs):
    spare = SparePart.objects.get(id=pk)
    stock = EnhanceInOutStock.objects.filter(parts=pk).order_by('-date_added')
    stock_filter = StockFilter(request.GET, queryset=stock)
    spare_list = stock_filter.qs
    
    paginator = Paginator(spare_list, 10)
    page = request.GET.get('page')

    gt = request.GET.copy()
    if 'page' in gt:
        del gt['page']

    try:
        posts = paginator.get_page(page)  # returns the desired page object
    except PageNotAnInteger:
        # if page_number is not an integer then assign the first page
        posts = paginator.page(1)
    except EmptyPage:
        # if page is empty then return last page
        posts = paginator.page(paginator.num_pages)

    context = {'stock': posts, 'spare':spare, "stock_filter": stock_filter, "params": urlencode(gt)}
    return render (request, 'spare/all_stock_history.html', context)

@login_required
def request_order(request, *args, **kwargs):
    order = Order.objects.get(person_responsible = request.user, request_order=False, paid=False)
    order.request_order = True
    order.person_responsible = request.user
    for orders in order.orderitem_set.all():
        serializers = OrderItemSerializer(orders)
        orders.receipt = serializers.data
        if orders.use_discaunt == True:
            price = (int(orders.parts.price) * int(orders.quantity)) - ((int(orders.parts.price) * int(orders.quantity)) * (int(orders.discount) / 100))
            orders.total_price = price
        else:
            price = (int(orders.parts.price) * int(orders.quantity))
            orders.total_price = price
        orders.save()
    totalprice = order.orderitem_set.all().aggregate(total_price=models.Sum('total_price'))
    
    order.total_amount = totalprice['total_price']
    order.order_code = 1000000 + order.pk
    order.save()
    if request.method == 'POST':
        order.customer_id = request.POST.get('customer')
        order.save()
        return redirect('cart')

@login_required
def stock_history(request, pk, *args, **kwargs):
    today = datetime.date.today()
    spare = SparePart.objects.get(id=pk)
    stock = EnhanceInOutStock.objects.filter(parts=pk, date_added__month=today.month).order_by('-date_added')
    stock_filter = StockFilter(request.GET, queryset=stock)
    context = {'spare':spare, 'stock': stock, 'stock_filter': stock_filter}
    return render (request, 'spare/stock_history.html', context)

@login_required
def update_product(request, pk, *args, **kwargs):
    spare = SparePart.objects.get(id=pk)
    if request.method == 'POST':
        category = Category.objects.get(pk=request.POST.get('category'))
        spare.name = request.POST.get('sparepart_name')
        spare.description = request.POST.get('sparepart_description')
        spare.category_id = category.pk
        spare.product_code = category.code + str(spare.id + 1000000)
        spare.price = request.POST.get('sparepart_price')
        spare.person_responsible_for_update = request.user
        spare.promo_price = request.POST.get('promo_price')
        spare.update_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        #print(request.build_absolute_uri())
        #current_site = get_current_site(request)
        #print(current_site.domain)
        spare.save()
        return redirect('view_saprepart', pk=pk)

@login_required
def stock_in(request, pk, *args, **kwargs):
    spare = SparePart.objects.get(id=pk)
    if request.method == 'POST':
        EnhanceInOutStock.objects.create(
            stock = spare.stock + int(request.POST.get('stock_in')),
            stockin = request.POST.get('stock_in'), 
            stockout = 0, 
            description = request.POST.get('keterangan'),
            date_added = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            parts_id = pk,
            person_responsible = request.user
        )
        spare.stock = F('stock') + request.POST.get('stock_in')
        spare.save()
        return redirect('view_saprepart', pk=pk)
    context = {'spare':spare}
    return render (request, 'spare/increase_stock.html', context)

@login_required
def stock_out(request, pk, *args, **kwargs):
    spare = SparePart.objects.get(id=pk)
    if request.method == 'POST':
        EnhanceInOutStock.objects.create(
            stock = spare.stock - int(request.POST.get('stock_out')),
            stockin = 0,
            stockout = request.POST.get('stock_out'), 
            description = request.POST.get('keterangan'),
            date_added = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            parts_id = pk,
            person_responsible = request.user
        )
        spare.stock = F('stock') - request.POST.get('stock_out')
        spare.save()
        return redirect('view_saprepart', pk=pk)
    context = {'spare':spare}
    return render (request, 'spare/decrease_stock.html', context)

def stock_in_bulk(request, *args, **kwargs):
    spare = SparePart.objects.all()
    context = {'spare':spare}
    return render (request, 'spare/bulk_increase_stock.html', context)

@login_required
def list_order(request, *args, **kwargs):
    order = Order.objects.filter(person_responsible=request.user).order_by('-creation_date')
    order_filter = OrderFilter(request.GET, queryset=order)
    order_list = order_filter.qs

    paginator = Paginator(order_list, 10)
    page = request.GET.get('page')

    gt = request.GET.copy()
    if 'page' in gt:
        del gt['page']

    try:
        posts = paginator.get_page(page)  # returns the desired page object
    except PageNotAnInteger:
        # if page_number is not an integer then assign the first page
        posts = paginator.page(1)
    except EmptyPage:
        # if page is empty then return last page
        posts = paginator.page(paginator.num_pages)

    context = {'order':posts, 'order_filter': order_filter, "params": urlencode(gt)}
    return render (request, 'spare/list_order.html', context)

@login_required
def view_order(request, pk, *args, **kwargs):
    order = Order.objects.get(pk = pk, person_responsible = request.user)
    orderitem = OrderItem.objects.filter(order = order, person_responsible = request.user)
    context = {'order':order, 'orderitem':orderitem}
    return render (request, 'spare/view_order.html', context)

@login_required
def cancel_order(request, pk, *args, **kwargs):
    order = Order.objects.get(pk = pk, person_responsible = request.user)
    if request.method == 'POST':
        order.cancel = True
        order.cancel_reason = request.POST.get('alasan_pembatalan')
        order.save()
        return redirect('view_order', pk=pk)

@login_required
def return_order(request, pk, *args, **kwargs):
    order = Order.objects.get(pk = pk, person_responsible = request.user)
    if request.method == 'POST':
        order.retur = True
        order.retur_reason = request.POST.get('alasan_retur')
        order.save()
        return redirect('view_order', pk=pk)

@login_required
def invoice(request, pk, *args, **kwargs):
    date = datetime.datetime.now().strftime("%d/%m/%Y")
    logo = Logo.objects.get(pk=1)
    order = Order.objects.get(pk = pk, person_responsible = request.user)
    orderitem = OrderItem.objects.filter(order = order, person_responsible = request.user)
    if request.method == 'POST':
        template_path = 'spare/re_invoice.html'

        context = {'order':order, 'orderitem':orderitem, 'logo':logo, 'date': date}

        response = HttpResponse(content_type='application/pdf')

        response['Content-Disposition'] = 'filename="products_report.pdf"'

        template = get_template(template_path)

        html = template.render(context)

        # create a pdf
        pisa_status = pisa.CreatePDF(
        html, dest=response)
        # if error then show some funy view
        if pisa_status.err:
            return HttpResponse('We had some errors <pre>' + html + '</pre>')
        return response
    context = {'order':order, 'orderitem':orderitem, 'logo':logo, 'date': date}

    return render (request, 'spare/invoice.html', context)

@login_required
def pdf_receipt(request, pk, *args, **kwargs):
    date = datetime.datetime.now().strftime("%d/%m/%Y")
    logo = Logo.objects.get(pk=1)
    order = Order.objects.get(pk = pk, person_responsible = request.user)
    orderitem = OrderItem.objects.filter(order = order, person_responsible = request.user)
    return render (request, 'spare/invoice.html', context)

@login_required
def upload_payment_proof(request, pk, *args, **kwargs):
    order = Order.objects.get(pk = pk, person_responsible = request.user)
    order.paid_proof = request.FILES['bukti_pembayaran']
    if order.paid == False:
        for orders in order.orderitem_set.all():
            EnhanceInOutStock.objects.create(parts_id=orders.parts.pk, description="Penjualan Invoice - " + str(order.order_code), stockout=orders.quantity, stock=orders.parts.stock - int(orders.quantity), stockin=0, person_responsible_id = request.user, date_added=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            spare = SparePart.objects.get(pk=orders.parts.pk)
            spare.stock=spare.stock - int(orders.quantity)
            spare.save()
    order.paid = True
    order.save()
    return redirect('view_order', pk=pk)

@login_required
def update_user_profile(request, pk, *args, **kwargs):
    order = Order.objects.get(pk = pk, person_responsible = request.user)
    order.nama_penerima = request.POST['nama_pemesan']
    order.no_hp = request.POST['nomor_hp']
    order.alamat = request.POST['alamat']
    order.save()
    return redirect('view_order', pk=pk)

@login_required
def remove_from_cart(request, pk, *args, **kwargs):
    order = OrderItem.objects.get(pk = pk)
    order.delete()
    return redirect('cart')

@login_required
def create_customer(request, *args, **kwargs):
    if request.method == 'POST':
        Customer.objects.create(creation_date=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 
            nama_pelanggan=request.POST['penerima'], 
            alamat=request.POST['alamat'], 
            no_hp=request.POST['no_hp'], 
            catatan=request.POST['catatan'], 
            person_responsible=request.user)
        return redirect('list_customer')
    return render (request, 'spare/add_customer.html')

@login_required
def list_customer(request, *args, **kwargs):
    cus = Customer.objects.filter(person_responsible=request.user).order_by('-creation_date')
    cus_filter = CustomerFilter(request.GET, queryset=cus)
    cus_list = cus_filter.qs

    paginator = Paginator(cus_list, 10)
    page = request.GET.get('page')

    gt = request.GET.copy()
    if 'page' in gt:
        del gt['page']

    try:
        posts = paginator.get_page(page)  # returns the desired page object
    except PageNotAnInteger:
        # if page_number is not an integer then assign the first page
        posts = paginator.page(1)
    except EmptyPage:
        # if page is empty then return last page
        posts = paginator.page(paginator.num_pages)

    context = {'cus':posts, 'cus_filter': cus_filter, "params": urlencode(gt)}
    return render (request, 'spare/customer.html', context)

@login_required
def view_customer(request, pk, *args, **kwargs):
    cus = Customer.objects.get(pk=pk, person_responsible=request.user)
    if request.method == 'POST':
        customer = Customer.objects.get(pk=pk, person_responsible=request.user)
        customer.nama_pelanggan = request.POST['nama_pemesan']
        customer.alamat = request.POST['alamat']
        customer.no_hp = request.POST['no_hp']
        customer.catatan = request.POST['catatan']
        customer.save()
        return redirect('view_customer', pk=pk)

    order = Order.objects.filter(customer = pk).order_by('-creation_date')
    order_filter = OrderFilter(request.GET, queryset=order)
    order_list = order_filter.qs

    paginator = Paginator(order_list, 10)
    page = request.GET.get('page')

    gt = request.GET.copy()
    if 'page' in gt:
        del gt['page']

    try:
        posts = paginator.get_page(page)  # returns the desired page object
    except PageNotAnInteger:
        # if page_number is not an integer then assign the first page
        posts = paginator.page(1)
    except EmptyPage:
        # if page is empty then return last page
        posts = paginator.page(paginator.num_pages)

    context = {'cus':cus, 'order':posts, 'order_filter': order_filter, "params": urlencode(gt)}
    return render (request, 'spare/view_customer.html', context)
