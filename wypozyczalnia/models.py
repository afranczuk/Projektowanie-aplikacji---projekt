from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator, MinLengthValidator 
class Kategoria(models.Model):
    nazwa = models.CharField(max_length=100, unique=True)
    opis = models.TextField(blank=True)

    def __str__(self):
        return self.nazwa

class Samochod(models.Model):
    marka = models.CharField(max_length=100)
    model = models.CharField(max_length=100)
    numer_vin = models.CharField(max_length=17, validators=[MinLengthValidator(17)],unique=True, blank=False, null=False)
    rok_produkcji = models.IntegerField(default=2024, validators= [MinValueValidator(1900),MaxValueValidator(2026)])
    kolor = models.CharField(max_length=50, default="Czarny")
    cena_za_dobe = models.DecimalField(max_digits=8, decimal_places=2, default=0.00, validators=[MinValueValidator(1.00)])
    data_dodania = models.DateField(default=timezone.now)
    kategoria = models.ForeignKey(Kategoria, on_delete=models.CASCADE)
    wlasciciel = models.ForeignKey('auth.User', on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.marka} {self.model} ({self.rok_produkcji})"