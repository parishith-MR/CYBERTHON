from django.urls import path
from .views import home
from . import views
urlpatterns = [
    path('', home, name='home'),  # Homepage route
    path('analyze_transactions/', views.analyze_transactions, name='analyze_transactions'),
]
