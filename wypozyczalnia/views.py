from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import RejestracjaForm, WniosekWlascicielForm, WynajemForm, SamochodForm
from .models import UserProfil, Samochod, Wynajem, WniosekWlasciciel
from datetime import date
from django.db.models import Sum # Dodaj ten import na górze!
from django.contrib.auth import logout



def rejestracja(request):
    if request.method == 'POST':
        form = RejestracjaForm(request.POST)
        if form.is_valid():
            user = form.save()
            UserProfil.objects.create(
                user=user,
                posiada_prawo_jazdy=form.cleaned_data.get('posiada_prawo_jazdy'),
                numer_telefonu=form.cleaned_data.get('numer_telefonu')
            )
            return redirect('logowanie')
    else:
        form = RejestracjaForm()
    return render(request, 'uzytkownik_rejestracja.html', {'form': form})

def strona_glowna(request):
    samochody = Samochod.objects.all()
    is_wlasciciel = False
    if request.user.is_authenticated:
        # Sprawdzamy grupę 'Wlasciciel'
        is_wlasciciel = request.user.groups.filter(name='Wlasciciel').exists()

    zajete_auta_ids = Wynajem.objects.filter(
        data_do__gte=date.today()
    ).values_list('samochod_id', flat=True)

    return render(request, 'strona_glowna.html', {
        'samochody': samochody,
        'is_wlasciciel': is_wlasciciel,
        'zajete_auta_ids': zajete_auta_ids,
    })

@login_required
def moje_auta(request):
    # Sprawdzamy, czy to właściciel/admin
    if not request.user.groups.filter(name='Wlasciciel').exists() and not request.user.is_superuser:
        return redirect('home')

    # TUTAJ JEST BŁĄD – MUSI BYĆ FILTER, A NIE ALL
    # Pobieramy TYLKO auta, których właścicielem jest zalogowany użytkownik (request.user)
    samochody = Samochod.objects.filter(wlasciciel=request.user).prefetch_related('wynajem_set')

    # To samo dla zarobków – liczymy tylko z aut tego konkretnego właściciela
    total_zarobek = Wynajem.objects.filter(
        samochod__wlasciciel=request.user
    ).aggregate(Sum('laczna_cena'))['laczna_cena__sum'] or 0

    return render(request, 'moje_auta.html', {
        'samochody': samochody,
        'dzisiaj': date.today(),
        'total_zarobek': total_zarobek
    })




@login_required
def moje_wynajmy(request):
    wynajmy = Wynajem.objects.filter(uzytkownik=request.user).select_related('samochod__wlasciciel')
    return render(request, 'moje_wynajmy.html', {
        'wynajmy': wynajmy,
        'dzisiaj': date.today()  # TA LINIA JEST NIEZBĘDNA DLA PRZYCISKÓW
    })

@login_required
def wynajem_szczegoly(request, auto_id):
    auto = get_object_or_404(Samochod, id=auto_id)
    if request.method == 'POST':
        form = WynajemForm(request.POST)
        if form.is_valid():
            data_od = form.cleaned_data['data_od']
            data_do = form.cleaned_data['data_do']

            czy_zajety = Wynajem.objects.filter(
                samochod=auto,
                data_od__lte=data_do,
                data_do__gte=data_od
            ).exists()

            if czy_zajety:
                messages.error(request, "Ten samochód jest już wynajęty w wybranym terminie.")
                return redirect('wynajem_szczegoly', auto_id=auto.id)

            ilosc_dni = (data_do - data_od).days + 1
            laczna_cena = ilosc_dni * auto.cena_za_dobe

            wynajem = Wynajem.objects.create(
                samochod=auto,
                uzytkownik=request.user,
                data_od=data_od,
                data_do=data_do,
                ilosc_dni=ilosc_dni,
                laczna_cena=laczna_cena
            )
            return redirect('po_wynajeciu', wynajem_id=wynajem.id)
    else:
        form = WynajemForm()

    return render(request, 'wynajem_szczegoly.html', {'auto': auto, 'form': form})

@login_required
def po_wynajeciu(request, wynajem_id):
    wynajem = get_object_or_404(Wynajem, id=wynajem_id, uzytkownik=request.user)
    return render(request, 'po_wynajeciu.html', {'wynajem': wynajem})

