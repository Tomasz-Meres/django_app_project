from django.contrib import admin
from .models import CustomUser, Hotel, Pokoj, Rezerwacja
from django.contrib.auth.admin import UserAdmin

# Rejestracja niestandardowego modelu użytkownika
admin.site.register(CustomUser, UserAdmin)

# Rejestracja innych modeli
admin.site.register(Hotel)
admin.site.register(Pokoj)
admin.site.register(Rezerwacja)