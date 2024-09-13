from flask import Flask, render_template, jsonify, make_response, request
from ip_operations import verificar_ips
import time
import threading

app = Flask(__name__)

check_ip = []
background_thread = None
stop_event = threading.Event()

# Rotina background para verificar os IPs
def background_ip_check(vlan):
    global check_ip
    rede_base = '172.17.' + vlan + '.'

    while not stop_event.is_set():  # Usa o evento de parada para verificar se a thread deve parar
        check_ip = verificar_ips(rede_base)
        stop_event.wait(30) 

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/ip-status')
def ip_status():
    if not check_ip:
        return make_response('Lista vazia', 204)
    return jsonify(check_ip)

@app.route('/start-check/<string:vlan>', methods=['GET'])
def check(vlan):
    global background_thread, stop_event, check_ip

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
