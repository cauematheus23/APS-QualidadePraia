import uuid
from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime

class PraiaCreate(BaseModel):
    nome: str
    latitude: float
    longitude: float
    descricao: Optional[str] = None

class LeituraCreate(BaseModel):
    # --- MUDANÇA: praia_id agora é um UUID ---
    praia_id: uuid.UUID
    parametro: str
    valor: float
    meta: Optional[dict] = None

class AlertaOut(BaseModel):
    id: int
    # --- MUDANÇA: praia_id agora é um UUID ---
    praia_id: uuid.UUID
    nivel: str
    mensagem: str
    timestamp: datetime
    model_config = ConfigDict(from_attributes=True)