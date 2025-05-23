from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import CustomUser, Hotel, Pokoj, Rezerwacja
from django.contrib.auth import login, logout, authenticate, update_session_auth_hash
from django.contrib import messages 
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
import re



# Create your views here.

# Szablony stron
def base(request):
    return render(request, 'reservedme/base.html')

def base_account(request):
    return render(request, 'reservedme/base-account.html')


# Strony widoczne bez zalogowania
def index(request):
    hotele = Hotel.objects.all()
    return render(request, 'reservedme/index.html', {'hotele': hotele})

def kontakt(request):
    return render(request, 'reservedme/kontakt.html')

def o_nas(request):
    return render(request, 'reservedme/o_nas.html')

def profil(request):
    return render(request, 'reservedme/profil.html')

def rejestracja(request):
    return render(request, 'reservedme/rejestracja.html')

def logowanie(request):
    return render(request, 'reservedme/logowanie.html')


# Strony widoczne po zalogowaniu

@login_required
def add_hotel_view(request):
    return render(request, 'reservedme/add_hotel.html')

@login_required
def manage_rooms(request):
    return render(request, 'reservedme/manage_rooms.html')

@login_required
def favourite_hotels_view(request):
    return render(request, 'reservedme/favourite_hotels.html')

@login_required
def my_reservations_view(request):
    return render(request, 'reservedme/my_reservations.html')

@login_required
def profile_view(request):
    user = request.user
    return render(request, 'reservedme/profile.html', {'user': user})

@login_required
def add_rooms(request):
    hotele = Hotel.objects.filter(uzytkownik=request.user)
    return render(request, 'reservedme/add_rooms.html', {'hotele': hotele})


# Logowanie, wylogowanie oraz rejestracja użytkownikiów

def logout_user(request):
     logout(request)
     return redirect('home')

def login_user(request):
    if request.method == "POST":
        email = request.POST['email']
        password = request.POST['haslo']

        # Autentykacja przy użyciu CustomUser model
        user = authenticate(request, username=email, password=password)

        if user is not None:
            login(request, user)
            return redirect('home') 
        else:
            messages.error(request, "Błędne hasło lub e-mail.")
    
    return render(request, 'reservedme/logowanie.html')

def validate_password(password):
    if len(password) < 8:
        return False, 'Hasło musi mieć conajmniej 8 znaków'

    if not re.search(r'[a-z]', password):
        return False, 'Hasło musi zawierać min. 1 małą literę'

    if not re.search(r'[A-Z]', password):
        return False, 'Hasło musi zawierać min. 1 dużą literę'
    
    if not re.search(r'[0-9]', password):
        return False, 'Hasło musi zawierać min. 1 cyfrę'    
    
    if not re.search(r'[!@#$]', password):
        return False, 'Hasło musi zawierać min. 1 znak specjalny'
    return True, ''

def register(request):
    if request.method == 'POST':
        fname = request.POST['imie']
        lname = request.POST['nazwisko']
        email = request.POST['email']
        password = request.POST['haslo']
        password2 = request.POST['powtorzHaslo']
        nr_tel = request.POST['telefon']

        if CustomUser.objects.filter(email=email).exists():
            messages.error(request, "Użytkownik z tym adresem e-mail już istnieje.")
            return redirect('rejestracja')
        
        if password != password2:
            messages.error(request, "Hasła nie są identyczne")
            return redirect('rejestracja')
        
        is_valid, message = validate_password(password)
        if not is_valid:
            messages.error(request, message)
            return redirect('rejestracja',) 


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
    return render(request, 'reservedme/rejestracja.html')

def change_password(request):
    if request.method == 'POST':
        stare_haslo = request.POST.get('haslo')
        nowe_haslo = request.POST.get('noweHaslo')
        powtorz_haslo = request.POST.get('powtorzHaslo')

        user = request.user

        if not user.check_password(stare_haslo):
            messages.error(request, "Stare hasło jest niepoprawne.")
        elif nowe_haslo != powtorz_haslo:
            messages.error(request, "Nowe hasła nie są takie same.")
        else:
            valid, error_msg = validate_password(nowe_haslo)
            if not valid:
                messages.error(request, error_msg)
            else:
                user.set_password(nowe_haslo)
                user.save()
                update_session_auth_hash(request, user)  # zapobiega wylogowaniu
                messages.success(request, "Hasło zostało zmienione pomyślnie.")
                return redirect('profile')

    return render(request, 'reservedme/profile.html')  # tam gdzie masz ten formularz

