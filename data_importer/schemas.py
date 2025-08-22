from pydantic import BaseModel, Field
from typing import Optional

class FullRegionSchema(BaseModel):
    id: int
    sigla: str
    nome: str

class FullUFSchema(BaseModel):
    id: int
    sigla: str
    nome: str
    regiao: FullRegionSchema

class FullMesorregiaoSchema(BaseModel):
    id: int
    nome: str
    UF: FullUFSchema

class FullMicrorregiaoSchema(BaseModel):
    id: int
    nome: str
    mesorregiao: FullMesorregiaoSchema

class FullMunicipioSchema(BaseModel):
    id: int
    nome: str
    microrregiao: Optional[FullMicrorregiaoSchema] = None

class FullDistrictSchema(BaseModel):
    id: int
    nome: str
    municipio: FullMunicipioSchema