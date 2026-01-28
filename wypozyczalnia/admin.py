from django.contrib import admin
from .models import Kategoria, Samochod, UserProfil, WniosekWlasciciel


@admin.register(Kategoria)
class KategoriaAdmin(admin.ModelAdmin):
    list_display = ('nazwa', 'opis')

@admin.register(Samochod)
class SamochodAdmin(admin.ModelAdmin):
    list_display = ('marka', 'model', 'numer_vin', 'rok_produkcji', 'kolor', 'cena_za_dobe', 'kategoria', 'wlasciciel', 'data_dodania')
    list_filter = ('kategoria', 'wlasciciel')
    search_fields = ('marka', 'model', 'numer_vin')


    # kto moze edytowac cene:
    def get_readonly_fields(self, request, obj=None):
        # pracownik nie bedacy wlasceielem = blokada edytowania ceny za dobe
        if request.user.groups.filter(name='Pracownicy').exists() and not request.user.is_superuser:
            return ('cena_za_dobe',) 
        
        return ()  #wlasciel i superuser maja mozliwosc edytowania wszystkiego

    # kto co widzi
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        
        # pracownik i superuser maja widziec wszystkie ofery
        if request.user.is_superuser or request.user.groups.filter(name='Pracownicy').exists():
            return qs
            
        # Wlasciciel nie widzi aut innuch wlascicieli
        return qs.filter(wlasciciel=request.user)
    

    #automatyczne przypisywanie wlasciciela do dodawanych aut
    def save_model(self, request, obj, form, change): 
        if not obj.pk: 
            obj.wlasciciel = request.user
        super().save_model(request, obj, form, change)

class UserProfilAdmin(admin.ModelAdmin):
    list_display = ('user', 'posiada_prawo_jazdy', 'numer_telefonu')
    list_filter = ('posiada_prawo_jazdy',)


from django.contrib import admin, messages
from django.contrib.auth.models import Group
from .models import WniosekWlasciciel

@admin.register(WniosekWlasciciel)
class WniosekWlascicielAdmin(admin.ModelAdmin):
    list_display = ('uzytkownik', 'imie', 'nazwisko', 'zatwierdzony')
    actions = ['zatwierdz_wnioski'] # Dodajemy akcję do listy

    @admin.action(description="Zatwierdź wybrane wnioski i dodaj do grupy Wlasciciel")
    def zatwierdz_wnioski(self, request, queryset):
        # Pobieramy (lub tworzymy na wszelki wypadek) grupę
        grupa_wlasciciel, _ = Group.objects.get_or_create(name='Wlasciciel')
        
        licznik = 0
        for wniosek in queryset:
            if not wniosek.zatwierdzony:
                # 1. Dodajemy użytkownika do grupy
                wniosek.uzytkownik.groups.add(grupa_wlasciciel)
                # 2. Oznaczamy wniosek jako zatwierdzony
                wniosek.zatwierdzony = True
                wniosek.save()
                licznik += 1
        
        self.message_user(request, f"Pomyślnie zatwierdzono {licznik} wniosków.")