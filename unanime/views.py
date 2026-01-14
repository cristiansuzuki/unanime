from datetime import date
from calendar import monthrange
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
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

    # ===== DEFINIÇÃO DE DEPARTAMENTO =====
    if is_admin(request.user):
        departamentos = Departamento.objects.all()
        departamento = (
            get_object_or_404(Departamento, id=depto_id)
            if depto_id else departamentos.first()
        )
    else:
        departamentos = None
        departamento = perfil.departamento

    # ===== FUNCIONÁRIOS DO SETOR =====
    funcionarios = Perfil.objects.filter(
        departamento=departamento
    ).select_related('user')

    # ===== CALENDÁRIO =====
    primeiro_dia, total_dias = monthrange(ano, mes)

    demandas = Demanda.objects.filter(
        data__year=ano,
        data__month=mes,
        departamento=departamento
    )

    # ===== FILTRO POR RESPONSÁVEL =====
    responsavel_id = request.GET.get('responsavel')
    if responsavel_id:
        demandas = demandas.filter(responsavel_id=responsavel_id)

    # ===== AGRUPAR POR DIA =====
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
        status=request.POST['status'],
        departamento_id=request.POST['departamento'],
        responsavel_id=request.POST.get('responsavel') or None
    )

    return redirect(request.META.get('HTTP_REFERER', 'home'))


@login_required
@require_POST
def editar_demanda(request, id):
    demanda = get_object_or_404(Demanda, id=id)
    user = request.user

    # ================= ADMIN =================
    if is_admin(user):
        demanda.titulo = request.POST.get('titulo', demanda.titulo)
        demanda.descricao = request.POST.get('descricao', demanda.descricao)

        if 'responsavel' in request.POST:
            demanda.responsavel_id = request.POST.get('responsavel') or None

        if 'status' in request.POST:
            demanda.status = request.POST['status']

        demanda.save()
        return redirect(request.META.get('HTTP_REFERER', 'home'))

    # ================= FUNCIONÁRIO =================
    # precisa ter perfil e ser do mesmo setor
    if not hasattr(user, 'perfil'):
        return redirect('home')

    if demanda.departamento != user.perfil.departamento:
        return redirect('home')

    # funcionário SÓ pode alterar o status
    if 'status' in request.POST:
        demanda.status = request.POST['status']
        demanda.save()

    return redirect(request.META.get('HTTP_REFERER', 'home'))


@login_required
@require_POST
def excluir_demanda(request, id):
    if is_admin(request.user):
        Demanda.objects.filter(id=id).delete()
    return redirect(request.META.get('HTTP_REFERER', 'home'))


@login_required
@require_POST
def mover_demanda(request):
    if not is_admin(request.user):
        return JsonResponse({'error': 'forbidden'}, status=403)

    demanda_id = request.POST.get('demanda_id')
    nova_data = request.POST.get('nova_data')

    if not demanda_id or not nova_data:
        return JsonResponse({'error': 'dados inválidos'}, status=400)

    demanda = get_object_or_404(Demanda, id=demanda_id)
    demanda.data = nova_data
    demanda.save()

    return JsonResponse({'success': True})
