from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import CustomUser, Hotel, Pokoj, Rezerwacja
from django.contrib.auth import login, logout, authenticate, update_session_auth_hash
from django.contrib import messages 
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.conf import settings
import re
import os
import uuid
from datetime import datetime, date
from decimal import Decimal

# Create your views here.

# Szablony stron
def base(request):
    return render(request, 'reservedme/base.html')

def base_account(request):
    return render(request, 'reservedme/base-account.html')


# Strony widoczne bez zalogowania
def index(request):
    hotele = Hotel.objects.all()
    if request.method == 'GET':
        city = request.GET.get('city')
        start = request.GET.get('checkin')
        end = request.GET.get('checkout')

        if start and end:
            checkin = datetime.strptime(start, '%Y-%m-%d').date() 
            checkout = datetime.strptime(end, '%Y-%m-%d').date() 
            valid, message = search_check(checkin, checkout)
            if not valid:
                return render(request, 'reservedme/index.html', {'hotele': hotele, 'error': message
                })
            
            sql = """
                SELECT h.id
                FROM ReservedMe_Pokoj p
                JOIN ReservedMe_Hotel h ON h.id = p.hotel_id
                WHERE p.id NOT IN (
                    SELECT r.pokoj_id
                    FROM ReservedMe_Rezerwacja r
                    JOIN ReservedMe_Pokoj p2 ON r.pokoj_id = p2.id
                    WHERE r.id IS NOT NULL
                    AND (%s >= r.data_rozpoczecia AND %s < r.data_zakonczenia)
                )
                AND p.id NOT IN (
                    SELECT r.pokoj_id
                    FROM ReservedMe_Rezerwacja r
                    JOIN ReservedMe_Pokoj p2 ON r.pokoj_id = p2.id
                    WHERE r.id IS NOT NULL
                    AND (%s >= r.data_rozpoczecia AND %s < r.data_zakonczenia)
                )
                AND h.miasto = %s
                GROUP BY h.id
            """
            params = [checkin, checkin, checkout, checkout, city]

            hotele_id = [h.id for h in Rezerwacja.objects.raw(sql, params)]
            hotele = Hotel.objects.filter(pk__in=hotele_id)


    return render(request, 'reservedme/index.html', {'hotele': hotele})

def kontakt(request):
    return render(request, 'reservedme/kontakt.html')

def o_nas(request):
    return render(request, 'reservedme/o_nas.html')

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
def my_reservations_view(request):
    user = request.user.id

    sql = """
            SELECT
                r.id,
                h.nazwa,
                h.miasto,
                h.ulica,
                p.ilu_osobowy,
                r.calkowita_cena,
                r.data_rozpoczecia,
                r.data_zakonczenia,
                r.data_wykonania,
                h.telefon
            FROM
                ReservedMe_Rezerwacja r
            JOIN ReservedMe_Hotel h ON r.hotel_id = h.id
            JOIN ReservedMe_Pokoj p ON r.pokoj_id = p.id
            WHERE r.uzytkownik_id = %s
            ORDER BY r.data_wykonania DESC
            """
    params = [user]
    
    my_reservations = Rezerwacja.objects.raw(sql, params) 


    sql1 = """
        SELECT
            r.id,
            h.nazwa,
            h.miasto,
            h.ulica,
            p.ilu_osobowy,
            r.calkowita_cena,
            r.data_rozpoczecia,
            r.data_zakonczenia,
            r.data_wykonania,
            u.nr_tel,
            u.first_name,
            u.last_name
        FROM ReservedMe_Rezerwacja r
        JOIN ReservedMe_Hotel h ON r.hotel_id = h.id
        JOIN ReservedMe_Pokoj p ON r.pokoj_id = p.id
        JOIN ReservedMe_CustomUser u ON r.uzytkownik_id = u.id
        WHERE h.uzytkownik_id = %s
        ORDER BY r.data_wykonania DESC
    """

    params1 = [user]  
    hotel_reservations = Rezerwacja.objects.raw(sql1, params1) 
    return render(request, 'reservedme/my_reservations.html', {'my_reservations': my_reservations, 'hotel_reservations': hotel_reservations})

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

    return render(request, 'reservedme/profile.html') 

def search_check(checkin, checkout):
    today = date.today()
    if checkin > checkout:
        return False, 'Data zameldowania jest większa od daty wymeldowania'
    if checkin < today:
        return False, 'Data zameldowania jest mniejsza od dzisiejszej daty'
    if checkout < today:
        return False, 'Data wymeldowania jest mniejsza od dzisiejszej daty'
    return True, ''



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
        zdjecie = request.FILES.get('zdjecie')

        image_name = ''
        if not kraj:
            kraj = 'Polska' 

        if not opis:
            opis = 'Brak opisu'
        
        if zdjecie:
            ext = os.path.splitext(zdjecie.name)[1]  
            image_name = f"{uuid.uuid4().hex}{ext}"  # unikalna nazwa
            save_path = os.path.join(settings.BASE_DIR, 'ReservedMe', 'static', 'reservedme', 'img', image_name)

            with open(save_path, 'wb+') as destination:
                for chunk in zdjecie.chunks():
                    destination.write(chunk)
            zdjecie_nazwa = image_name
        else:
            zdjecie_nazwa = ''

        Hotel.objects.create(
            uzytkownik= request.user,
            nazwa=nazwa,
            miasto=miasto,
            ulica=ulica,
            kraj=kraj,
            opis=opis,
            telefon=nr_tel,
            email=email, 
            zdjecie=zdjecie_nazwa
        )
        
        return redirect('add_hotel')
    return render(request, 'reservedme/profile.html')

