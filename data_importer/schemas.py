# data_importer/schemas.py
from pydantic import BaseModel, Field
from typing import Optional

# Schema para a Região (usado dentro do schema de Estado)
class RegionSchema(BaseModel):
    id: int
    nome: str
    sigla: str

# Schema principal para os dados de um Estado
class StateSchema(BaseModel):
    id: int
    nome: str
    sigla: str
    regiao: RegionSchema

# Schemas aninhados para os dados de um Município
class UFSchema(BaseModel):
    id: int
    sigla: str
    nome: str
    regiao: RegionSchema

class MesorregiaoSchema(BaseModel):
    id: int
    nome: str
    UF: UFSchema

class MicrorregiaoSchema(BaseModel):
    id: int
    nome: str
    mesorregiao: MesorregiaoSchema

# Schema principal para os dados de um Município
class MunicipalitySchema(BaseModel):
    id: int
    nome: str
    microrregiao: MicrorregiaoSchema = Field(alias='microrregiao')

# Schemas para os dados de um Distrito
class MunicipalityRefSchema(BaseModel):
    id: int

# Schema principal para os dados de um Distrito
class DistrictSchema(BaseModel):
    id: int
    nome: str
    municipio: MunicipalityRefSchema