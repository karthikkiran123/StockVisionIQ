from django.shortcuts import render, redirect
from vendor.models import Payment, Vendor, Product
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.models import User
from django.db.models import Sum
from store.models import Order

# Create your views here.
def dashboard(request):
    if not request.user.is_authenticated:
        return redirect('admin_login')
    if request.user.profiles.last().role == 'customer':
        return redirect('index')
    login = request.user.is_authenticated
    if request.user.profiles.last().role == 'admin':
        total_income = sum(Payment.objects.all().values_list('amount', flat=True))
        approved = sum(Payment.objects.filter(is_approved=True).values_list('amount', flat=True))
        pending = sum(Payment.objects.filter(is_approved=False).values_list('amount', flat=True))
        income_data = [total_income, approved, pending]
        all_transactions = Payment.objects.all().order_by('-created_at')[:5]
        success_transactions = Payment.objects.filter(is_approved=True).order_by('-created_at')[:5]
        pending_transactions = Payment.objects.filter(is_approved=False).order_by('-created_at')[:5]
    elif request.user.profiles.last().role == 'vendor':
        vendor = Vendor.objects.get(profile=request.user.profiles.last())
        total_income = sum(Payment.objects.filter(vendor=vendor).values_list('amount', flat=True))
        approved = sum(Payment.objects.filter(vendor=vendor, is_approved=True).values_list('amount', flat=True))
        pending = sum(Payment.objects.filter(vendor=vendor, is_approved=False).values_list('amount', flat=True))
        income_data = [total_income, approved, pending]
        all_transactions = Payment.objects.filter(vendor=vendor).order_by('-created_at')[:5]
        success_transactions = Payment.objects.filter(vendor=vendor, is_approved=True).order_by('-created_at')[:5]
        pending_transactions = Payment.objects.filter(vendor=vendor, is_approved=False).order_by('-created_at')[:5]
    return render(request, 'dashboard.html', {'income_data': income_data, 'total_income': total_income, 'approved': approved, 'pending': pending, 'all_transactions': all_transactions, 'success_transactions': success_transactions, 'pending_transactions': pending_transactions, 'login': login})

def login_staff(request):
    loggedin = request.user.is_authenticated
    error_msg = None
    if loggedin:
        return redirect('dashboard')
    if request.method == 'POST':
        email = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=email, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, 'Welcome to ReCraftify')
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid credentials')
            error_msg = 'Invalid credentials'
    return render(request, 'admin_login.html', {'login': loggedin, 'error_msg': error_msg})

def logout_user(request):
    if not request.user.is_authenticated:
        return redirect('admin_login')
    logout(request)
    system_messages = messages.get_messages(request)
    for message in system_messages:
        # This iteration is necessary
        pass
    return redirect('index')

def orders(request):
    if not request.user.is_authenticated:
        return redirect('admin_login')
    loggedin = request.user.is_authenticated
    user = request.user
    if user.profiles.last().role == 'admin':
        orders = Order.objects.all().order_by('-created_at')
    elif user.profiles.last().role == 'vendor':
        vendor = user.profiles.last().vendor.last()
        orders = Order.objects.filter(products__vendor=vendor).order_by('-created_at')
    else:
        redirect('index')
    return render(request, 'orders.html', {'orders': orders, 'login': loggedin})

def complete_order(request, id):
    if not request.user.is_authenticated:
        return redirect('admin_login')
    order = Order.objects.get(id=id)
    order.is_completed = True
    order.is_paid = True
    order.save()
    payment = Payment.objects.get(order=order)
    payment.is_approved = True
    payment.save()
    return redirect('orders')

def users(request):
    if not request.user.is_authenticated:
        return redirect('admin_login')
    loggedin = request.user.is_authenticated
    if request.user.profiles.last().role == 'admin':
        users = User.objects.all()
    else:
        redirect('index')
    return render(request, 'users.html', {'users': users, 'login': loggedin})

