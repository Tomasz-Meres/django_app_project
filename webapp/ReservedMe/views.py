from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import CustomUser
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages #to show message back for errors


# Create your views here.
def index(request):
    return render(request, 'reservedme/index.html')

def kontakt(request):
    return render(request, 'reservedme/kontakt.html')

def o_nas(request):
    return render(request, 'reservedme/o_nas.html')

def base(request):
    return render(request, 'reservedme/base.html')

def rejestracja(request):
    return render(request, 'reservedme/rejestracja.html')

def rezerwacja(request):
    return render(request, 'reservedme/rezerwacja.html')

def logowanie(request):
    return render(request, 'reservedme/logowanie.html')

def logout_user(request):
     logout(request)
     return redirect('home')

def login_user(request):
    if request.method == "POST":
        email = request.POST['email']
        password = request.POST['password']

        # Authenticate user using email (custom user model)
        user = authenticate(request, username=email, password=password)

        if user is not None:
            login(request, user)
            return redirect('home') 
        else:
            messages.error(request, "Błędne hasło lub e-mail.")
    
    return render(request, 'reservedme/login.html')

def register(request):
     return render(request, 'main/users/rejestracja.html')