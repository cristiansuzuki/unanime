from datetime import date
from calendar import monthrange
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST

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

    demandas = Demanda.objects.filter(
        data__year=ano,
        data__month=mes,
        departamento=departamento
    )

    responsavel_id = request.GET.get('responsavel')
    if responsavel_id:
        demandas = demandas.filter(responsavel_id=responsavel_id)

    demandas_por_dia = {}
    for d in demandas:
        demandas_por_dia.setdefault(d.data.day, []).append(d)

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

    Demanda.objects.create(
        titulo=request.POST['titulo'],
        descricao=request.POST.get('descricao', ''),
        data=request.POST['data'],
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

    if not is_admin(user):
        if demanda.status == 'FE':
            return redirect('home')

        if demanda.departamento != user.perfil.departamento:
            return redirect('home')

    novo_status = request.POST.get('status')

    if novo_status == 'PE':
        motivo = request.POST.get('motivo_atraso', '')
        nova_data = request.POST.get('nova_data')

        if nova_data:
            nova_demanda = Demanda.objects.create(
                titulo=demanda.titulo,
                descricao=demanda.descricao,
                data=nova_data,
                status='PE',
                motivo_atraso=motivo,
                nova_data=nova_data,
                departamento=demanda.departamento,
                responsavel=demanda.responsavel,
                demanda_origem=demanda
            )

            demanda.status = 'FE'
            demanda.save()
            return redirect(request.META.get('HTTP_REFERER', 'home'))

    demanda.status = novo_status

    if is_admin(user):
        demanda.titulo = request.POST.get('titulo', demanda.titulo)
        demanda.descricao = request.POST.get('descricao', demanda.descricao)

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
