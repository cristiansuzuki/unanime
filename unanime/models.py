from django.db import models
from django.contrib.auth.models import User


class Departamento(models.Model):
    nome = models.CharField(max_length=50)

    def __str__(self):
        return self.nome


class Perfil(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    departamento = models.ForeignKey(
        Departamento,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    def __str__(self):
        return self.user.username


class Demanda(models.Model):

    class StatusChoices(models.TextChoices):
        ABERTO = 'AB', 'Aberto'
        CONCLUIDO = 'CO', 'Concluído'
        PENDENTE = 'PE', 'Pendente'

    titulo = models.CharField(max_length=200)
    descricao = models.TextField(blank=True)
    data = models.DateField()

    status = models.CharField(
        max_length=2,
        choices=StatusChoices.choices,
        default=StatusChoices.ABERTO
    )

    departamento = models.ForeignKey(
        Departamento,
        on_delete=models.CASCADE,
        related_name='demandas'
    )

    # 🔹 RESPONSÁVEL PELA DEMANDA (FUNCIONÁRIO)
    responsavel = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='demandas_responsavel'
    )

    criado_em = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.titulo
