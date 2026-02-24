from datetime import date, timedelta
from calendar import monthrange
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.db.models import Q

from .models import Demanda, Departamento, Perfil


def is_admin(user):
    return user.groups.filter(name='Administrador').exists()


@login_required
def calendario(request, depto_id=None):
    hoje = date.today()
    ano = hoje.year
    mes = hoje.month

    perfil = get_object_or_404(Perfil, user=request.user)

    if is_admin(request.user):
        departamentos = Departamento.objects.all()
        departamento = (
            get_object_or_404(Departamento, id=depto_id)
            if depto_id else departamentos.first()
        )
    else:
        departamentos = None
        departamento = perfil.departamento

    funcionarios = Perfil.objects.filter(
        departamento=departamento
    ).select_related('user')

    primeiro_dia, total_dias = monthrange(ano, mes)

    inicio_mes = date(ano, mes, 1)
    fim_mes = date(ano, mes, total_dias)

    demandas = Demanda.objects.filter(
        departamento=departamento,
        data__lte=fim_mes
    ).filter(
        Q(data_fim__gte=inicio_mes) |
        Q(data_fim__isnull=True)
    )

    responsavel_id = request.GET.get('responsavel')
    if responsavel_id:
        demandas = demandas.filter(responsavel_id=responsavel_id)

    demandas_por_dia = {}

    for d in demandas:
        data_inicio = d.data
        data_fim = d.data_fim or d.data

        atual = data_inicio
        while atual <= data_fim:
            if atual.month == mes:
                demandas_por_dia.setdefault(atual.day, []).append(d)
            atual += timedelta(days=1)

    return render(request, 'calendario.html', {
        'ano': ano,
        'mes': mes,
        'departamento': departamento,
        'departamentos': departamentos,
        'funcionarios': funcionarios,
        'demandas_por_dia': demandas_por_dia,
        'dias_mes': range(1, total_dias + 1),
        'espacos_vazios': range(primeiro_dia),
        'is_admin': is_admin(request.user),
        'hoje': hoje
    })


@login_required
@require_POST
def criar_demanda(request):
    if not is_admin(request.user):
        return redirect('home')

    data_inicio = request.POST['data']
    data_fim = request.POST.get('data_fim') or data_inicio

    Demanda.objects.create(
        titulo=request.POST['titulo'],
        descricao=request.POST.get('descricao', ''),
        data=data_inicio,
        data_fim=data_fim,
        status=request.POST.get('status', 'AB'),
        departamento_id=request.POST['departamento'],
        responsavel_id=request.POST.get('responsavel') or None
    )

    return redirect(request.META.get('HTTP_REFERER', 'home'))


@login_required
@require_POST
def editar_demanda(request, id):
    demanda = get_object_or_404(Demanda, id=id)
    user = request.user
    hoje = date.today()
    novo_status = request.POST.get('status')

    # =========================
    # FUNCIONÁRIO
    # =========================
    if not is_admin(user):

        if demanda.status == 'FE':
            return redirect('home')

        if demanda.departamento != user.perfil.departamento:
            return redirect('home')

        # 🔥 REGRA DE PENDENTE RESTAURADA
        if novo_status == 'PE':

            nova_data = request.POST.get('nova_data')
            motivo = request.POST.get('motivo_atraso', '')

            if not nova_data:
                return redirect(request.META.get('HTTP_REFERER', 'home'))

            nova_data_date = date.fromisoformat(nova_data)

            # não pode ser hoje ou passado
            if nova_data_date < hoje:
                return redirect(request.META.get('HTTP_REFERER', 'home'))

            # cria nova demanda
            Demanda.objects.create(
                titulo=demanda.titulo,
                descricao=demanda.descricao,
                data=nova_data_date,
                data_fim=nova_data_date,
                status='PE',
                motivo_atraso=motivo,
                nova_data=nova_data_date,
                departamento=demanda.departamento,
                responsavel=demanda.responsavel,
                demanda_origem=demanda
            )

            demanda.status = 'FE'
            demanda.save()

            return redirect(request.META.get('HTTP_REFERER', 'home'))

        # 🔒 Só pode concluir
        if novo_status == 'CO':
            demanda.status = 'CO'
            demanda.save()
            return redirect(request.META.get('HTTP_REFERER', 'home'))

        return redirect('home')

    # =========================
    # ADMIN
    # =========================
    demanda.status = novo_status
    demanda.titulo = request.POST.get('titulo', demanda.titulo)
    demanda.descricao = request.POST.get('descricao', demanda.descricao)
    demanda.data_fim = request.POST.get('data_fim') or demanda.data

    if 'responsavel' in request.POST:
        demanda.responsavel_id = request.POST.get('responsavel') or None

    demanda.save()
    return redirect(request.META.get('HTTP_REFERER', 'home'))


@login_required
@require_POST
def excluir_demanda(request, id):
    if is_admin(request.user):
        Demanda.objects.filter(id=id).delete()
    return redirect(request.META.get('HTTP_REFERER', 'home'))