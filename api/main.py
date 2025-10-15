import uuid
from fastapi import FastAPI, HTTPException
from sqlalchemy.orm import Session
from apscheduler.schedulers.background import BackgroundScheduler
import database, models, schemas, alerts

database.init_db()
app = FastAPI(title="API Qualidade Água - UUID Sharded Demo")

# --- MUDANÇA RADICAL: Lógica de Criação de Praia com UUID ---
@app.post("/praias/", response_model=dict)
def cria_praia(p: schemas.PraiaCreate):
    # 1. Aplicação gera um ID universalmente único
    novo_id = uuid.uuid4()
    
    # 2. Determina o shard a partir do novo ID
    shard_id = database.get_shard_id_for_praia(novo_id)
    
    # 3. Obtém a sessão do shard correto
    db_gen = database.get_db_session(shard_id)
    db = next(db_gen)
    try:
        # 4. Cria o objeto Praia com o ID pré-definido
        praia = models.Praia(
            id=novo_id, 
            nome=p.nome, 
            latitude=p.latitude, 
            longitude=p.longitude, 
            descricao=p.descricao
        )
        db.add(praia)
        db.commit()
        db.refresh(praia)
        return {"id": praia.id, "nome": praia.nome, "shard_id": shard_id}
    finally:
        next(db_gen, None)

@app.post("/ingest/")
def ingest(leitura: schemas.LeituraCreate):
    # Agora a leitura.praia_id é um UUID, e a função de roteamento funciona corretamente
    shard_id = database.get_shard_id_for_praia(leitura.praia_id)
    db_gen = database.get_db_session(shard_id)
    db = next(db_gen)
    try:
        # O resto da lógica funciona como antes
        praia = db.query(models.Praia).filter(models.Praia.id == leitura.praia_id).first()
        if not praia:
            raise HTTPException(status_code=404, detail=f"Praia ID {leitura.praia_id} não encontrada no shard {shard_id}")
        
        l = models.Leitura(praia_id=leitura.praia_id, parametro=leitura.parametro, valor=leitura.valor, meta=leitura.meta)
        db.add(l)
        db.commit()
        return {"status": "ok", "shard_id": shard_id}
    finally:
        next(db_gen, None)

# O resto dos endpoints (/praias, /alertas) e o job_avaliacao permanecem os mesmos

@app.get("/praias/")
def lista_praias():
    todas_as_praias = []
    for shard_id in database.sessions.keys():
        db_gen = database.get_db_session(shard_id)
        db = next(db_gen)
        try:
            praias_no_shard = db.query(models.Praia).all()
            
            # --- MUDANÇA SIMPLES AQUI ---
            # Para cada praia encontrada, criamos um dicionário e adicionamos o shard_id
            for praia in praias_no_shard:
                praia_com_shard = {
                    "id": praia.id,
                    "nome": praia.nome,
                    "latitude": praia.latitude,
                    "longitude": praia.longitude,
                    "descricao": praia.descricao,
                    "shard_id": shard_id  # <-- Adicionando a informação do shard!
                }
                todas_as_praias.append(praia_com_shard)
        finally:
            next(db_gen, None)
            
    return todas_as_praias

@app.get("/alertas/", response_model=list[schemas.AlertaOut])
def lista_alertas():
    todos_os_alertas = []
    for shard_id in database.sessions.keys():
        db_gen = database.get_db_session(shard_id)
        db = next(db_gen)
        try:
            alertas_no_shard = db.query(models.Alerta).order_by(models.Alerta.timestamp.desc()).limit(50).all()
            todos_os_alertas.extend(alertas_no_shard)
        finally:
            next(db_gen, None)
    
    todos_os_alertas.sort(key=lambda a: a.timestamp, reverse=True)
    return todos_os_alertas[:100]

def job_avaliacao():
    print("Iniciando job de avaliação de alertas em todos os shards...")
    for shard_id in database.sessions.keys():
        db_gen = database.get_db_session(shard_id)
        db = next(db_gen)
        try:
            alerts.avalia_leituras_e_gera_alerta(db, models.Praia, models.Leitura, models.Alerta)
        finally:
            next(db_gen, None)
    print("Job de avaliação concluído.")

scheduler = BackgroundScheduler()
scheduler.add_job(job_avaliacao, "interval", seconds=30)
scheduler.start()