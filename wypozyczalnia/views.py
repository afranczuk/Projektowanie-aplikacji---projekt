from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import RejestracjaForm, WniosekWlascicielForm, WynajemForm
from .models import UserProfil, Samochod, Wynajem, WniosekWlasciciel


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
        # Sprawdzamy, czy użytkownik należy do grupy 'Wlasciciele'
        is_wlasciciel = request.user.groups.filter(name='Wlasciciel').exists()

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
    # Sprawdzamy, czy użytkownik należy do grupy Właściciele
    if not request.user.groups.filter(name='Wlasciciele').exists():
        # jeśli nie jest właścicielem → przekierowujemy go na stronę główną
        return redirect('home')

    # pobieramy tylko auta przypisane do tego użytkownika
    samochody = Samochod.objects.filter(wlasciciel=request.user)
    return render(request, 'moje_auta.html', {'samochody': samochody})




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
            data_od = form.cleaned_data['data_od']
            data_do = form.cleaned_data['data_do']

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

            # oznacz auto jako wynajęte
            auto.wynajety = True
            auto.save()

            return redirect('po_wynajeciu', wynajem_id=wynajem.id)
    else:
        form = WynajemForm()  # <<< TU tworzymy form w GET

    return render(request, 'wynajem_szczegoly.html', {
        'auto': auto,
        'form': form
    })

@login_required
def po_wynajeciu(request, wynajem_id):
    wynajem = get_object_or_404(Wynajem, id=wynajem_id, uzytkownik=request.user)

    return render(request, 'po_wynajeciu.html', {
        'wynajem': wynajem
    })

@login_required
def wniosek_o_wlasciciela(request):
    if request.method == 'POST':
        form = WniosekWlascicielForm(request.POST)
        if form.is_valid():
            wniosek = form.save(commit=False)
            wniosek.uzytkownik = request.user
            wniosek.save()
            messages.success(request, "Twój wniosek został wysłany. Pracownik rozpatrzy go w ciągu max 5 dni roboczych.")
            return redirect('home')
    else:
        form = WniosekWlascicielForm()
    
    return render(request, 'wniosek_o_wlasciciela.html', {'form': form})


@login_required
def moje_wynajmy(request):
    wynajmy = Wynajem.objects.filter(uzytkownik=request.user)
    return render(request, 'moje_wynajmy.html', {'wynajmy': wynajmy})
