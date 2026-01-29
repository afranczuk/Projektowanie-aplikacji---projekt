from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator, MinLengthValidator 
from django.contrib.auth.models import User
from django.core.validators import RegexValidator 

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
   # wynajety = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.marka} {self.model} ({self.rok_produkcji})"

    def aktualny_wynajem(self):
        from datetime import date
        # Szukamy wynajmu tego auta, który trwa dzisiaj
        return self.wynajem_set.filter(data_od__lte=date.today(), data_do__gte=date.today()).first()
 
class Wynajem(models.Model):
    samochod = models.ForeignKey('Samochod', on_delete=models.CASCADE)
    uzytkownik = models.ForeignKey('auth.User', on_delete=models.CASCADE)

    data_od = models.DateField()
    data_do = models.DateField()

    ilosc_dni = models.PositiveIntegerField()
    laczna_cena = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.samochod} – {self.uzytkownik.username}"



class WniosekWlasciciel(models.Model):
    uzytkownik = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    imie = models.CharField(max_length=100)
    nazwisko = models.CharField(max_length=100)
    regulamin = models.BooleanField(default=False) # To jest Twój regulamin
    zatwierdzony = models.BooleanField(default=False) # To jest ten przycisk do akceptacji
    data_wyslania = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Wniosek od {self.uzytkownik.username}"

class UserProfil(models.Model):
    user = models.OneToOneField('auth.User', on_delete=models.CASCADE)
    posiada_prawo_jazdy = models.BooleanField(default=False)
    
    # Poprawione pole z walidacją
    numer_telefonu = models.CharField(
        max_length=12, 
        default="+48",
        validators=[
            RegexValidator(
                regex=r'^\+?\d{9,12}$', 
                message="Numer telefonu może zawierać tylko cyfry i opcjonalnie '+' na początku."
            )
        ]
    )

    def __str__(self):
        return f"Profil: {self.user.username}"