from urllib import request
import django
from django.contrib.auth.models import User
from store.models import Address, Cart, Category, Order, Product, WishList
from django.shortcuts import redirect, render, get_object_or_404
from .forms import RegistrationForm, AddressForm
from django.contrib import messages
from django.views import View
import decimal
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.decorators import login_required
import re
from django.utils.decorators import method_decorator # for Class Based Views
import pandas as pd
import random
import requests
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json
from django.core.paginator import Paginator

# Create your views here.

def sku_gen():
    sku = ""
    for i in range(10):
        sku+=str(random.randint(0,9))
    return sku

def random_cat():
    dt = Category.objects.all()
    dt_len = len(dt)
    return dt[random.randint(0,dt_len-1)]

boolean_field= [True,False]
def active():
    return random.choice(boolean_field)

def feature():
    return random.choice(boolean_field)


def home(request):
    categories = Category.objects.filter(is_active=True, is_featured=True)[:3]
    products = Product.objects.filter(is_active=True, is_featured=True)[:8]

    print("***************************")
    # print(Product.objects.get(title='Shadow Kiss'))

    # data = pd.read_csv("books.csv")

    # for i in range(0,len(data)):

    #     title = data.iloc[i].title.strip()
    #     print(title)
    #     sku = sku_gen()
    #     detail_description = "There are several things to consider in order to help your book achieve its greatest potential discoverability. Readers, librarians, and retailers can't purchase a book they can't find, and your book metadata is responsible for whether or not your book pops up when they type in search terms relevant to your book. Book metadata may sound complicated, but it consists of all the information that describes your book, including: your title, subtitle, series name, price, trim size, author name, book description, and more. There are two metadata fields for your book description: the long book description and the short book description. Although both play a role in driving traffic to your book, they have distinct differences. "
    #     short_description = "There are several things to consider in order to help your book achieve its greatest potential discoverability. "
    #     # print(len(data.iloc[i].description))
    #     # if len(str(data.iloc[i].description))>30:
    #     #     short_description = data.iloc[i].description[:30]
    #     # else:
    #     #     short_description = data.iloc[i].description[:30]
            
    #     img = data.iloc[i].image_url
    #     price = random.randint(200,1000)
    #     cat = random_cat()
    # # ''.join(c for c in title if c.isalpha())
    #     slug = sku
    #     is_active = True
    #     features = True
    #     Product.objects.create(title=title,sku=sku,short_description=short_description,detail_description=detail_description,product_image=img,category=cat, price = price,is_active=is_active,is_featured=features,slug=slug)

    # for i in Product.objects.all():
    #     i.delete()

    context = {
        'categories': categories,
        'products': products,
    }
    return render(request, 'store/index.html', context)

def about(request):
    return render(request, 'store/about.html')

def sendEmail(email,message,name):
    email_detail = f"""
    Name: {name}
    Message: {message}
    """
    send_mail(
    'Subject',
    email_detail,
    settings.EMAIL_HOST_USER,
    [email.strip()],
    fail_silently=False,
    )
    return "success"

def contact(request):
    if request.method == "POST":
        form_name = request.POST.get("name")
        form_email = request.POST.get("email")
        form_message = request.POST.get("message")
        # sendEmail(email,message,name)
        subject = "Contact Form Filled by:" + form_name
        message = "Hello Admin, Here are the contact form details.\n\nname:" + form_name +"\nemail:" + form_email + "\nmessage:" + form_message
        from_email = settings.EMAIL_HOST_USER
        to_list = ["np03a180310@heraldcollege.edu.np"]
        send_mail(subject, message, from_email, to_list)
        messages.info(request, 'Thank you  we will contact you shortly!!!')
        return redirect("store:contact")
    return render(request, 'store/contact.html')


def recommend_book_collab(book):
    data = requests.get(f"http://localhost:5000/collaborative/{book}")
    data = json.loads(data.content)
    related_products = []
    print( data['recommended_books'])
    for i in data['recommended_books']:
        print(i)
        pd = Product.objects.get(title =i.strip())
        print(pd)
        related_products.append(pd)
    return related_products

