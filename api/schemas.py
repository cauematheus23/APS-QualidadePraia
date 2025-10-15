from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import datetime

class PraiaCreate(BaseModel):
    nome: str
    latitude: float
    longitude: float
    descricao: Optional[str] = None

class LeituraCreate(BaseModel):
    praia_id: int
    parametro: str
    valor: float
    meta: Optional[dict] = None

class AlertaOut(BaseModel):
    id: int
    praia_id: int
    nivel: str
    mensagem: str
    timestamp: datetime

    model_config = ConfigDict(from_attributes=True)
        