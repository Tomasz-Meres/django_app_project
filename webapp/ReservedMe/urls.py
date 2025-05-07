from django.urls import path
from . import views

urlpatterns = [
    # strona główna i podstrony widoczne bez logowania się
    path('', views.index, name='home'),  # Strona główna
    path('kontakt/', views.kontakt, name='kontakt'),  # Strona Kontakt
    path('o-nas/', views.o_nas, name='o_nas'),  # Strona O nas
    path('base/', views.base, name='base'),  # Strona szablon
    path('profil/', views.profil, name='profil'),  # Strona profilu
    path('rejestracja/', views.rejestracja, name='rejestracja'),  # Strona z formularzem rejestracji
    path('logowanie/', views.logowanie, name='logowanie'),  # Strona z formularzem logowania

    # Strony widoczne po zalogowaniu
    path('dodaj-hotel/', views.add_hotel_view, name='add_hotel'),  # Strona 
    path('dodaj-pokoje/', views.add_room_view, name='add_room'),  # Strona 
    path('ulubione-hotele/', views.favourite_hotels_view, name='favourite_hotels'),  # Strona 
    path('moje-rezerwacje/', views.my_reservations_view, name='my_reservations'),  # Strona 
    path('moje-dane/', views.profile_view, name='profile'),  # Strona 


    # Rejestracja oraz logowanie użytkonika
    path('login_user/', views.login_user, name='login_user'),  # Logowanie użytkownika
    path('logout_user/', views.logout_user, name="logout_user"),  # Wylogowanie używkownika
    path('register', views.register, name='register_user'), # Dodanie nowego użytkownika
    path('search', views.search, name='search'), # Szukanie hoteli w bazie danych

    path('base-account', views.base_account, name='base-account'),

    # Zarządzanie hotelami i rezerwacjami
    
]