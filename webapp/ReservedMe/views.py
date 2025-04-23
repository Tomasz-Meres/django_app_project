from django.shortcuts import render
from django.http import HttpResponse
from .models import CustomUser

# Create your views here.
def index(request):
    return render(request, 'reservedme/index.html')

def kontakt(request):
    return render(request, 'reservedme/kontakt.html')

def o_nas(request):
    return render(request, 'reservedme/o_nas.html')

def base(request):
    user = CustomUser.objects.get(id=request.user.id)
    context = {
        'user_name': user.__str__()
    }
    return render(request, 'reservedme/base.html', context)

def logowanie(request):
    return render(request, 'reservedme/logowanie.html')

def rejestracja(request):
    return render(request, 'reservedme/rejestracja.html')