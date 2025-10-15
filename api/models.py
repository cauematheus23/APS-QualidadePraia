from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

Base = declarative_base()

class Praia(Base):
    __tablename__ = "praias"
    id = Column(Integer, primary_key=True)
    nome = Column(String, unique=True, nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    descricao = Column(String, nullable=True)

class Leitura(Base):
    __tablename__ = "leituras"
    id = Column(Integer, primary_key=True)
    praia_id = Column(Integer, ForeignKey("praias.id"))
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    parametro = Column(String)  # ex: "enterococos", "temperatura_agua"
    valor = Column(Float)
    meta = Column(JSON, nullable=True)
    praia = relationship("Praia")

class Alerta(Base):
    __tablename__ = "alertas"
    id = Column(Integer, primary_key=True)
    praia_id = Column(Integer, ForeignKey("praias.id"))
    nivel = Column(String)  # verde/amarelo/vermelho
    mensagem = Column(String)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    notificado = Column(Boolean, default=False)
    praia = relationship("Praia")
