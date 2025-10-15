from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
import os
import database, models, schemas, alerts
from apscheduler.schedulers.background import BackgroundScheduler

database.init_db()
app = FastAPI(title="API Qualidade Água - Demo")
SessionLocal = database.SessionLocal

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/praias/", response_model=dict)
def cria_praia(p: schemas.PraiaCreate, db: Session = Depends(get_db)):
    praia = models.Praia(nome=p.nome, latitude=p.latitude, longitude=p.longitude, descricao=p.descricao)
    db.add(praia)
    db.commit()
    db.refresh(praia)
    return {"id": praia.id}

@app.post("/ingest/")
def ingest(leitura: schemas.LeituraCreate, db: Session = Depends(get_db)):
    # validacoes basicas
    praia = db.query(models.Praia).filter(models.Praia.id == leitura.praia_id).first()
    if not praia:
        raise HTTPException(status_code=404, detail="Praia nao encontrada")
    l = models.Leitura(praia_id=leitura.praia_id, parametro=leitura.parametro, valor=leitura.valor, meta=leitura.meta)
    db.add(l)
    db.commit()
    return {"status": "ok"}

@app.get("/praias/")
def lista_praias(db: Session = Depends(get_db)):
    praias = db.query(models.Praia).all()
    return praias

@app.get("/alertas/", response_model=list[schemas.AlertaOut])
def lista_alertas(db: Session = Depends(get_db)):
    alerts = db.query(models.Alerta).order_by(models.Alerta.timestamp.desc()).limit(100).all()
    return alerts

# Scheduler: roda regras a cada N segundos
def job_avaliacao():
    db = SessionLocal()
    try:
        alerts.avalia_leituras_e_gera_alerta(db, models.Praia, models.Leitura, models.Alerta)
    finally:
        db.close()

scheduler = BackgroundScheduler()
scheduler.add_job(job_avaliacao, "interval", seconds=30)  # a cada 30s para demo
scheduler.start()
