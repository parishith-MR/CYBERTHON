from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('analyze_transactions/', views.analyze_transactions_view, name='analyze_transactions'),
    path('forpdf/', views.forpdf, name='forpdf'),
    path('dust_attack/', views.dust_attack_view, name='dust_attack'),  # New route for dust attack
]