def recommend_book_content(book):
    data = requests.get(f"http://localhost:5000/content_based/{book}")
    data = json.loads(data.content)
    related_products = []
    print( data['recommended_books'])
    for i in data['recommended_books']:
        print(i)
        pd = Product.objects.get(title =i.strip())
        print(pd)
        related_products.append(pd)
    return related_products
    

def detail(request, slug):
    product = get_object_or_404(Product, slug=slug)
    related_products_content =''
    related_products_collab =''
    book_name = product.title
    print("&&&&&")
    print(book_name)
    try: 
        related_products_content = recommend_book_content(book_name)
    except:
        related_products_content = Product.objects.exclude(id=product.id).filter(is_active=True, category=product.category)[:4]
   
    try:
       related_products_collab = recommend_book_collab(book_name)
    except:
        related_products_collab = Product.objects.exclude(id=product.id).filter(is_active=True, category=product.category)[4:8]
   

    
    context = {
        'product': product,
        'related_products_content': related_products_content,
        'related_products_collab':related_products_collab

    }
    return render(request, 'store/detail.html', context)


def all_categories(request):
    categories = Category.objects.filter(is_active=True)
    return render(request, 'store/categories.html', {'categories':categories})


def category_products(request, slug):
    category = get_object_or_404(Category, slug=slug)
    products = Product.objects.filter(is_active=True, category=category)
    categories = Category.objects.filter(is_active=True)

    p = Paginator(products, 6)  # creating a paginator object
    page_number = request.GET.get('page')

    try:

        page_obj = p.get_page(page_number) 
    except PageNotAnInteger:
        page_obj = p.page(1)
    except EmptyPage:

        # if page is empty then return last page

        page_obj = p.page(p.num_pages)
    context = {
        'category': category,
        'products': products,
        'categories': categories,
        'page_obj': page_obj
    }
    return render(request, 'store/category_products.html', context)


# Authentication Starts Here

class RegistrationView(View):
    def get(self, request):
        form = RegistrationForm()
        return render(request, 'account/register.html', {'form': form})
    
    def post(self, request):
        form = RegistrationForm(request.POST)
        if form.is_valid():
            messages.success(request, "Congratulations! Registration Successful!")
            form.save()
        return render(request, 'account/register.html', {'form': form})
        

@login_required
def profile(request):
    addresses = Address.objects.filter(user=request.user)
    orders = Order.objects.filter(user=request.user)
    return render(request, 'account/profile.html', {'addresses':addresses, 'orders':orders})


@method_decorator(login_required, name='dispatch')
class AddressView(View):
    def get(self, request):
        form = AddressForm()
        return render(request, 'account/add_address.html', {'form': form})

    def post(self, request):
        form = AddressForm(request.POST)
        if form.is_valid():
            user=request.user
            locality = form.cleaned_data['locality']
            city = form.cleaned_data['city']
            state = form.cleaned_data['state']
            reg = Address(user=user, locality=locality, city=city, state=state)
            reg.save()
            messages.success(request, "New Address Added Successfully.")
        return redirect('store:profile')


@login_required
def remove_address(request, id):
    a = get_object_or_404(Address, user=request.user, id=id)
    a.delete()
    messages.success(request, "Address removed.")
    return redirect('store:profile')

@login_required
def add_to_cart(request):
    user = request.user
    product_id = request.GET.get('prod_id')
    product = get_object_or_404(Product, id=product_id)

    # Check whether the Product is alread in Cart or Not
    item_already_in_cart = Cart.objects.filter(product=product_id, user=user)
    if item_already_in_cart:
        cp = get_object_or_404(Cart, product=product_id, user=user)
        cp.quantity += 1
        cp.save()
    else:
        Cart(user=user, product=product).save()
    
    return redirect('store:cart')


@login_required
def add_to_wishList(request,id):
    user = request.user
    product = get_object_or_404(Product, id=id)
    print(id)
    item_already_in_wishList = WishList.objects.filter(product=id, user=user)
    if not item_already_in_wishList:
        WishList(user=user, product=product,id_pr=id).save()
    
    return redirect('store:wish')


