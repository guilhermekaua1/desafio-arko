from django.db import models

class Region(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField("Nome", max_length=50)
    acronym = models.CharField("Sigla", max_length=2)

    class Meta:
        verbose_name = "Região"
        verbose_name_plural = "Regiões"
        ordering = ['name']

    def __str__(self):
        return self.name

class State(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField("Nome", max_length=100)
    acronym = models.CharField("Sigla", max_length=2, unique=True)
    region = models.ForeignKey(
        Region,
        on_delete=models.PROTECT,
        related_name='states',
        verbose_name="Região"
    )

    class Meta:
        verbose_name = "Estado"
        verbose_name_plural = "Estados"
        ordering = ['name']

    def __str__(self):
        return f'{self.name} ({self.acronym})'

class Municipality(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField("Nome", max_length=200)
    state = models.ForeignKey(
        State,
        on_delete=models.PROTECT,
        related_name='municipalities',
        verbose_name="Estado"
    )

    class Meta:
        verbose_name = "Município"
        verbose_name_plural = "Municípios"
        ordering = ['name']

    def __str__(self):
        return self.name

class District(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField("Nome", max_length=200)
    municipality = models.ForeignKey(
        Municipality,
        on_delete=models.PROTECT,
        related_name='districts',
        verbose_name="Município"
    )

    class Meta:
        verbose_name = "Distrito"
        verbose_name_plural = "Distritos"
        ordering = ['name']

    def __str__(self):
        return self.name

#models do company 
class Company(models.Model):
    # O CNPJ básico (8 primeiros dígitos) vai ser a chave primaria
    cnpj = models.CharField("CNPJ Básico", max_length=8, primary_key=True)
    razao_social = models.CharField(
        "Razão Social", max_length=255, db_index=True
    )
    natureza_juridica = models.CharField("Natureza Jurídica", max_length=4)
    qualificacao_responsavel = models.CharField(
        "Qualificação do Responsável", max_length=2
    )
    capital_social = models.DecimalField(
        "Capital Social", max_digits=16, decimal_places=2
    )
    porte_empresa = models.CharField(
        "Porte da Empresa", max_length=2, null=True, blank=True
    )
    ente_federativo_responsavel = models.CharField(
        "Ente Federativo Responsável", max_length=255, null=True, blank=True
    )

    class Meta:
        verbose_name = "Empresa"
        verbose_name_plural = "Empresas"
        ordering = ['razao_social']

    def __str__(self):
        return self.razao_social