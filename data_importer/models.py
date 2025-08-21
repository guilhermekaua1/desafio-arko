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