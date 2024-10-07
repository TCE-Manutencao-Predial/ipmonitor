from flask import Flask, render_template, jsonify, make_response, request
from app import ip_operations
import time
import threading
from app import app



check_ip = []
background_thread = None
stop_event = threading.Event()

RAIZ = '/ipmonitor'

# Inicializar sistema com essa rotina para já verificar todas as vlans:
def verificacao_inicial_vlans():
    # PH: Lista de VLANs para iniciar na inicialização
    initial_vlans = ['70', '80', '85', '86', '200', '204']
    
    for vlan in initial_vlans:
        background_ip_check(vlan)

# Rotina background para verificar os IPs
def background_ip_check(vlan):
    global check_ip
    rede_base = '172.17.' + vlan + '.'
    
    # PH: somente para debugging:
    print(f"Verificando em background a VLAN {vlan}.")

    while not stop_event.is_set():  # Usa o evento de parada para verificar se a thread deve parar
        check_ip = ip_operations.verificar_ips(rede_base)
        #stop_event.wait(30) 


'''API ENDPOINTS'''        

@app.route('/') # Para rodar localmente
@app.route(RAIZ + '/')
def index():
    return render_template('index.html')

@app.route('/api/ip-status') # Para rodar localmente
@app.route(RAIZ + '/api/ip-status')
def ip_status():
    return jsonify(check_ip)

@app.route('/api/start-check/<string:vlan>', methods=['GET']) # Para rodar localmente
@app.route(RAIZ + '/api/start-check/<string:vlan>', methods=['GET'])
def check(vlan):
    global background_thread, stop_event, check_ip

    # PH: somente para debugging:
    print(f"Verificando VLAN {vlan}.")
    
    check_ip = []
    
    # Acaba com a thread anterior se estiver rodando
    if background_thread and background_thread.is_alive():
        stop_event.set()  
        background_thread.join()  

    # recomeça o evento de parada
    stop_event = threading.Event()

    # Começa a nova thread
    background_thread = threading.Thread(target=background_ip_check, args=(vlan,))
    background_thread.start()

    return jsonify({"status": "Search started", "vlan": vlan})

if __name__ == '__main__':
    app.run(debug=True)
    
# Função inicial de verificação:
verificacao_inicial_vlans()