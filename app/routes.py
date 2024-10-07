from flask import Flask, render_template, jsonify, make_response, request
from app import ip_operations
import time
import threading
from app import app
import concurrent.futures

check_ip = {}
background_thread = None
stop_event = threading.Event()

RAIZ = '/ipmonitor'

# Rotina background para verificar os IPs
def background_ip_check(vlan):
    global check_ip
    rede_base = '172.17.' + str(vlan) + '.'
    
    # PH: somente para debugging:
    print(f"Verificando em background a VLAN {vlan}.")

    check_ip[vlan] = ip_operations.verificar_ips(rede_base)

def get_check_ip():
    global check_ip
    return check_ip

'''API ENDPOINTS'''        

@app.route('/') # Para rodar localmente
@app.route(RAIZ + '/')
def index():
    get_check_ip()
    return render_template('index.html')

@app.route('/api/ip-status') # Para rodar localmente
@app.route(RAIZ + '/api/ip-status')
def ip_status():
    return jsonify(check_ip)

@app.route('/api/start-check/<string:vlan>', methods=['GET']) # Para rodar localmente
@app.route(RAIZ + '/api/start-check/<string:vlan>', methods=['GET'])
def check(vlan):
    return jsonify(check_ip[int(vlan)])

def start_background_service():
    vlan_list = [70,80,85,86,200,204]
    rede_base = '172.17.'
    rede_base_list = [rede_base + str(vlan) + '.' for vlan in vlan_list]
    def check_loop():
        vlan_list = [70,80,85,86,200,204]
        while True:
            # for vlan in vlan_list:
            #     background_ip_check(str(vlan))
            with concurrent.futures.ThreadPoolExecutor(max_workers=6) as executor:
                executor.map(background_ip_check, vlan_list)
            time.sleep(10)
    threading.Thread(target=check_loop).start()

if __name__ == '__main__':
    app.run(debug=True)
    