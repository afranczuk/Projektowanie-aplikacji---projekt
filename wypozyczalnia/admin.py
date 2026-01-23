from django.contrib import admin
from .models import Samochod, Kategoria

class SamochodAdmin(admin.ModelAdmin):
    list_display = ['marka', 'model', 'kategoria', 'data_dodania']
    list_filter = ['kategoria', 'data_dodania']
    search_fields = ['marka', 'model']

admin.site.register(Samochod, SamochodAdmin)
admin.site.register(Kategoria)
