from django.urls import path
from . import views  # ✅ Import views module
from .views import dust_attack, track_transaction ,log_ip # ✅ Explicitly import missing functions

urlpatterns = [
    path('', views.home, name='home'),
    path('analyze_transactions/', views.analyze_transactions_view, name='analyze_transactions'),
    path('about/', views.about, name='about'),
    path('log/', log_ip, name='log_ip'),
    path("api/dust_attack/", dust_attack, name="dust_attack"),  # ✅ Now defined
    path('tx/<str:tx_hash>/', track_transaction, name='track_transaction'),  # ✅ Now defined
    #path('generate-pdf/<str:wallet_address>/', views.generate_pdf_report, name='generate_pdf'),
]
