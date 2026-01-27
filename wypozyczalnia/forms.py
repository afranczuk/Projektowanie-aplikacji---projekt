from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import UserProfil, Wynajem, WniosekWlasciciel


class RejestracjaForm(UserCreationForm):
    posiada_prawo_jazdy = forms.BooleanField(
        required=True, 
        label="Czy posiadasz prawo jazdy?"
    )
    numer_telefonu = forms.CharField(
        max_length=12, 
        initial="+48", 
        label="Numer telefonu"
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ('posiada_prawo_jazdy', 'numer_telefonu')



class WynajemForm(forms.ModelForm):
    akceptuje_regulamin = forms.BooleanField(
        required=True,
        label="Akceptuję regulamin"
    )

    class Meta:
        model = Wynajem
        fields = ['data_od', 'data_do']
        widgets = {
            'data_od': forms.DateInput(attrs={'type': 'date'}),
            'data_do': forms.DateInput(attrs={'type': 'date'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        data_od = cleaned_data.get('data_od')
        data_do = cleaned_data.get('data_do')

        if data_od and data_do and data_do < data_od:
            raise forms.ValidationError(
                "Data zakończenia nie może być wcześniejsza niż data rozpoczęcia."
            )

        return cleaned_data


class WniosekWlascicielForm(forms.ModelForm):
    class Meta:
        model = WniosekWlasciciel
        fields = ['imie', 'nazwisko', 'dodatkowe_info']
        widgets = {
            'dodatkowe_info': forms.Textarea(attrs={'rows': 3}),
        }
        labels = {
            'imie': "Imię",
            'nazwisko': "Nazwisko",
            'dodatkowe_info': "Dodatkowe informacje (opcjonalnie)",
        }
