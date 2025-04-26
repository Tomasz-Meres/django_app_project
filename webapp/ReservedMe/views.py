from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import CustomUser
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages 


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
        password = request.POST['haslo']

        # Authenticate user using email (custom user model)
        user = authenticate(request, username=email, password=password)

        if user is not None:
            login(request, user)
            return redirect('home') 
        else:
            messages.error(request, "Błędne hasło lub e-mail.")
    
    return render(request, 'reservedme/login.html')

def register(request):
    if request.method == 'POST':
        fname = request.POST['imie']
        lname = request.POST['nazwisko']
        email = request.POST['email']
        password = request.POST['haslo']
        nr_tel = request.POST['telefon']

        if CustomUser.objects.filter(email=email).exists():
            messages.error(request, "Użytkownik z tym adresem e-mail już istnieje.")
            return redirect('rejestracja')
        
        username = f"{fname} {lname[0]}"
        user = CustomUser.objects.create_user(
            username=username,  # username nie musi być unikalne
            email=email, 
            password=password,
            first_name=fname,
            last_name=lname,
            nr_tel=nr_tel
            )
        login(request, user)
        return redirect('home')
    return render(request, 'main/users/rejestracja.html')