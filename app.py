from flask import Flask, render_template, jsonify
from script import verificar_ips_sem_uso
import time
app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/ip-status')
def ip_status():
    check_ip = verificar_ips_sem_uso()
    return jsonify(check_ip)

if __name__ == '__main__': 
    app.run(debug=True)
