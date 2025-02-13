from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('analyze_transactions/', views.analyze_transactions_view, name='analyze_transactions'),
    path('forpdf/', views.forpdf, name='forpdf'),
    path('about/', views.about, name='about'),
]