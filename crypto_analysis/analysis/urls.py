from django.urls import path
from .views import home
from . import views

urlpatterns = [
    path('', home, name='home'),  # Homepage route
    path('analyze_transactions/', views.analyze_transactions_view, name='analyze_transactions'),
    path('analyze_node/', views.analyze_node, name='analyze_node'),
]