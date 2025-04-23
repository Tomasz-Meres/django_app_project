from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.

# Model uzytkownika z dodatkowym polem nr_tel oraz z logowaniem za pomocą emaila
class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    nr_tel = models.CharField(max_length=20)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']
    
    def __str__(self):
        return self.email

