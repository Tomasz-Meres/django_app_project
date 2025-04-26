from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import CustomUser
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages #to show message back for errors
from django.contrib.auth.models import User

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

def login(request):
    return render(request, 'reservedme/login.html')

def logout_user(request):
     logout(request)
     return redirect('index')


def login_user(request):
    if request.method == "POST":
        email = request.POST['email']
        password = request.POST['password']

        # Próba zalogowania na podstawie emaila
        user = CustomUser.objects.filter(email=email).first()
        
        if user is not None:
            user = authenticate(request, username=user.username, password=password)
            if user is not None:
                login(request, user)
                return redirect('home')  # Zmien na odpowiednią stronę docelową
            else:
                messages.error(request, "Błędne hasło.")
        else:
            messages.error(request, "Użytkownik o podanym adresie e-mail nie istnieje.")
        
    return render(request, 'login.html')