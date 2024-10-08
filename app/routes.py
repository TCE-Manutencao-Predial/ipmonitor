from flask import Flask, render_template, jsonify, make_response, request
from app import ip_operations
import time
import threading
from app import app
import concurrent.futures

check_ip = {}

RAIZ = '/ipmonitor'

# Rotina background para verificar os IPs
def background_ip_check(vlan):
    global check_ip
    rede_base = '172.17.' + str(vlan) + '.'
    
    # PH: somente para debugging:
    print(f"Verificando em background a VLAN {vlan}.")

    check_ip[vlan] = ip_operations.verificar_ips(rede_base)


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
    try:
        return jsonify(check_ip[int(vlan)])
    except KeyError:
        print(f"VLAN {vlan} não encontrada em check_ip por enquanto.")
        return '', 204  # Resposta vazia com status 204 (No Content)

def start_background_service():
    def check_loop():
        vlan_list = [70,80,85,86,200,204]
        while True:
            with concurrent.futures.ThreadPoolExecutor(max_workers=6) as executor:
                executor.map(background_ip_check, vlan_list)
            time.sleep(10)

    threading.Thread(target=check_loop).start()

if __name__ == '__main__':
    app.run(debug=True)
    