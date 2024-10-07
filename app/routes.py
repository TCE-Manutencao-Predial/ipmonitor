from flask import Flask, render_template, jsonify, make_response, request
from app import ip_operations
import time
import threading
from app import app

check_ip = []
background_thread = None
stop_event = threading.Event()
cache_lock = threading.Lock()  # PH: Garantir thread safety ao acessar check_ip

RAIZ = '/ipmonitor'

# Função para atualizar o cache em segundo plano
def background_ip_check(vlan):
    global check_ip
    rede_base = '172.17.' + vlan + '.'

    while not stop_event.is_set():
        data = ip_operations.verificar_ips(rede_base)  # PH: Obtém os dados atualizados
        with cache_lock:  # PH: Bloqueia o cache para atualização segura
            check_ip = data  # PH: Atualiza o cache
        time.sleep(30)  # PH: Espera 30 segundos antes da próxima atualização

'''API ENDPOINTS'''

@app.route('/')  # Para rodar localmente
@app.route(RAIZ + '/')
def index():
    return render_template('index.html')

@app.route('/api/ip-status')  # Para rodar localmente
@app.route(RAIZ + '/api/ip-status')
def ip_status():
    with cache_lock:  # PH: Bloqueia o cache para leitura segura
        data = check_ip.copy()  # PH: Faz uma cópia dos dados do cache
    return jsonify(data)

@app.route('/api/start-check/<string:vlan>', methods=['GET'])  # Para rodar localmente
@app.route(RAIZ + '/api/start-check/<string:vlan>', methods=['GET'])
def check(vlan):
    global background_thread, stop_event, check_ip

    check_ip = []

    # Encerra a thread anterior se estiver rodando
    if background_thread and background_thread.is_alive():
        stop_event.set()
        background_thread.join()

    # Reinicia o evento de parada
    stop_event = threading.Event()

    # Inicia a nova thread
    background_thread = threading.Thread(target=background_ip_check, args=(vlan,))
    background_thread.daemon = True  # PH: Define a thread como daemon
    background_thread.start()

    return jsonify({"status": "Search started", "vlan": vlan})

if __name__ == '__main__':
    app.run(debug=True)
