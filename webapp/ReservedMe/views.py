from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import CustomUser
from django.contrib.auth import login, logout

# Create your views here.
def index(request):
    return render(request, 'reservedme/index.html')

def kontakt(request):
    return render(request, 'reservedme/kontakt.html')

def o_nas(request):
    return render(request, 'reservedme/o_nas.html')

def base(request):
    return render(request, 'reservedme/base.html')

def logowanie(request):
    return render(request, 'reservedme/logowanie.html')

def rejestracja(request):
    return render(request, 'reservedme/rejestracja.html')

def rezerwacja(request):
    return render(request, 'reservedme/rezerwacja.html')

def login(request):
    return render(request, 'reservedme/login.html')

def logout_user(request):
     logout(request)
     return redirect('home')