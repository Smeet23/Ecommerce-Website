from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from .models import Product, Contact, Orders, OrderUpdate
from math import ceil
import json
from .forms import RegisterForm

def login_required_message(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.warning(request, "You need to log in before accessing this page.")
            return redirect("login")
        return view_func(request, *args, **kwargs)
    return wrapper


# Render Registration Page
def register_page(request):
    if request.user.is_authenticated:
        return redirect("home")
    form = RegisterForm()
    return render(request, "shop/register.html", {"form": form})

# Handle User Registration
def register_user(request):
    if request.user.is_authenticated:
        return redirect("home")

    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Account created successfully! Please log in.")
            return redirect("login")  
        else:
            # Print errors to terminal (for debugging)
            print(form.errors)  
            messages.error(request, "Registration failed. Please check the form.")
            return render(request, "shop/register.html", {"form": form})  

    return redirect("register")


# Render Login Page
def login_page(request):
    if request.user.is_authenticated:
        return redirect("ShopHome")

    form = AuthenticationForm()
    return render(request, "shop/login.html", {"form": form})

# Handle User Login
def login_user(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]
            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
                messages.success(request, f"Welcome, {username}!")
                return redirect("ShopHome")
        messages.error(request, "Invalid username or password.")
    
    return redirect("login")  # Redirect back to login page if invalid

# User Logout
def user_logout(request):
    logout(request)
    messages.success(request, "You have been logged out successfully.")
    return redirect("login")

# Home Page (Redirect after login)
def home(request):
    return render(request, "shop/home.html")

@login_required_message
def index(request):
    allProds = []
    catprods = Product.objects.values('category', 'id')
    cats = {item['category'] for item in catprods}
    for cat in cats:
        prod = Product.objects.filter(category=cat)
        n = len(prod)
        nSlides = n // 4 + ceil((n / 4) - (n // 4))
        allProds.append([prod, range(1, nSlides), nSlides])
    params = {'allProds':allProds}
    return render(request, 'shop/index.html', params)

@login_required_message
def searchMatch(query, item):
    query = str(query).lower()  

    desc = (item.desc or "").lower()
    name = (item.product_name or "").lower()
    category = (item.category or "").lower()

    print(f"Query: {query}, Desc: {desc}, Name: {name}, Category: {category}")

    return query in desc or query in name or query in category

@login_required_message
def search(request):
    query = request.GET.get('search')
    allProds = []
    catprods = Product.objects.values('category', 'id')
    cats = {item['category'] for item in catprods}
    for cat in cats:
        prodtemp = Product.objects.filter(category=cat)
        prod = [item for item in prodtemp if searchMatch(query, item)]

        n = len(prod)
        nSlides = n // 4 + ceil((n / 4) - (n // 4))
        if len(prod) != 0:
            allProds.append([prod, range(1, nSlides), nSlides])
    params = {'allProds': allProds, "msg": ""}
    if len(allProds) == 0:
        params = {'msg': "Please make sure to enter relevant search query"}
    return render(request, 'shop/search.html', params)


@login_required_message
def about(request):
    return render(request, 'shop/about.html')

@login_required_message
def contact(request):
    context = {'empty_fields': False, 'submitted': False}

    if request.method == "POST":
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        phone = request.POST.get('phone', '').strip()
        desc = request.POST.get('desc', '').strip()

        if not name or not email or not phone or not desc:
            context['empty_fields'] = True  # Show alert for missing fields
        else:
            # Save the contact form data
            contact = Contact(name=name, email=email, phone=phone, desc=desc)
            contact.save()
            context['submitted'] = True  # Show success alert

    return render(request, 'shop/contact.html', context)

    

@login_required_message
def tracker(request):
    if request.method=="POST":
        orderId = request.POST.get('orderId', '')
        email = request.POST.get('email', '')
        try:
            order = Orders.objects.filter(order_id=orderId, email=email)
            if len(order)>0:
                update = OrderUpdate.objects.filter(order_id=orderId)
                updates = []
                for item in update:
                    updates.append({'text': item.update_desc, 'time': item.timestamp})
                    response = json.dumps({"status":"success", "updates": updates, "itemsJson": order[0].items_json}, default=str)
                return HttpResponse(response)
            else:
                return HttpResponse('{"status":"noitem"}')
        except Exception as e:
            return HttpResponse('{"status":"error"}')

    return render(request, 'shop/tracker.html')

@login_required_message
def productView(request, myid):

    # Fetch the product using the id
    product = Product.objects.filter(id=myid)
    return render(request, 'shop/prodView.html', {'product':product[0]})

@login_required_message
def checkout(request):
    if request.method=="POST":
        items_json = request.POST.get('itemsJson', '')
        name = request.POST.get('name', '')
        amount = request.POST.get('amount', '')
        email = request.POST.get('email', '')
        address = request.POST.get('address1', '') + " " + request.POST.get('address2', '')
        city = request.POST.get('city', '')
        state = request.POST.get('state', '')
        zip_code = request.POST.get('zip_code', '')
        phone = request.POST.get('phone', '')
        order = Orders(items_json=items_json, name=name, email=email, address=address, city=city,
                       state=state, zip_code=zip_code, phone=phone, amount=amount)
        order.save()
        update = OrderUpdate(order_id=order.order_id, update_desc="The order has been placed")
        update.save()
        thank = True
        id = order.order_id
        return render(request, 'shop/checkout.html', {'thank':thank, 'id': id})
    return render(request, 'shop/checkout.html')