def invite_user(request):
    if not request.user.is_authenticated:
        return redirect('admin_login')
    loggedin = request.user.is_authenticated
    if request.method == "POST":
        email = request.POST.get('email')
        contact = request.POST.get('contact')
        name = request.POST.get('name')
        password = request.POST.get('password')
        role = request.POST.get('role')
        user = User.objects.filter(username=email)
        if user is not None:
            user = User.objects.create(email=email, username=email, first_name=name)
            user.set_password(password)
            user.save()
            profile = user.profiles.create(user=user, role=role, contact=contact)
            if role == 'vendor':
                vendor = Vendor.objects.create(profile=profile, name=name, contact=contact, email=email)
            return redirect('admin_users')
        else:
            messages.error(request, 'User already exist')
            return redirect('invite_user')
    return render(request, 'invite_user.html', {'login': loggedin})

def register_vendor(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == "POST":
        email = request.POST.get('email')
        contact = request.POST.get('contact')
        name = request.POST.get('name')
        password = request.POST.get('password')
        address = request.POST.get('address')
        role = 'vendor'
        user = User.objects.filter(username=email).last()
        if user is None:
            user = User.objects.create(email=email, username=email, first_name=name)
        user.set_password(password)
        user.save()
        profile = user.profiles.create(user=user, role=role, contact=contact)
        if role == 'vendor':
            vendor = Vendor.objects.create(profile=profile, name=name, contact=contact, email=email, address=address)
        return redirect('admin_login')
    return render(request, 'register_vendor.html')

def admin_delete_user(request, id):
    user = User.objects.get(id=id)
    user.delete()
    return redirect('admin_users')

def products(request, type):
    if not request.user.is_authenticated:
        return redirect('admin_login')
    loggedin = request.user.is_authenticated
    type_data = {
        "new": 1,
        "used": 2,
        "scrapyard": 3
    }
    type_opt = {
        1: "New",
        2: "Used",
        3: "Scrapyard"
    }
    if request.user.profiles.last().role == 'admin':
        products = Product.objects.filter(is_active=True)
    elif request.user.profiles.last().role == 'vendor':
        user = request.user
        profile = user.profiles.last()
        vendor = profile.vendor.last()
        products = Product.objects.filter(vendor=vendor, is_active=True)
    else:
        redirect('index')
    if type not in ["all", "reported"]:
        products = products.filter(type=type_data[type])
    if type == "reported":
        products = Product.objects.filter(reported__gt=0)

    for product in products:
        product.type = type_opt[product.type]
    return render(request, 'products.html', {'login': loggedin, 'products': products, 'type': type.capitalize(), 'type_opt': type_opt})

def admin_delete_product(request, id):
    product = Product.objects.get(id=id)
    product.delete()
    return redirect('dashboard')

def add_product(request):
    if not request.user.is_authenticated:
        return redirect('admin_login')
    loggedin = request.user.is_authenticated
    if request.method == "POST":
        name = request.POST.get('name')
        description = request.POST.get('description')
        price = request.POST.get('price')
        type = request.POST.get('type')
        if type == 3 or type == "3":
            name = name + " x " + str(request.POST.get('qty')) + "KG"
        vendor = request.POST.get('vendor')
        image = request.FILES.get('image')
        featured = request.POST.get('featured')
        discount = request.POST.get('discount')
        if featured == "on":
            featured = True
        else:
            featured = False
        print(request.POST)
        product = Product.objects.create(name=name, description=description, price=price, type=type, vendor=Vendor.objects.get(id=vendor),discount=discount , featured=featured, image=image)
        product.save()
        return redirect('dashboard')
    vendors = Vendor.objects.all()
    if request.user.profiles.last().role == 'vendor':
        user = request.user
        profile = user.profiles.last()
        vendor = profile.vendor.last()
        vendors = vendors.filter(id=vendor.id)
    return render(request, 'add_product.html', {'login': loggedin, 'vendors': vendors})