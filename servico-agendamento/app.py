import os
import logging
import json
import datetime
import requests
from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///agenda.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Configuração de Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s')
logger = logging.getLogger("servico-agendamento")

# URL do Coordenador (muda se estiver no Docker ou local)
# Se estiver rodando localmente sem docker, use 'http://localhost:3000'
COORDINATOR_URL = os.environ.get('COORDINATOR_URL', 'http://localhost:3000')

# --- MODELO ---
class Agendamento(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cientista = db.Column(db.String(50), nullable=False)
    recurso = db.Column(db.String(100), nullable=False) # Ex: Hubble_2025-12-01
    data_horario = db.Column(db.String(50), nullable=False)

with app.app_context():
    db.create_all()

# --- FUNÇÕES AUXILIARES ---
def log_auditoria(event_type, details):
    log_entry = {
        "timestamp_utc": datetime.datetime.utcnow().isoformat(),
        "level": "AUDIT",
        "event_type": event_type,
        "service": "servico-agendamento",
        "details": details
    }
    # Na prática, isso iria para um arquivo separado ou sistema de logs
    logger.info(f"AUDIT_LOG: {json.dumps(log_entry)}")

def adquirir_lock(recurso):
    try:
        logger.info(f"Tentando adquirir lock para {recurso} em {COORDINATOR_URL}")
        resp = requests.post(f"{COORDINATOR_URL}/lock", json={"recurso": recurso}, timeout=2)
        return resp.status_code == 200
    except Exception as e:
        logger.error(f"Erro ao contatar coordenador: {e}")
        return False

def liberar_lock(recurso):
    try:
        requests.post(f"{COORDINATOR_URL}/unlock", json={"recurso": recurso}, timeout=2)
        logger.info(f"Lock liberado para {recurso}")
    except:
        pass

# --- ROTAS ---

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/time', methods=['GET'])
def get_time():
    # Entrega 4: Fonte da verdade do tempo 
    return jsonify({"server_time_utc": datetime.datetime.utcnow().isoformat()})

@app.route('/agendamentos', methods=['GET'])
def listar():
    agendamentos = Agendamento.query.all()
    resultado = []
    for a in agendamentos:
        resultado.append({
            "id": a.id,
            "cientista": a.cientista,
            "recurso": a.recurso,
            "links": [
                {"rel": "self", "href": f"/agendamentos/{a.id}", "method": "GET"},
                {"rel": "delete", "href": f"/agendamentos/{a.id}", "method": "DELETE"}
            ]
        })
    return jsonify(resultado)

@app.route('/agendamentos', methods=['POST'])
def criar():
    data = request.json
    cientista = data.get('cientista')
    recurso = data.get('recurso') 
    horario = data.get('data_horario')

    logger.info(f"Requisição recebida para recurso {recurso}")

    # 1. Tenta pegar o Lock no Node.js
    if not adquirir_lock(recurso):
        logger.warning(f"Falha ao adquirir lock, recurso ocupado: {recurso}")
        return jsonify({"error": "Conflito: Recurso bloqueado"}), 409

    try:
        # 2. Verifica se já existe no banco (Double check)
        existente = Agendamento.query.filter_by(recurso=recurso).first()
        if existente:
            return jsonify({"error": "Já agendado no banco"}), 409

        # 3. Salva
        logger.info("Salvando novo agendamento no BD")
        novo = Agendamento(cientista=cientista, recurso=recurso, data_horario=horario)
        db.session.add(novo)
        db.session.commit()

        log_auditoria("AGENDAMENTO_CRIADO", {"id": novo.id, "recurso": recurso})
        
        return jsonify({"status": "Agendado", "id": novo.id}), 201

    finally:
        # 4. Libera o Lock (Sempre!) [cite: 216]
        liberar_lock(recurso)

@app.route('/agendamentos/<int:id>', methods=['DELETE'])
def deletar(id):
    agendamento = Agendamento.query.get(id)
    if agendamento:
        db.session.delete(agendamento)
        db.session.commit()
        log_auditoria("AGENDAMENTO_CANCELADO", {"id": id})
        return jsonify({"status": "removido"}), 200
    return jsonify({"error": "nao encontrado"}), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)