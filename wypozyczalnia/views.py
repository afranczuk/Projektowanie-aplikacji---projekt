from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import RejestracjaForm, WniosekWlascicielForm, WynajemForm
from .models import UserProfil, Samochod, Wynajem, WniosekWlasciciel
from datetime import date
from django.db.models import Sum # Dodaj ten import na górze!



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
    if not request.user.groups.filter(name='Wlasciciel').exists() and not request.user.is_superuser:
        return redirect('home')

    # Pobieramy auta właściciela
    samochody = Samochod.objects.filter(wlasciciel=request.user).prefetch_related('wynajem_set')

    # LICZYMY ZAROBKI: Sumujemy laczna_cena ze wszystkich wynajmów aut tego użytkownika
    total_zarobek = Wynajem.objects.filter(samochod__wlasciciel=request.user).aggregate(Sum('laczna_cena'))['laczna_cena__sum'] or 0

    return render(request, 'moje_auta.html', {
        'samochody': samochody,
        'dzisiaj': date.today(),
        'total_zarobek': total_zarobek
    })

# PRZYWRÓCONA FUNKCJA MOJE_WYNAJMY (Punkt 1 z Twojej listy)
@login_required
def moje_wynajmy(request):
    # Pobieramy wynajmy zalogowanego usera wraz z danymi auta i jego właściciela
    wynajmy = Wynajem.objects.filter(uzytkownik=request.user).select_related('samochod__wlasciciel')
    return render(request, 'moje_wynajmy.html', {'wynajmy': wynajmy})

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