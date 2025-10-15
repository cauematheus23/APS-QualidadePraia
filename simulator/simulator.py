import os
import time
import random
import requests

API_URL = os.getenv("API_URL", "http://localhost:8000")

def wait_for_api():
    """Espera a API ficar disponível antes de continuar."""
    print("Aguardando a API ficar disponível...")
    start_time = time.time()
    while time.time() - start_time < 30: # Tenta por até 30 segundos
        try:
            response = requests.get(f"{API_URL}/docs")
            if response.status_code == 200:
                print("API está pronta!")
                return True
        except requests.exceptions.ConnectionError:
            pass # Ignora o erro e tenta de novo
        time.sleep(2) # Espera 2 segundos antes da próxima tentativa
    print("Erro: A API não ficou disponível a tempo.")
    return False

# --- LISTA DE PRAIAS CORRIGIDA ---
initial_praias = [
    {"nome": "Copacabana", "cidade": "Rio de Janeiro", "latitude": -22.9719, "longitude": -43.1828},
    {"nome": "Gonzaga", "cidade": "Santos", "latitude": -23.9752, "longitude": -46.3283},
    {"nome": "Jurerê Internacional", "cidade": "Florianópolis", "latitude": -27.4379, "longitude": -48.4947},
    {"nome": "Boa Viagem", "cidade": "Recife", "latitude": -8.1334, "longitude": -34.9019},
]

def ensure_praias():
    """Garante que as praias existam na API, usando o nome como identificador único."""
    try:
        r = requests.get(f"{API_URL}/praias/")
        r.raise_for_status()
        praias_existentes = {p['nome'] for p in r.json()}
        
        praias_a_criar = [p for p in initial_praias if p['nome'] not in praias_existentes]

        if not praias_a_criar:
            print("Praias de demonstração já existem.")
            return

        print(f"Criando {len(praias_a_criar)} novas praias de demonstração...")
        for p in praias_a_criar:
            payload = {
                "nome": p['nome'],
                "latitude": p['latitude'],
                "longitude": p['longitude'],
                "descricao": f"Praia localizada em {p['cidade']}"
            }
            requests.post(f"{API_URL}/praias/", json=payload)

    except requests.exceptions.RequestException as e:
        print(f"Erro ao garantir a criação das praias: {e}")


def envia_leitura(praia_id, parametro, valor):
    payload = {"praia_id": praia_id, "parametro": parametro, "valor": valor}
    try:
        requests.post(f"{API_URL}/ingest/", json=payload, timeout=2)
        print(f"Enviada leitura para praia ID {praia_id}: {parametro} = {valor}")
    except Exception as e:
        print("Erro no envio da leitura:", e)

def main_loop():
    ensure_praias()
    
    try:
        r = requests.get(f"{API_URL}/praias/")
        r.raise_for_status()
        praias = r.json()
    except requests.exceptions.RequestException as e:
        print(f"Não foi possível buscar a lista de praias da API: {e}")
        return

    while True:
        for p in praias:
            praia_id = p["id"]
            
            faixas_valores = [(0, 35), (36, 104), (105, 200)]
            pesos = [0.80, 0.15, 0.05]
            
            faixa_sorteada = random.choices(faixas_valores, weights=pesos, k=1)[0]
            
            enterococos = random.randint(faixa_sorteada[0], faixa_sorteada[1])
            temperatura = random.uniform(18, 30)
            
            envia_leitura(praia_id, "enterococos", float(enterococos))
            envia_leitura(praia_id, "temperatura_agua", round(temperatura, 1))
            
        time.sleep(10)

if __name__ == "__main__":
    if wait_for_api():
        main_loop()