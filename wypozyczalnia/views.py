from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import RejestracjaForm
from .models import UserProfil, Samochod, Wynajem
from .forms import WynajemForm


def rejestracja(request):
    if request.method == 'POST':
        form = RejestracjaForm(request.POST)
        if form.is_valid():
            # 1. Zapisujemy podstawowe dane użytkownika
            user = form.save()
            
            # 2. Tworzymy dla niego UserProfil z Twoimi polami
            UserProfil.objects.create(
                user=user,
                posiada_prawo_jazdy=form.cleaned_data.get('posiada_prawo_jazdy'),
                numer_telefonu=form.cleaned_data.get('numer_telefonu')
            )
            return redirect('logowanie') # Po rejestracji wyślij go do logowania
    else:
        form = RejestracjaForm()
    
    return render(request, 'uzytkownik_rejestracja.html', {'form': form})


def strona_glowna(request):
    samochody = Samochod.objects.all()

    is_wlasciciel = False
    if request.user.is_authenticated:
        is_wlasciciel = request.user.groups.filter(name='Wlasciciele').exists()

    return render(
        request,
        'strona_glowna.html',
        {
            'samochody': samochody,
            'is_wlasciciel': is_wlasciciel,
        }
    )
#def lista_samochodow(request):
   # samochody = Samochod.objects.select_related('kategoria', 'wlasciciel')
    #return render(request, 'lista_samochodow.html', {'samochody': samochody})


@login_required
def moje_auta(request):
    # tylko auta właściciela
    samochody = Samochod.objects.filter(wlasciciel=request.user)
    return render(request, 'moje_auta.html', {'samochody': samochody})



@login_required
def moje_wynajmy(request):
    wynajmy = Wynajem.objects.filter(uzytkownik=request.user)
    return render(request, 'moje_wynajmy.html', {'wynajmy': wynajmy})


@login_required
def wynajmij_samochod(request, auto_id):
    auto = get_object_or_404(Samochod, id=auto_id)

    Wynajem.objects.create(
        uzytkownik=request.user,
        samochod=auto
    )

    return redirect('/')

@login_required
def wynajem_szczegoly(request, auto_id):
    auto = get_object_or_404(Samochod, id=auto_id)

    if request.method == 'POST':
        form = WynajemForm(request.POST)
        if form.is_valid():
            wynajem = form.save(commit=False)
            wynajem.user = request.user
            wynajem.samochod = auto
            wynajem.save()
            auto.delete()
            # wysłanie powiadomienia właścicielowi (można później wysłać maila)
            messages.success(request, f"Twoje auto {auto.marka} {auto.model} zostało wynajęte!")

            return redirect('po_wynajeciu')
    else:
        form = WynajemForm()

    return render(request, 'wynajem_szczegoly.html', {'auto': auto, 'form': form})

@login_required
def wynajem_szczegoly(request, auto_id):
    auto = get_object_or_404(Samochod, id=auto_id)

    if request.method == 'POST':
        form = WynajemForm(request.POST)
        if form.is_valid():
            wynajem = form.save(commit=False)
            wynajem.uzytkownik = request.user
            wynajem.samochod = auto
            wynajem.laczna_cena = wynajem.ilosc_dni * auto.cena_za_dobe
            wynajem.save()

            # powiadomienie właściciela (można wysłać maila)
            messages.success(request, f"Twoje auto {auto.marka} {auto.model} zostało wynajęte! Właściciel otrzyma powiadomienie.")

            # usuwamy auto z dostępnych (opcjonalnie, jeśli nie chcesz go całkiem usuwać, możesz dodać status)
            auto.delete()

            return redirect('po_wynajeciu')
    else:
        form = WynajemForm()

    return render(request, 'wynajem_szczegoly.html', {'auto': auto, 'form': form})



@login_required
def po_wynajeciu(request):
    return render(request, 'po_wynajeciu.html')