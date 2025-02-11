from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('analyze_transactions/', views.analyze_transactions_view, name='analyze_transactions'),
    path('about/', views.about, name='about'),
    path('generate-pdf/<str:wallet_address>/', views.generate_pdf_report, name='generate_pdf'),
]