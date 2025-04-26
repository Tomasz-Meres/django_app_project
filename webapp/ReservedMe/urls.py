from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='home'),  # Główna strona
    path('kontakt/', views.kontakt, name='kontakt'),  # Strona Kontakt
    path('o-nas/', views.o_nas, name='o_nas'),  # Strona O nas
    path('base/', views.base, name='base'),  # Strona szablon
    path('profil/', views.base, name='profil'),  # Strona profilu
    path('logowanie/', views.logowanie, name='logowanie'),  # Strona szablon
    path('rejestracja/', views.rejestracja, name='rejestracja'),  # Strona szablon
    path('rezerwacja/', views.rezerwacja, name='rezerwacja'),  # Strona szablon
    path('login/', views.login, name='login'),  # Strona szablon
    path('logout/', views.logout_user, name='logout'),
]