# dodanie pokoju do hotelu
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
    return render(request, 'reservedme/profile.html')

# wyswietlanie listy hoteli danego użytkownika
def hotel_list(request):
    hotele = Hotel.objects.filter(uzytkownik=request.user)
    return render(request, 'reservedme/hotel_list.html', {'hotels': hotele})


# wyswietlanie Wszystkich hoteli
def all_hotel_list(request):
    hotele = Hotel.objects.all()
    return render(request, 'reservedme/index.html', {'hotele': hotele})

# Wyświetlanie pokoi dla wybranego hotelu
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
        zdjecie = request.FILES.get('zdjecie')
        

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
            ext = os.path.splitext(zdjecie.name)[1]  # np. ".jpg"
            image_name = f"{uuid.uuid4().hex}{ext}"  # unikalna nazwa
            save_path = os.path.join(settings.BASE_DIR, 'ReservedMe', 'static', 'reservedme', 'img', image_name)

            with open(save_path, 'wb+') as destination:
                for chunk in zdjecie.chunks():
                    destination.write(chunk)

            hotel_obj.zdjecie = image_name 

        hotel_obj.save() 
    return redirect('hotel_list')


def hotel_view(request):
    if request.method == 'GET':
        hotel_id = request.GET['hotel_id']
        hotel = get_object_or_404(Hotel, pk=hotel_id)
        pokoje = Pokoj.objects.filter(hotel_id=hotel_id)

        start = request.GET.get('checkin')
        end = request.GET.get('checkout')
        guests = request.GET.get('guests')
        rooms = request.GET.get('rooms')
        wyniki = []
        dni_pobytu = 0
        daty = {}

        # Sprawdzenie dat
        if start and end:
            checkin = datetime.strptime(start, '%Y-%m-%d').date() 
            checkout = datetime.strptime(end, '%Y-%m-%d').date() 

            valid, message = search_check(checkin, checkout)
            if not valid:
                # Zwróć odpowiedź z błędem lub renderuj z komunikatem
                return render(request, 'reservedme/hotel.html', {'hotel': hotel, 'pokoje': pokoje,
                    'error': message,
                })

            sql = """
                SELECT p.id, p.hotel_id, p.*
                FROM ReservedMe_Pokoj p
                JOIN ReservedMe_Hotel h ON h.id = p.hotel_id
                WHERE p.id NOT IN (
                    SELECT r.pokoj_id
                    FROM ReservedMe_Rezerwacja r
                    JOIN ReservedMe_Pokoj p2 ON r.pokoj_id = p2.id
                    WHERE r.id IS NOT NULL
                    AND (%s >= r.data_rozpoczecia AND %s < r.data_zakonczenia)
                )
                AND p.id NOT IN (
                    SELECT r.pokoj_id
                    FROM ReservedMe_Rezerwacja r
                    JOIN ReservedMe_Pokoj p2 ON r.pokoj_id = p2.id
                    WHERE r.id IS NOT NULL
                    AND (%s >= r.data_rozpoczecia AND %s < r.data_zakonczenia)
                )
                AND p.hotel_id = %s
                AND p.ilu_osobowy = %s
                AND p.liczba_pokoi = %s;
            """
            params = [checkin, checkin, checkout, checkout, hotel_id, guests, rooms]
            
            pokoje = Pokoj.objects.raw(sql, params)
            dni_pobytu = (checkout - checkin).days
            daty = {'checkin': checkin,
                    'checkout': checkout,
                    'dni_pobytu': dni_pobytu}
            wyniki = []
            for pokoj in pokoje:
                if dni_pobytu:
                    cena_za_pobyt = pokoj.cena_za_noc * dni_pobytu
                else:
                    cena_za_pobyt = pokoj.cena_za_noc
                wyniki.append({
                    'pokoj': pokoj,
                    'cena_za_pobyt': cena_za_pobyt
                })  


    return render(request, 'reservedme/hotel.html', {'hotel': hotel, 'pokoje': pokoje, 'wyniki': wyniki, 'daty': daty})

def book_room(request):
    if request.method == 'POST':
        hotel_id = request.POST['hotel_id']
        pokoj_id = request.POST['pokoj_id']
        hotel = get_object_or_404(Hotel, pk=hotel_id)
        pokoj = get_object_or_404(Pokoj, pk=pokoj_id)
        user = request.user

        price_str = request.POST['price']
        price = price_str.replace(',', '.').strip()

        start = request.POST['checkin']
        end = request.POST['checkout']
        checkin = datetime.strptime(start, '%Y-%m-%d').date() 
        checkout = datetime.strptime(end, '%Y-%m-%d').date() 
        

        Rezerwacja.objects.create(
            hotel=hotel, pokoj=pokoj, uzytkownik=user, 
            data_rozpoczecia=checkin, data_zakonczenia=checkout, 
            calkowita_cena=Decimal(price), data_wykonania=date.today()
        )
        return redirect('my_reservations')
    return render(request, 'reservedme/index.html')

def delete_reservation(request):
    if request.method == 'POST':
        reservation_id = request.POST['reservation']
        rezervation = get_object_or_404(Rezerwacja, pk=reservation_id)
        rezervation.delete()
    return redirect('my_reservations')