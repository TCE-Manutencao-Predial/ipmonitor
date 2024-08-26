from flask import Flask, render_template, jsonify
from ip_operations import verificar_ips
import time
import threading
from collections import deque

app = Flask(__name__)


check_ip = []

# Rotina background para verificar os IPs a cada 30s
def background_ip_check():
    rede_base = '172.17.86.'
    global check_ip

    while True:
        check_ip = verificar_ips(rede_base)
        time.sleep(30)

thread = threading.Thread(target=background_ip_check,daemon=True)
thread.start()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/ip-status')
def ip_status():
    if not check_ip:
        return 204
    return jsonify(check_ip)

if __name__ == '__main__':
    app.run(debug=True)