import os
import requests
import zipfile
import logging
import pandas as pd
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.db import transaction
from django.conf import settings
from tqdm import tqdm

from data_importer.models import Company

logger = logging.getLogger(__name__)

# Nomes das colunas baseados no documento de metadados da Receita Federal
COLUMN_NAMES = [
    'cnpj', 'razao_social', 'natureza_juridica', 'qualificacao_responsavel',
    'capital_social', 'porte_empresa', 'ente_federativo_responsavel'
]

class Command(BaseCommand):
    help = 'Baixa, descompacta e popula o banco de dados com dados de empresas da Receita Federal.'

    def add_arguments(self, parser):
        parser.add_argument('url', type=str, help="A URL para o arquivo .zip de empresas.")

    @transaction.atomic
    def handle(self, *args, **options):
        url = options['url']
        # Define o caminho onde os dados serão salvos, dentro da pasta 'data'
        data_dir = os.path.join(settings.BASE_DIR.parent, 'data')
        os.makedirs(data_dir, exist_ok=True) # Garante que a pasta 'data' exista
        zip_file_path = os.path.join(data_dir, 'Empresas.zip')

        self._download_file(url, zip_file_path)
        self._process_zip_file(zip_file_path)

    def _download_file(self, url, path):
        if os.path.exists(path):
            self.stdout.write(self.style.SUCCESS(f'Arquivo {path} já existe. Pulando download.'))
            return
        
        self.stdout.write(self.style.SUCCESS(f'Baixando arquivo de {url}...'))
        try:
            with requests.get(url, stream=True) as r:
                r.raise_for_status()
                total_size = int(r.headers.get('content-length', 0))
                with open(path, 'wb') as f, tqdm(
                    desc=path,
                    total=total_size,
                    unit='iB',
                    unit_scale=True,
                    unit_divisor=1024,
                ) as bar:
                    for chunk in r.iter_content(chunk_size=8192):
                        size = f.write(chunk)
                        bar.update(size)
            self.stdout.write(self.style.SUCCESS('Download concluído.'))
        except requests.RequestException as e:
            self.stderr.write(self.style.ERROR(f'Falha no download: {e}'))
            # Se o download falhar, remove o arquivo parcial
            if os.path.exists(path):
                os.remove(path)
            raise e

    def _process_zip_file(self, zip_file_path):
        self.stdout.write(self.style.SUCCESS(f'Processando arquivo zip: {zip_file_path}'))
        chunk_size = 50000
        total_rows_processed = 0

        with zipfile.ZipFile(zip_file_path) as zf:
            # Encontra o primeiro arquivo CSV dentro do zip
            csv_filename = next((name for name in zf.namelist() if '.csv' in name.lower() or '.emprecsv' in name.lower()), None)
            if not csv_filename:
                raise FileNotFoundError(f'Nenhum arquivo CSV encontrado em {zip_file_path}')

            with zf.open(csv_filename) as csv_file:
                csv_reader = pd.read_csv(
                    csv_file,
                    header=None,
                    names=COLUMN_NAMES,
                    sep=';',
                    encoding='latin-1',
                    dtype=str,
                    chunksize=chunk_size
                )

                self.stdout.write(self.style.WARNING('Iniciando importação para o banco de dados... Este processo pode levar vários minutos.'))
                for i, chunk in enumerate(csv_reader):
                    self.process_chunk(chunk)
                    total_rows_processed += len(chunk)
                    self.stdout.write(f'Processado chunk {i+1}... Total de linhas até agora: {total_rows_processed}')
        
        self.stdout.write(self.style.SUCCESS(f'>>> Importação concluída! Total de {total_rows_processed} linhas processadas.'))

    def process_chunk(self, chunk: pd.DataFrame):
        # Esta função continua exatamente a mesma de antes, com a lógica de bulk_create e bulk_update
        chunk['capital_social'] = chunk['capital_social'].str.replace(',', '.', regex=False)
        chunk['capital_social'] = pd.to_numeric(chunk['capital_social'], errors='coerce').fillna(0)

        objects_to_update = []
        objects_to_create = []

        cnpjs_in_chunk = set(chunk['cnpj'])
        existing_cnpjs = set(Company.objects.filter(cnpj__in=cnpjs_in_chunk).values_list('cnpj', flat=True))

        for _, row in chunk.iterrows():
            company_data = {
                'cnpj': row['cnpj'],
                'razao_social': row['razao_social'],
                'natureza_juridica': row['natureza_juridica'],
                'qualificacao_responsavel': row['qualificacao_responsavel'],
                'capital_social': Decimal(row['capital_social']),
                'porte_empresa': row['porte_empresa'],
                'ente_federativo_responsavel': row['ente_federativo_responsavel'],
            }

            if row['cnpj'] in existing_cnpjs:
                objects_to_update.append(Company(**company_data))
            else:
                objects_to_create.append(Company(**company_data))
        
        if objects_to_create:
            Company.objects.bulk_create(objects_to_create, batch_size=1000)

        if objects_to_update:
            Company.objects.bulk_update(
                objects_to_update,
                ['razao_social', 'natureza_juridica', 'qualificacao_responsavel', 'capital_social', 'porte_empresa', 'ente_federativo_responsavel'],
                batch_size=1000
            )