@login_required
def wniosek_o_wlasciciela(request):
    if request.method == 'POST':
        form = WniosekWlascicielForm(request.POST)
        if form.is_valid():
            wniosek = form.save(commit=False)
            wniosek.uzytkownik = request.user
            wniosek.save()
            messages.success(request, "Twój wniosek został wysłany.")
            return redirect('home')
    else:
        form = WniosekWlascicielForm()
    return render(request, 'wniosek_o_wlasciciela.html', {'form': form})

@login_required
def dodaj_auto(request):
    # 1. Strażnik dostępu
    if not request.user.groups.filter(name='Wlasciciel').exists() and not request.user.is_superuser:
        messages.error(request, "Tylko właściciele mogą dodawać auta.")
        return redirect('home')

    if request.method == 'POST':
        form = SamochodForm(request.POST)
        if form.is_valid():
            # 2. Tworzymy obiekt auta, ale jeszcze go nie wysyłamy do bazy (commit=False)
            auto = form.save(commit=False)
            
            # 3. TUTAJ WKLEJAMY PRZYPISANIE WŁAŚCICIELA
            auto.wlasciciel = request.user 
            
            # 4. Teraz, gdy auto ma już przypisanego właściciela, zapisujemy na stałe
            auto.save()
            
            messages.success(request, "Auto zostało dodane!")
            return redirect('moje_auta')
    else:
        form = SamochodForm()
        
    return render(request, 'dodaj_auto.html', {'form': form})

def anuluj_wynajem(request, wynajem_id):
    # Pobieramy wynajem, ale upewniamy się, że należy do zalogowanego usera
    wynajem = get_object_or_404(Wynajem, id=wynajem_id, uzytkownik=request.user)
    
    # Prosta zasada: nie można anulować czegoś, co już się zaczęło
    if wynajem.data_od <= date.today():
        messages.error(request, "Nie możesz anulować wynajmu, który już trwa lub się zakończył.")
    else:
        wynajem.delete()
        messages.success(request, "Wynajem został anulowany.")
    
    return redirect('moje_wynajmy')


def logout_view(request):
    logout(request)
    return redirect('home')


@login_required
def edytuj_wynajem(request, pk): # <-- teraz pasuje do tego, co wysyła URL
    wynajem = get_object_or_404(Wynajem, id=pk, uzytkownik=request.user)
    
    if wynajem.data_od <= date.today():
        messages.error(request, "Nie możesz edytować wynajmu, który już trwa.")
        return redirect('moje_wynajmy')

    if request.method == 'POST':
        form = WynajemForm(request.POST, instance=wynajem)
        if form.is_valid():
            data_od = form.cleaned_data['data_od']
            data_do = form.cleaned_data['data_do']
            
            czy_zajety = Wynajem.objects.filter(
                samochod=wynajem.samochod,
                data_od__lte=data_do,
                data_do__gte=data_od
            ).exclude(id=wynajem.id).exists()

            if czy_zajety:
                messages.error(request, "Auto jest zajęte w tym terminie.")
                return render(request, 'wynajem_szczegoly.html', {
                    'form': form, 
                    'samochod': wynajem.samochod, # Upewnij się że nazwa to 'samochod' a nie 'auto'
                    'edycja': True
                })

            wynajem.ilosc_dni = (data_do - data_od).days + 1
            wynajem.laczna_cena = wynajem.ilosc_dni * wynajem.samochod.cena_za_dobe
            wynajem.save()
            messages.success(request, "Zaktualizowano termin.")
            return redirect('moje_wynajmy')
    else:
        form = WynajemForm(instance=wynajem)
        
    return render(request, 'wynajem_szczegoly.html', {
        'form': form, 
        'samochod': wynajem.samochod, 
        'edycja': True
    })

@login_required
def edytuj_auto(request, pk):
    # Pobieramy auto tylko jeśli należy do zalogowanego użytkownika
    auto = get_object_or_404(Samochod, id=pk, wlasciciel=request.user)
    
    if request.method == 'POST':
        form = SamochodForm(request.POST, instance=auto)
        if form.is_valid():
            form.save()
            messages.success(request, "Dane samochodu zostały zaktualizowane.")
            return redirect('moje_auta')
    else:
        form = SamochodForm(instance=auto)
    
    return render(request, 'dodaj_auto.html', {'form': form, 'edycja': True})

@login_required
def usun_auto(request, pk):
    auto = get_object_or_404(Samochod, id=pk, wlasciciel=request.user)
    auto.delete()
    messages.success(request, "Samochód został usunięty z oferty.")
    return redirect('moje_auta')