from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views
from wypozyczalnia import views 

#urlpatterns = [
    # 1. Panel Admina
   # path('admin/', admin.site.urls),

    # 2. Twoja rejestracja (używamy funkcji z pliku views.py w wypozyczalnia)
    #path('rejestracja/', views.rejestracja, name='rejestracja'),

    # 3. Logowanie (używamy gotowca z Django)
    #path('logowanie/', auth_views.LoginView.as_view(template_name='uzytkownik_logowanie.html'), name='logowanie'),

   # path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    
    #path('', views.strona_glowna, name='home'), 

    #path('moje_auta/', views.moje_auta, name='moje_auta'),

#    path('moje_wynajmy/', views.moje_wynajmy, name='moje_wynajmy'),
#]

urlpatterns = [
    path('admin/', admin.site.urls),
    path('rejestracja/', views.rejestracja, name='rejestracja'),
    path('logowanie/', auth_views.LoginView.as_view(template_name='uzytkownik_logowanie.html'), name='logowanie'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),

    path('', views.strona_glowna, name='home'),
    path('moje_auta/', views.moje_auta, name='moje_auta'),
    path('moje_wynajmy/', views.moje_wynajmy, name='moje_wynajmy'),
    path('wynajmij/<int:auto_id>/', views.wynajmij_samochod, name='wynajmij_samochod'),
    path('wynajem/<int:auto_id>/', views.wynajem_szczegoly, name='wynajem_szczegoly'),
    path('po_wynajeciu/<int:wynajem_id>/', views.po_wynajeciu, name='po_wynajeciu'),
    path('wniosek-wlasciciela/', views.wniosek_o_wlasciciela, name='wniosek_o_wlasciciela'),



]
