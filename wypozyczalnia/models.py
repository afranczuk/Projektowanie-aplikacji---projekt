
from django.db import models
from django.utils import timezone

class Kategoria(models.Model):
    nazwa = models.CharField(max_length=100)
    opis = models.TextField(blank=True)

    def __str__(self):
        return self.nazwa

class Samochod(models.Model):
    marka = models.CharField(max_length=100)
    model = models.CharField(max_length=100)
    data_dodania = models.DateField(default=timezone.now)
    kategoria = models.ForeignKey(Kategoria, on_delete=models.CASCADE)
    wlasciciel = models.ForeignKey('auth.User', on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.marka} {self.model}"
    
class Samochod(models.Model):
    marka = models.CharField(max_length=100)
    model = models.CharField(max_length=100)
    cena_za_dobe = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)
    data_dodania = models.DateField(default=timezone.now)
    kategoria = models.ForeignKey(Kategoria, on_delete=models.CASCADE)
    wlasciciel = models.ForeignKey('auth.User', on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.marka} {self.model} - {self.cena_za_dobe} zł" 
