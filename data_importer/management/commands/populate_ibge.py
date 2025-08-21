# data_importer/management/commands/populate_ibge.py
import logging
from django.core.management.base import BaseCommand
from django.db import transaction

from data_importer.models import Region, State, Municipality, District
from data_importer.services import IBGEApiClient

#Configura um logger para o comando
logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Busca dados de localidades da API do IBGE e popula o banco de dados.'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.client = IBGEApiClient()
        self.created_regions = 0
        self.created_states = 0
        self.created_municipalities = 0
        self.created_districts = 0

    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('>>> Iniciando importação de dados do IBGE...'))

        try:
            self._import_regions_and_states()
            self._import_municipalities()
            self._import_districts()
        except Exception as e:
            logger.error(f"Ocorreu um erro crítico durante a importação: {e}")
            self.stdout.write(self.style.ERROR('A importação falhou. Verifique os logs para mais detalhes.'))
            return

        self.stdout.write(self.style.SUCCESS('--- Resumo da Importação ---'))
        self.stdout.write(f'{self.created_regions} novas regiões criadas.')
        self.stdout.write(f'{self.created_states} novos estados criados.')
        self.stdout.write(f'{self.created_municipalities} novos municípios criados.')
        self.stdout.write(f'{self.created_districts} novos distritos criados.')
        self.stdout.write(self.style.SUCCESS('>>> Importação concluída com sucesso!'))

    def _import_regions_and_states(self):
        self.stdout.write('Importando regiões e estados...')
        states_data = self.client.get_states()

        for state_item in states_data:
            region_data = state_item.regiao
            
            #get_or_create das regioes
            region, created = Region.objects.get_or_create(
                id=region_data.id,
                defaults={'name': region_data.nome, 'acronym': region_data.sigla}
            )
            if created:
                self.created_regions += 1

            #get_or_create dos estados
            _, created = State.objects.get_or_create(
                id=state_item.id,
                defaults={
                    'name': state_item.nome,
                    'acronym': state_item.sigla,
                    'region': region
                }
            )
            if created:
                self.created_states += 1

    def _import_municipalities(self):
        self.stdout.write('Importando municípios... (Pode levar um momento)')
        municipalities_data = self.client.get_municipalities()
        
        #Carregar todos os estados existentes em um mapa para evitar queries no loop
        states_map = {s.id: s for s in State.objects.all()}
        
        municipalities_to_create = []
        for mun_item in municipalities_data:
            state_id = mun_item.microrregiao.mesorregiao.UF.id
            state_instance = states_map.get(state_id)
            
            if not state_instance:
                logger.warning(f"Estado com ID {state_id} não encontrado para o município {mun_item.nome}. Pulando.")
                continue

            municipalities_to_create.append(
                Municipality(id=mun_item.id, name=mun_item.nome, state=state_instance)
            )
        
        if municipalities_to_create:
            created_objs = Municipality.objects.bulk_create(municipalities_to_create, ignore_conflicts=True)
            self.created_municipalities = len(created_objs)

    def _import_districts(self):
        self.stdout.write('Importando distritos... (Pode levar um momento)')
        districts_data = self.client.get_districts()

        municipalities_map = {m.id: m for m in Municipality.objects.all()}

        districts_to_create = []
        for dist_item in districts_data:
            municipality_id = dist_item.municipio.id
            municipality_instance = municipalities_map.get(municipality_id)

            if not municipality_instance:
                logger.warning(f"Município com ID {municipality_id} não encontrado para o distrito {dist_item.nome}. Pulando.")
                continue

            districts_to_create.append(
                District(id=dist_item.id, name=dist_item.nome, municipality=municipality_instance)
            )

        if districts_to_create:
            created_objs = District.objects.bulk_create(districts_to_create, ignore_conflicts=True)
            self.created_districts = len(created_objs)