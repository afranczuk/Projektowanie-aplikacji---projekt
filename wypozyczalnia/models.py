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
 
class Wynajem(models.Model):
    samochod = models.ForeignKey('Samochod', on_delete=models.CASCADE)
    uzytkownik = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    data_wynajmu = models.DateField(default=timezone.now)
    ilosc_dni = models.PositiveIntegerField(default=1)
    data_od = models.DateField(null=True, blank=True)
    data_do = models.DateField(null=True, blank=True)
    laczna_cena = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    def __str__(self):
        return f"{self.samochod} wynajęty przez {self.uzytkownik.username}"
    
class UserProfil(models.Model):
    user = models.OneToOneField('auth.User', on_delete=models.CASCADE)
    posiada_prawo_jazdy = models.BooleanField(default=False)
    numer_telefonu = models.CharField(max_length=12, default="+48",validators=[MinLengthValidator(12)])

    def __str__(self):
        return f"Profil: {self.user.username}"

class Wynajem(models.Model):
    samochod = models.ForeignKey('Samochod', on_delete=models.CASCADE)
    uzytkownik = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    data_wynajmu = models.DateField(default=timezone.now)
    ilosc_dni = models.PositiveIntegerField(default=1)
    data_od = models.DateField(null=True, blank=True)
    data_do = models.DateField(null=True, blank=True)
    laczna_cena = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    def __str__(self):
        return f"{self.samochod} wynajęty przez {self.uzytkownik.username}"