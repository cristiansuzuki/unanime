from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('criar-demanda/', views.criar_demanda, name='criar_demanda'),
]
