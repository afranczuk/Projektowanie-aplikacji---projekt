from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views
from wypozyczalnia import views 


urlpatterns = [
    path('admin/', admin.site.urls),
    path('rejestracja/', views.rejestracja, name='rejestracja'),
    path('logowanie/', auth_views.LoginView.as_view(template_name='uzytkownik_logowanie.html'), name='logowanie'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),

    path('', views.strona_glowna, name='home'),
    path('moje_auta/', views.moje_auta, name='moje_auta'),
    path('moje_wynajmy/', views.moje_wynajmy, name='moje_wynajmy'),
    path('wynajem/<int:auto_id>/', views.wynajem_szczegoly, name='wynajem_szczegoly'),
    path('po_wynajeciu/<int:wynajem_id>/', views.po_wynajeciu, name='po_wynajeciu'),
    path('wniosek-wlasciciela/', views.wniosek_o_wlasciciela, name='wniosek_o_wlasciciela'),
    path('dodaj-auto/', views.dodaj_auto, name='dodaj_auto'),
    path('anuluj-wynajem/<int:wynajem_id>/', views.anuluj_wynajem, name='anuluj_wynajem'),
    path('logout/', views.logout_view, name='wylogowanie'),
    path('wynajem/edytuj/<int:pk>/', views.edytuj_wynajem, name='edytuj_wynajem'),
    path('moje-auta/edytuj/<int:pk>/', views.edytuj_auto, name='edytuj_auto'),
    path('moje-auta/usun/<int:pk>/', views.usun_auto, name='usun_auto'),

]