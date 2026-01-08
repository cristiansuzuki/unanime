from django.db import models
from django.contrib.auth.models import User

class Departamento(models.Model):
    nome = models.CharField(max_length=100)

    def __str__(self):
        return self.nome


class Demanda(models.Model):

    class StatusChoices(models.TextChoices):
        ABERTO = 'AB', 'Aberto'
        CONCLUIDO = 'CO', 'Concluído'
        PENDENTE = 'PE', 'Pendente'

    titulo = models.CharField(max_length=200)
    responsavel = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='demandas'
    )
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
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.titulo} - {self.get_status_display()}"
