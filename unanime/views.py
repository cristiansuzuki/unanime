from datetime import date
from calendar import monthrange
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import JsonResponse
from .models import Demanda, Departamento


@login_required
def home(request):
    hoje = date.today()

    ano = int(request.GET.get('ano', hoje.year))
    mes = int(request.GET.get('mes', hoje.month))

    primeiro_dia_semana, total_dias_mes = monthrange(ano, mes)

    demandas = Demanda.objects.filter(
        data__year=ano,
        data__month=mes
    ).select_related('responsavel', 'departamento')

    demandas_por_dia = {}
    for demanda in demandas:
        dia = demanda.data.day
        demandas_por_dia.setdefault(dia, []).append(demanda)

    mes_anterior = mes - 1 if mes > 1 else 12
    ano_anterior = ano if mes > 1 else ano - 1

    proximo_mes = mes + 1 if mes < 12 else 1
    proximo_ano = ano if mes < 12 else ano + 1

    context = {
        'ano': ano,
        'mes': mes,
        'dias_semana': ['Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sáb', 'Dom'],
        'espacos_vazios': range(primeiro_dia_semana),
        'total_dias': range(1, total_dias_mes + 1),
        'demandas_por_dia': demandas_por_dia,
        'usuarios': User.objects.all(),
        'departamentos': Departamento.objects.all(),
        'status_choices': Demanda.StatusChoices.choices,
        'mes_anterior': mes_anterior,
        'ano_anterior': ano_anterior,
        'proximo_mes': proximo_mes,
        'proximo_ano': proximo_ano,
    }

    return render(request, 'home.html', context)


@login_required
def criar_demanda(request):
    if request.method == 'POST':
        Demanda.objects.create(
            titulo=request.POST['titulo'],
            descricao=request.POST['descricao'],
            data=request.POST['data'],
            status=request.POST['status'],
            responsavel_id=request.POST['responsavel'],
            departamento_id=request.POST['departamento'],
        )
    return redirect('home')


@login_required
def editar_demanda(request, demanda_id):
    demanda = get_object_or_404(Demanda, id=demanda_id)

    if request.method == 'POST':
        demanda.titulo = request.POST['titulo']
        demanda.descricao = request.POST['descricao']
        demanda.status = request.POST['status']
        demanda.responsavel_id = request.POST['responsavel']
        demanda.departamento_id = request.POST['departamento']
        demanda.save()

    return redirect('home')


@login_required
def mover_demanda(request):
    if request.method == 'POST':
        demanda_id = request.POST['demanda_id']
        nova_data = request.POST['nova_data']

        demanda = Demanda.objects.get(id=demanda_id)
        demanda.data = nova_data
        demanda.save()

        return JsonResponse({'status': 'ok'})
