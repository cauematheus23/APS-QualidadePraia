import uuid
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID # Importa o tipo UUID do Postgres
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.sql import func

Base = declarative_base()

class Praia(Base):
    __tablename__ = "praias"
    # --- MUDANÇA: ID agora é UUID ---
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nome = Column(String, unique=False, nullable=False) # unique=True entre shards é complexo, removemos por simplicidade
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    descricao = Column(String, nullable=True)

class Leitura(Base):
    __tablename__ = "leituras"
    id = Column(Integer, primary_key=True) # Leituras podem ter ID sequencial, não tem problema
    # --- MUDANÇA: Foreign Key agora aponta para um UUID ---
    praia_id = Column(UUID(as_uuid=True), ForeignKey("praias.id"))
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    parametro = Column(String)
    valor = Column(Float)
    meta = Column(JSON, nullable=True)
    praia = relationship("Praia")

class Alerta(Base):
    __tablename__ = "alertas"
    id = Column(Integer, primary_key=True) # Alertas também podem ter ID sequencial
    # --- MUDANÇA: Foreign Key agora aponta para um UUID ---
    praia_id = Column(UUID(as_uuid=True), ForeignKey("praias.id"))
    nivel = Column(String)
    mensagem = Column(String)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    notificado = Column(Boolean, default=False)
    praia = relationship("Praia")