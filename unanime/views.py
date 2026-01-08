from datetime import date
from calendar import monthrange
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import Demanda, Departamento


@login_required
def home(request):
    hoje = date.today()
    ano = hoje.year
    mes = hoje.month

    primeiro_dia_semana, total_dias_mes = monthrange(ano, mes)

    demandas = Demanda.objects.filter(
        data__year=ano,
        data__month=mes
    ).select_related('responsavel', 'departamento')

    demandas_por_dia = {}
    for demanda in demandas:
        dia = demanda.data.day
        demandas_por_dia.setdefault(dia, []).append(demanda)

    context = {
        'ano': ano,
        'mes': mes,
        'dias_semana': ['Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sáb', 'Dom'],
        'espacos_vazios': range(primeiro_dia_semana),
        'total_dias': range(1, total_dias_mes + 1),
        'demandas_por_dia': demandas_por_dia,
        'usuarios': User.objects.all(),
        'departamentos': Departamento.objects.all(),
    }

    return render(request, 'home.html', context)


@login_required
def criar_demanda(request):
    if request.method == 'POST':
        titulo = request.POST.get('titulo')
        descricao = request.POST.get('descricao')
        data = request.POST.get('data')
        responsavel_id = request.POST.get('responsavel')
        departamento_id = request.POST.get('departamento')

        responsavel = User.objects.get(id=responsavel_id)
        departamento = Departamento.objects.get(id=departamento_id)

        Demanda.objects.create(
            titulo=titulo,
            descricao=descricao,
            data=data,
            responsavel=responsavel,
            departamento=departamento
        )

    return redirect('home')
