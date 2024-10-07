from flask import Flask, render_template, jsonify, make_response, request
from app import ip_operations
import time
import threading
from app import app

# PH: Alterado check_ip para um dicionário para lidar com múltiplas VLANs
check_ip = {}  # PH: Dados em cache por VLAN
background_threads = {}  # PH: Threads por VLAN
stop_events = {}  # PH: Eventos de parada por VLAN

RAIZ = '/ipmonitor'

# PH: Lista de VLANs para iniciar na inicialização
initial_vlans = ['70', '80', '85', '86', '200', '204']

# Rotina de background para verificar os IPs
def background_ip_check(vlan):
    rede_base = '172.17.' + vlan + '.'

    while not stop_events[vlan].is_set():  # PH: Usa o evento de parada para a VLAN específica
        # PH: Atualiza o cache para a VLAN específica
        check_ip[vlan] = ip_operations.verificar_ips(rede_base)
        time.sleep(30)  # PH: Aguarda antes da próxima atualização

'''API ENDPOINTS'''

@app.route('/')  # Para rodar localmente
@app.route(RAIZ + '/')
def index():
    return render_template('index.html')

@app.route('/api/ip-status')  # Para rodar localmente
@app.route(RAIZ + '/api/ip-status')
def ip_status():
    # PH: Retorna os dados em cache para todas as VLANs
    return jsonify(check_ip)

@app.route('/api/start-check/<string:vlan>', methods=['GET'])  # Para rodar localmente
@app.route(RAIZ + '/api/start-check/<string:vlan>', methods=['GET'])
def check(vlan):
    vlan = vlan.strip()
    
    print(f"Verificando a VLAN {vlan}.")

    # PH: Inicia a verificação para a VLAN especificada
    if vlan in background_threads and background_threads[vlan].is_alive():
        # PH: Se já estiver rodando, para e reinicia
        stop_events[vlan].set()
        background_threads[vlan].join()

    # PH: Inicializa o evento de parada e o cache para a VLAN
    stop_events[vlan] = threading.Event()
    check_ip[vlan] = []

    # PH: Inicia uma nova thread de background para esta VLAN
    background_threads[vlan] = threading.Thread(target=background_ip_check, args=(vlan,))
    background_threads[vlan].start()

    return jsonify({"status": "Search started", "vlan": vlan})

# PH: Inicia as verificações de background para as VLANs iniciais na inicialização
def start_initial_checks():
    print("Iniciando verificação inicial das VLANs.")
    
    for vlan in initial_vlans:
        vlan = vlan.strip()
        stop_events[vlan] = threading.Event()
        check_ip[vlan] = []

        background_threads[vlan] = threading.Thread(target=background_ip_check, args=(vlan,))
        background_threads[vlan].start()

# PH: Chama a função para iniciar as verificações iniciais quando o app inicia
if __name__ == '__main__':
    start_initial_checks()
    app.run(debug=True)
