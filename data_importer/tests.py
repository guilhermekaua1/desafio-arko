# data_importer/tests.py
from django.test import TestCase
from unittest.mock import patch, MagicMock
from requests.exceptions import RequestException

from .services import IBGEApiClient
from .schemas import StateSchema

class IBGEApiClientTests(TestCase):
    #Testes para o IBGEApiClient, focando na logica de requisicao e validacao de dados, sem fazer chamadas de rede reais

    def setUp(self):
        #Configuracao inicial para cada teste.
        self.client = IBGEApiClient()

    @patch('data_importer.services.requests.get')
    def test_get_states_success(self, mock_get):
        #Testa se o cliente processa corretamente uma resposta bem sucedida da API.
        
        #Cria uma resposta JSON de exemplo, como a que a API do IBGE retornaria.
        mock_api_response = [
            {
                "id": 11,
                "sigla": "RO",
                "nome": "Rondônia",
                "regiao": {"id": 1, "sigla": "N", "nome": "Norte"}
            },
            {
                "id": 12,
                "sigla": "AC",
                "nome": "Acre",
                "regiao": {"id": 1, "sigla": "N", "nome": "Norte"}
            }
        ]

        #Configura o  "mock" para simular a API
        #Quando 'requests.get' for chamado, ele retorna esse objeto
        mock_response = MagicMock()
        mock_response.json.return_value = mock_api_response
        mock_response.raise_for_status.return_value = None  #Simula uma resposta HTTP 200 OK
        mock_get.return_value = mock_response

        #Chama o metodo que quer testar
        states = self.client.get_states()

        #Verifica se o resultado é o esperado
        self.assertEqual(len(states), 2)
        self.assertIsInstance(states[0], StateSchema)
        self.assertEqual(states[0].nome, "Rondônia")
        self.assertEqual(states[1].sigla, "AC")
        
        #Verifica se a URL correta foi chamada
        mock_get.assert_called_once_with(
            "https://servicodados.ibge.gov.br/api/v1/localidades/estados?orderBy=nome",
            timeout=20
        )

    @patch('data_importer.services.requests.get')
    def test_get_states_http_error(self, mock_get):

        #Testa como o cliente se comporta quando a API retorna um erro HTTP
        #Configura o mock para simular um erro de rede

        mock_get.side_effect = RequestException("Erro de conexão simulado")

        with self.assertRaises(RequestException):
            self.client.get_states()