from django.urls import path
from . import views

urlpatterns = [
    path('', views.calendario, name='home'),
    path('setor/<int:depto_id>/', views.calendario, name='calendario_setor'),

    path('demanda/criar/', views.criar_demanda, name='criar_demanda'),
    path('demanda/editar/<int:id>/', views.editar_demanda, name='editar_demanda'),
    path('demanda/excluir/<int:id>/', views.excluir_demanda, name='excluir_demanda'),

    path('demanda/mover/', views.mover_demanda, name='mover_demanda'),  # 👈 ESSA
]
