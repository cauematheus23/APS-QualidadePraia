import os
import uuid
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base

DATABASE_URL_SHARD1 = os.getenv("DATABASE_URL_SHARD1")
DATABASE_URL_SHARD2 = os.getenv("DATABASE_URL_SHARD2")

if not DATABASE_URL_SHARD1 or not DATABASE_URL_SHARD2:
    raise RuntimeError("As URLs dos shards de banco de dados não foram configuradas!")

engine_shard1 = create_engine(DATABASE_URL_SHARD1)
engine_shard2 = create_engine(DATABASE_URL_SHARD2)

SessionLocal_shard1 = sessionmaker(bind=engine_shard1)
SessionLocal_shard2 = sessionmaker(bind=engine_shard2)

engines = {1: engine_shard1, 2: engine_shard2}
sessions = {1: SessionLocal_shard1, 2: SessionLocal_shard2}

# --- MUDANÇA: Nova Lógica de Roteamento baseada em Hash de UUID ---
def get_shard_id_for_praia(praia_id: uuid.UUID) -> int:
    """Decide para qual shard um UUID de praia deve ir usando um hash."""
    if praia_id.int % 2 == 0:
        return 2  # Par
    else:
        return 1  # Ímpar

def get_db_session(shard_id: int):
    SessionLocal = sessions.get(shard_id)
    if not SessionLocal:
        raise ValueError(f"Shard ID inválido: {shard_id}")
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    print("Inicializando tabelas (com UUIDs) no Shard 1...")
    Base.metadata.create_all(bind=engine_shard1)
    print("Inicializando tabelas (com UUIDs) no Shard 2...")
    Base.metadata.create_all(bind=engine_shard2)