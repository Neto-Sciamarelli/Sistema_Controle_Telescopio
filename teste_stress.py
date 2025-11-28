import threading
import requests
import time

URL = "http://localhost:5000/agendamentos"
# Recurso único para gerar conflito
DATA = {
    "cientista": "Dr. Estranho",
    "recurso": "Hubble-DeepField_2025-01-01_00:00",
    "data_horario": "2025-01-01T00:00:00Z"
}

def tentar_agendar(i):
    try:
        print(f"Tentativa {i} enviada...")
        r = requests.post(URL, json=DATA)
        print(f"Tentativa {i}: Status {r.status_code}")
    except Exception as e:
        print(f"Erro {i}: {e}")

threads = []
print("--- Iniciando Teste de Estresse (Race Condition) ---")
# Dispara 10 requisições simultâneas
for i in range(10):
    t = threading.Thread(target=tentar_agendar, args=(i,))
    threads.append(t)
    t.start()

for t in threads:
    t.join()
print("--- Fim do Teste ---")