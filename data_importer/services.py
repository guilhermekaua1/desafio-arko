# data_importer/services.py
import requests
from requests.exceptions import RequestException
from typing import List
import logging

from .schemas import StateSchema, MunicipalitySchema, DistrictSchema

logger = logging.getLogger(__name__)

IBGE_API_URL = "https://servicodados.ibge.gov.br/api/v1/localidades"
DEFAULT_TIMEOUT = 20  #valor alto pra chamadas que tem mts dados

class IBGEApiClient:
    """
    Um cliente para interagir com a API de Localidades do IBGE,
    com validação de dados via Pydantic.
    """

    def _make_request(self, endpoint: str) -> List[dict]:
        """Método base para fazer requisições à API."""
        url = f"{IBGE_API_URL}/{endpoint}"
        try:
            response = requests.get(url, timeout=DEFAULT_TIMEOUT)
            response.raise_for_status()  #lanca excecao para erros HTTP
            return response.json()
        except RequestException as e:
            logger.error(f"Erro na requisição à API para {url}: {e}")
            raise  #manda dnv a excecao pra ser tratada pelo chamador
        except ValueError as e: #erros de parsing do json
            logger.error(f"Erro ao decodificar JSON de {url}: {e}")
            raise

    def get_states(self) -> List[StateSchema]:
        """Busca e valida todos os estados da API."""
        response_data = self._make_request("estados?orderBy=nome")
        try:
            return [StateSchema.model_validate(item) for item in response_data]
        except Exception as e:
            logger.error(f"Erro de validação Pydantic para Estados: {e}")
            return []

    def get_municipalities(self) -> List[MunicipalitySchema]:
        """Busca e valida todos os municípios da API."""
        response_data = self._make_request("municipios?orderBy=nome")
        try:
            return [MunicipalitySchema.model_validate(item) for item in response_data]
        except Exception as e:
            logger.error(f"Erro de validação Pydantic para Municípios: {e}")
            return []

    def get_districts(self) -> List[DistrictSchema]:
        """Busca e valida todos os distritos da API."""
        response_data = self._make_request("distritos?orderBy=nome")
        try:
            return [DistrictSchema.model_validate(item) for item in response_data]
        except Exception as e:
            logger.error(f"Erro de validação Pydantic para Distritos: {e}")
            return []