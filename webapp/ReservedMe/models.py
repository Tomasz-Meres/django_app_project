from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings

# Create your models here.

# Model dla użytkownika
class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    nr_tel = models.CharField(max_length=20)
    username = models.CharField(max_length=150, blank=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username','first_name', 'last_name']
    
    
    def __str__(self):
        return f"{self.first_name} {self.last_name}"

# Model dla hotelu
class Hotel(models.Model):
    uzytkownik = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="hotele"
    )
    nazwa = models.CharField(max_length=255)
    miasto = models.CharField(max_length=100)
    ulica = models.CharField(max_length=255)
    kraj = models.CharField(max_length=100, default="Polska")
    opis = models.TextField(default="")
    telefon = models.CharField(max_length=20)
    email = models.EmailField(max_length=255)
    zdjecie = models.CharField(max_length=255, default="")

#  Model dla pokoju
class Pokoj(models.Model):
    hotel = models.ForeignKey(
        'Hotel',  # Odwołanie do modelu Hotel
        on_delete=models.CASCADE,
        related_name="pokoje"
    )
    ilu_osobowy = models.IntegerField()
    liczba_pokoi = models.IntegerField()
    numer_pokoju = models.IntegerField()
    cena_za_noc = models.DecimalField(max_digits=10, decimal_places=2)
    def cena_za_pobyt(self, liczba_nocy):
        return self.cena_za_noc * liczba_nocy    

# Model dla rezerwacji
class Rezerwacja(models.Model):
    hotel = models.ForeignKey(
        'Hotel',  # Odwołanie do modelu Hotel
        on_delete=models.CASCADE,
        related_name="rezerwacje"
    )
    pokoj = models.ForeignKey(
        'Pokoj',  # Odwołanie do modelu Pokoj
        on_delete=models.CASCADE,
        related_name="rezerwacje"
    )
    uzytkownik = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="rezerwacje"
    )
    data_rozpoczecia= models.DateField()
    data_zakonczenia = models.DateField()
    calkowita_cena = models.DecimalField(max_digits=10, decimal_places=2)
    data_wykonania = models.DateTimeField(auto_now_add=True)  # Automatycznie dodana data i czas utworzenia rezerwacji
