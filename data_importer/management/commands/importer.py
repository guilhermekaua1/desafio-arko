import logging
from django.core.management.base import BaseCommand
from django.db import transaction

from data_importer.models import Region, State, Municipality, District
from data_importer.services import IBGEApiClient
from data_importer.schemas import FullDistrictSchema 

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Importa todas as localidades (Regiões, Estados, Municípios e Distritos) usando apenas o endpoint de Distritos.'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.client = IBGEApiClient()
        self.regions_created = set()
        self.states_created = set()
        self.municipalities_created = set()
        self.districts_created = set()

    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('>>> Iniciando importador otimizado...'))
        
        self.stdout.write('Buscando todos os distritos da API do IBGE... (Pode levar um momento)')
        districts_data = self.client.get_districts()
        
        if not districts_data:
            self.stdout.write(self.style.ERROR('Nenhum dado recebido da API. Abortando.'))
            return
            
        try:
            validated_districts = [FullDistrictSchema.model_validate(d) for d in districts_data]
        except Exception as e:
            logger.error(f"Erro de validação Pydantic: {e}")
            self.stdout.write(self.style.ERROR('Os dados recebidos da API não estão no formato esperado. Abortando.'))
            return

        self.stdout.write(f'{len(validated_districts)} distritos encontrados. Processando e salvando no banco de dados...')

        for district_item in validated_districts:
            municipality_item = district_item.municipio

            # ADICIONE ESTA VERIFICAÇÃO DE SEGURANÇA AQUI
            if not municipality_item.microrregiao:
                logger.warning(f"Município '{municipality_item.nome}' (ID: {municipality_item.id}) veio sem microrregião. Pulando distrito '{district_item.nome}'.")
                continue # Pula para o próximo distrito da lista

            microrregiao_item = municipality_item.microrregiao
            mesorregiao_item = microrregiao_item.mesorregiao
            mesorregiao_item = microrregiao_item.mesorregiao
            state_item = mesorregiao_item.UF
            region_item = state_item.regiao

            region, created = Region.objects.get_or_create(
                id=region_item.id,
                defaults={'name': region_item.nome, 'acronym': region_item.sigla}
            )
            if created: self.regions_created.add(region.id)

            state, created = State.objects.get_or_create(
                id=state_item.id,
                defaults={'name': state_item.nome, 'acronym': state_item.sigla, 'region': region}
            )
            if created: self.states_created.add(state.id)

            municipality, created = Municipality.objects.get_or_create(
                id=municipality_item.id,
                defaults={'name': municipality_item.nome, 'state': state}
            )
            if created: self.municipalities_created.add(municipality.id)

            district, created = District.objects.get_or_create(
                id=district_item.id,
                defaults={'name': district_item.nome, 'municipality': municipality}
            )
            if created: self.districts_created.add(district.id)

        self.stdout.write(self.style.SUCCESS('--- Resumo da Importação ---'))
        self.stdout.write(f'{len(self.regions_created)} novas regiões criadas.')
        self.stdout.write(f'{len(self.states_created)} novos estados criados.')
        self.stdout.write(f'{len(self.municipalities_created)} novos municípios criados.')
        self.stdout.write(f'{len(self.districts_created)} novos distritos criados.')
        self.stdout.write(self.style.SUCCESS('>>> Importação otimizada concluída com sucesso!'))