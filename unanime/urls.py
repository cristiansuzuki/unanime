from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('criar-demanda/', views.criar_demanda, name='criar_demanda'),
    path('editar-demanda/<int:demanda_id>/', views.editar_demanda, name='editar_demanda'),
    path('mover-demanda/', views.mover_demanda, name='mover_demanda'),
]
