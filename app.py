from flask import Flask, render_template, jsonify
from ip_operations import verificar_ips
import time
app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/ip-status')
def ip_status():
    rede_base = '172.17.86.'
    check_ip = verificar_ips(rede_base)
    return jsonify(check_ip)

if __name__ == '__main__': 
    app.run(debug=True)
