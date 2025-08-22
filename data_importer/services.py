#teste pro importer.py
import time
import requests
from requests.exceptions import RequestException
from typing import List
import logging
import os

logger = logging.getLogger(__name__)

IBGE_API_URL = "https://servicodados.ibge.gov.br/api/v1/localidades"
DEFAULT_TIMEOUT = 60

class IBGEApiClient:

    def _make_request(self, endpoint: str) -> List[dict]:
        url = f"{IBGE_API_URL}/{endpoint}"
        try:
            response = requests.get(url, timeout=DEFAULT_TIMEOUT)
            response.raise_for_status()  
            time.sleep(3)
            return response.json()
        except RequestException as e:
            logger.error(f"Erro na requisição à API para {url}: {e}")
            raise
        except ValueError as e:
            logger.error(f"Erro ao decodificar JSON de {url}: {e}")
            raise

    def get_districts(self) -> List[dict]:
        return self._make_request("distritos?orderBy=nome")