def search(request):
    return redirect('home')

# Zarządzanie hotelami

# dodanie nowego hotelu
def add_hotel(request):
    if request.method == 'POST':
        nazwa = request.POST['nazwa']
        miasto = request.POST['miasto']
        ulica = request.POST['ulica']
        opis = request.POST.get('opis') 
        kraj = request.POST.get('kraj') 
        email = request.POST['email']
        nr_tel = request.POST['telefon']
       # zdjecie = request.POST['zdjecie']
        
        if not kraj:
            kraj = 'Polska' 

        if not opis:
            opis = 'Brak opisu'

        Hotel.objects.create(
            uzytkownik= request.user,
            nazwa=nazwa,
            miasto=miasto,
            ulica=ulica,
            kraj=kraj,
            opis=opis,
            telefon=nr_tel,
            email=email, 
            # zdjecie=zdjecie
             
        )
        
        return redirect('add_hotel')
    return render(request, 'reservedme/profil.html')

def add_room(request):
    if request.method == 'POST':
        hotel_id = request.POST['hotel']
        ile_osob = request.POST['ile_osob']
        ile_pokoi = request.POST['pokoje']
        nr_pok = request.POST['nr_pok']
        cena = request.POST['cena']
    
        hotel_obj = Hotel.objects.get(id=hotel_id)

        if not nr_pok:
            nr_pok = 0

    
        Pokoj.objects.create(
            hotel=hotel_obj,
            ilu_osobowy = ile_osob,
            liczba_pokoi = ile_pokoi,
            numer_pokoju = nr_pok,
            cena_za_noc = cena
        )
        
        return redirect('add_rooms')
    return render(request, 'reservedme/profil.html')

# wyswietlanie listy hoteli danego użytkownika
def hotel_list(request):
    hotele = Hotel.objects.filter(uzytkownik=request.user)
    return render(request, 'reservedme/hotel_list.html', {'hotels': hotele})


# wyswietlanie Wszystkich hoteli
def all_hotel_list(request):
    hotele = Hotel.objects.all()
    return render(request, 'reservedme/index.html', {'hotele': hotele})


def hotel_management(request):
    hotele = Hotel.objects.filter(uzytkownik=request.user)
    pokoje = Pokoj.objects.filter(hotel__in=hotele)
    return render(request, 'reservedme/manage_rooms.html', {'hotele': hotele})


# Usuwanie hotelu
def remove_hotel(request):
    if request.method == 'POST':
        id = request.POST['hotel_id']
        hotel = get_object_or_404(Hotel, pk=id)
        hotel.delete()

    return redirect('hotel_list')

# Wyświetlanie pokoi konkretnego hotelu
def display_rooms(request):
    if request.method == 'POST':
        hotel_id = request.POST['hotel_id']
        hotele = Hotel.objects.filter(uzytkownik=request.user)
        display_hotel = get_object_or_404(hotele, id=hotel_id)
        pokoje = Pokoj.objects.filter(hotel=display_hotel)
    return render(request, 'reservedme/manage_rooms.html', {'hotele': hotele, 'pokoje': pokoje})

# Usuwanie pokoju
def remove_room(request):
    if request.method == 'POST':
        id = request.POST['room_id']
        room = get_object_or_404(Pokoj, pk=id)
        room.delete()
    return redirect('manage_rooms')

# Edytowanie hotelu
def edit_hotel(request):
    if request.method == 'POST':
        id = request.POST['hotel']
        hotel_obj = get_object_or_404(Hotel, pk=id)
        nazwa = request.POST['nazwa']
        miasto = request.POST['miasto']
        ulica = request.POST['ulica']
        opis = request.POST.get('opis') 
        kraj = request.POST.get('kraj') 
        email = request.POST['email']
        nr_tel = request.POST['telefon']
        zdjecie = request.POST['zdjecie']
        

        if nazwa:
            hotel_obj.nazwa = nazwa
        if miasto:
            hotel_obj.miasto = miasto
        if ulica:
            hotel_obj.ulica = ulica
        if opis:
            hotel_obj.opis = opis
        if kraj:
            hotel_obj.kraj = kraj
        if email:
            hotel_obj.email = email
        if nr_tel:
            hotel_obj.telefon = nr_tel
        if zdjecie:
            hotel_obj.zdjecie = zdjecie

        hotel_obj.save() 
    return redirect('hotel_list')