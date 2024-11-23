from django.shortcuts import render, redirect
from datetime import date, datetime
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.models import User
from scrapify import settings
import stripe

stripe.api_key = settings.STRIPE_SECRET_KEY

# Create your views here.
def index(request):
    return render(request, 'index.html')

def faq(request):
    return render(request, 'faq.html')

def about(request):
    return render(request, 'about.html')

def prediction(request):
    return render(request, 'prediction.html')

def login_user(request):
    is_logged_in = request.user.is_authenticated
    if is_logged_in:
        return redirect('index')

    if request.method == 'POST':
        # Handle login
        if request.POST.get('auth_action') == 'login':
            email = request.POST.get('email')
            password = request.POST.get('password')
            user = authenticate(request, username=email, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, 'Welcome to ForecasterIQ')
                return redirect('index')
            else:
                messages.error(request, 'Invalid username or password.')

        # Handle registration
        elif request.POST.get('auth_action') == 'register':
            fname = request.POST.get('fname')
            lname = request.POST.get('lname')
            email = request.POST.get('email')
            password = request.POST.get('password')
            cpassword = request.POST.get('cpassword')

            # Check if passwords match
            if password != cpassword:
                messages.error(request, 'Passwords do not match.')
            else:
                # Check if a user with the same email already exists
                if User.objects.filter(email=email).exists():
                    messages.error(request, 'An account with this email already exists.')
                else:
                    # Create new user
                    user = User.objects.create(
                        first_name=fname, last_name=lname, email=email, username=email
                    )
                    user.set_password(password)
                    user.save()
                    user.profiles.create(user=user, role='customer')  # Assuming there is a 'profiles' related model
                    messages.success(request, 'Your account has been created! You can now log in.')
                    return redirect('login')

    # Handle the GET request
    cart_items = str(len(request.session.get('cart_products', [])))
    return render(request, 'login.html', {'cart_items': cart_items})

def logout_user(request):
    if not request.user.is_authenticated:
        return redirect('index')
    logout(request)
    system_messages = messages.get_messages(request)
    for message in system_messages:
        # This iteration is necessary
        pass
    return redirect('index')