@login_required
def cart(request):
    user = request.user
    cart_products = Cart.objects.filter(user=user)

    # Display Total on Cart Page
    amount = decimal.Decimal(0)
    shipping_amount = decimal.Decimal(10)
    # using list comprehension to calculate total amount based on quantity and shipping
    cp = [p for p in Cart.objects.all() if p.user==user]
    if cp:
        for p in cp:
            temp_amount = (p.quantity * p.product.price)
            amount += temp_amount

    # Customer Addresses
    addresses = Address.objects.filter(user=user)

    context = {
        'cart_products': cart_products,
        'amount': amount,
        'shipping_amount': shipping_amount,
        'total_amount': amount + shipping_amount,
        'addresses': addresses,
    }
    return render(request, 'store/cart.html', context)


@login_required
def wish(request):
    user = request.user
    wish_products = WishList.objects.filter(user=user)

    # Display Total on Cart Page
    amount = decimal.Decimal(0)
    shipping_amount = decimal.Decimal(10)
    # using list comprehension to calculate total amount based on quantity and shipping
    cp = [p for p in WishList.objects.all() if p.user==user]
    if cp:
        for p in cp:
            temp_amount = (p.quantity * p.product.price)
            amount += temp_amount

    # Customer Addresses
    addresses = Address.objects.filter(user=user)

    context = {
        'wish_products': wish_products,
        'amount': amount,
        'shipping_amount': shipping_amount,
        'total_amount': amount + shipping_amount,
        'addresses': addresses,
    }
    return render(request, 'store/WishList.html', context)


@login_required
def remove_cart(request, cart_id):
    if request.method == 'GET':
        c = get_object_or_404(Cart, id=cart_id)
        c.delete()
        messages.success(request, "Product removed from Cart.")
    return redirect('store:cart')

@login_required
def remove_wish(request, id):
    if request.method == 'GET':
        c = get_object_or_404(WishList, id=id)
        c.delete()
        messages.success(request, "Product removed from Wish List.")
    return redirect('store:wish')


@login_required
def plus_cart(request, cart_id):
    if request.method == 'GET':
        cp = get_object_or_404(Cart, id=cart_id)
        cp.quantity += 1
        cp.save()
    return redirect('store:cart')


@login_required
def minus_cart(request, cart_id):
    if request.method == 'GET':
        cp = get_object_or_404(Cart, id=cart_id)
        # Remove the Product if the quantity is already 1
        if cp.quantity == 1:
            cp.delete()
        else:
            cp.quantity -= 1
            cp.save()
    return redirect('store:cart')


@login_required
def checkout(request):
    user = request.user
    # address_id = request.GET.get('address')
    
    address = get_object_or_404(Address,user=user)
    # Get all the products of User in Cart
    cart = Cart.objects.filter(user=user)
    for c in cart:
        # Saving all the products from Cart to Order
        Order(user=user, address=address, product=c.product, quantity=c.quantity).save()
        # And Deleting from Cart
        c.delete()
    # return render(request,"store/checkout.html")
    return redirect('store:orders')


@login_required
def orders(request):
    all_orders = Order.objects.filter(user=request.user).order_by('-ordered_date')
    return render(request, 'store/orders.html', {'orders': all_orders})





def shop(request):
    return render(request, 'store/shop.html')





def test(request):
    return render(request, 'store/test.html')


@csrf_exempt
def khalti(request):
   data = request.POST
   product_id = data['product_identity']
   token = data['token']
   amount = data['amount']

   url = "https://khalti.com/api/v2/payment/verify/"
   payload = {
   "token": token,
   "amount": amount
   }
   headers = {
   "Authorization": "test_public_key_dc74e0fd57cb46cd93832aee0a390234"
   }
   
   response = requests.post(url, payload, headers = headers)
   
   response_data = json.loads(response.text)
   status_code = str(response.status_code)

   if status_code == '400':
      response = JsonResponse({'status':'false','message':response_data['detail']}, status=500)
      return response

   import pprint 
   pp = pprint.PrettyPrinter(indent=4)
   pp.pprint(response_data)
   
   return JsonResponse(f"Payment Success !! . {response_data['user']['idx']}",safe=False)


def search(request):
    searched = request.POST['search']
    result = Product.objects.filter(title__icontains=searched)
    print(result)
    return render(request, 'store/search.html',{'searched':result})