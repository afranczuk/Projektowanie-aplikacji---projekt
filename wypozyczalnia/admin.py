from django.contrib import admin
from .models import Kategoria, Samochod

@admin.register(Kategoria)
class KategoriaAdmin(admin.ModelAdmin):
    list_display = ('nazwa', 'opis')

@admin.register(Samochod)
class SamochodAdmin(admin.ModelAdmin):
    list_display = ('marka', 'model', 'numer_vin', 'rok_produkcji', 'kolor', 'cena_za_dobe', 'kategoria', 'wlasciciel', 'data_dodania')
    list_filter = ('kategoria', 'wlasciciel')
    search_fields = ('marka', 'model', 'numer_vin')
