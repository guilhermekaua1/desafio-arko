# data_importer/tests.py
from django.test import TestCase
import pandas as pd
from decimal import Decimal

# Importa o comando que queremos testar e o modelo
from data_importer.management.commands.populate_companies import Command as PopulateCompaniesCommand
from data_importer.models import Company

class PopulateCompaniesCommandTests(TestCase):
    """
    Testes para o comando populate_companies, focando na lógica de
    processamento de chunks (criação e atualização de dados).
    """

    def setUp(self):
        """Prepara o comando para ser usado nos testes."""
        self.command = PopulateCompaniesCommand()

    def test_process_chunk_creates_new_companies(self):
        """
        Verifica se o process_chunk cria novas empresas quando a base de dados está vazia.
        """
        # 1. PREPARAÇÃO (Arrange)
        # Cria um DataFrame do pandas em memória, simulando um chunk do CSV.
        data = {
            'cnpj': ['11111111', '22222222'],
            'razao_social': ['EMPRESA A LTDA', 'EMPRESA B SA'],
            'natureza_juridica': ['2062', '2054'],
            'qualificacao_responsavel': ['49', '10'],
            'capital_social': ['1000,00', '2500,50'],
            'porte_empresa': ['01', '03'],
            'ente_federativo_responsavel': ['', ''],
        }
        chunk = pd.DataFrame(data)

        # 2. AÇÃO (Act)
        # Chama o método que queremos testar.
        self.command.process_chunk(chunk)

        # 3. VERIFICAÇÃO (Assert)
        # Verifica se as empresas foram criadas corretamente na base de dados.
        self.assertEqual(Company.objects.count(), 2)
        empresa_a = Company.objects.get(cnpj='11111111')
        self.assertEqual(empresa_a.razao_social, 'EMPRESA A LTDA')
        self.assertEqual(empresa_a.capital_social, Decimal('1000.00'))

    def test_process_chunk_updates_existing_companies(self):
        """
        Verifica se o process_chunk atualiza empresas existentes.
        """
        # 1. PREPARAÇÃO (Arrange)
        # Cria uma empresa preexistente na base de dados.
        Company.objects.create(
            cnpj='11111111',
            razao_social='NOME ANTIGO',
            natureza_juridica='0000',
            qualificacao_responsavel='00',
            capital_social=Decimal('1.00'),
            porte_empresa='00'
        )
        # Prepara um chunk com os mesmos CNPJs, mas com dados atualizados.
        data = {
            'cnpj': ['11111111'],
            'razao_social': ['NOME NOVO ATUALIZADO'],
            'natureza_juridica': ['2062',],
            'qualificacao_responsavel': ['49',],
            'capital_social': ['5000,00',],
            'porte_empresa': ['05',],
            'ente_federativo_responsavel': ['GOVERNO FEDERAL',],
        }
        chunk = pd.DataFrame(data)

        # 2. AÇÃO (Act)
        self.command.process_chunk(chunk)

        # 3. VERIFICAÇÃO (Assert)
        # Garante que nenhuma nova empresa foi criada.
        self.assertEqual(Company.objects.count(), 1)
        # Obtém a empresa atualizada e verifica se os campos foram alterados.
        empresa_atualizada = Company.objects.get(cnpj='11111111')
        self.assertEqual(empresa_atualizada.razao_social, 'NOME NOVO ATUALIZADO')
        self.assertEqual(empresa_atualizada.capital_social, Decimal('5000.00'))
        self.assertEqual(empresa_atualizada.porte_empresa, '05')