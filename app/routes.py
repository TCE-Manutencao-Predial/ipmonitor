from flask import Flask, render_template, jsonify, make_response, request  # Importa as funções necessárias do Flask.
from app import ip_operations  # Importa o módulo 'ip_operations' da aplicação, que contém a função 'verificar_ips'.
import time  # Módulo para manipulação de tempo (usado para pausas e delays).
import threading  # Módulo para rodar threads em paralelo (execução simultânea).
from app import app  # Importa a instância 'app' da aplicação Flask.
import concurrent.futures  # Para execução concorrente de múltiplas tarefas.

# Dicionário global que armazenará o status dos IPs verificados, por VLAN.
check_ip = {}

# Constante que define o caminho raiz para os endpoints da API.
RAIZ = '/ipmonitor'

# Função que verifica os IPs em uma determinada VLAN em segundo plano.
# Esta função é chamada pelas threads para rodar verificações assíncronas.
def background_ip_check(vlan):
    global check_ip
    rede_base = '172.17.' + str(vlan) + '.'  # Define a base do endereço IP para a VLAN específica.
    
    # Para debugging: exibe uma mensagem indicando qual VLAN está sendo verificada.
    print(f"Verificando em background a VLAN {vlan} e rede_base {rede_base}.")

    # Chama a função 'verificar_ips' do módulo 'ip_operations' e armazena o resultado no dicionário 'check_ip'.
    check_ip[vlan] = ip_operations.verificar_ips(rede_base)


'''API ENDPOINTS'''        

# Define o endpoint principal para a página inicial.
@app.route('/')  # Rota para rodar localmente.
@app.route(RAIZ + '/')  # Rota que inclui o prefixo 'RAIZ' para ambiente de produção.
def index():
    # Renderiza o arquivo HTML 'index.html' como resposta.
    return render_template('index.html')

# Define o endpoint para retornar o status dos IPs verificados em formato JSON.
@app.route('/api/ip-status')  # Rota para rodar localmente.
@app.route(RAIZ + '/api/ip-status')  # Rota com prefixo 'RAIZ' para produção.
def ip_status():
    # Retorna o conteúdo do dicionário 'check_ip' (status dos IPs) como um JSON.
    return jsonify(check_ip)
    
# Endpoint para iniciar a verificação de uma VLAN específica.
@app.route('/api/start-check/<string:vlan>', methods=['GET'])  # Rota local.
@app.route(RAIZ + '/api/start-check/<string:vlan>', methods=['GET'])  # Rota com prefixo 'RAIZ'.
def check(vlan):
    try:
        # Tenta retornar o status da VLAN solicitada em formato JSON.
        return jsonify(check_ip[int(vlan)])
    except KeyError:
        # Caso a VLAN ainda não tenha sido verificada, retorna status 204 (No Content).
        print(f"VLAN {vlan} não encontrada em check_ip por enquanto.")
        return '', 204  # Resposta vazia com status 204.

# Função que inicia o serviço de verificação de IPs em segundo plano.
def start_background_service():
    print("Iniciando serviço de verificação em background.")
    
    # Função interna que define um loop de verificação das VLANs.
    def check_loop():
        vlan_list = [70, 80, 85, 86, 200, 204]  # Lista de VLANs a serem verificadas.
        
        # Loop infinito que verifica as VLANs a cada intervalo de tempo (10 segundos).
        while True:
            # Usa um pool de threads para verificar duas VLANs simultaneamente.
            with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
                executor.map(background_ip_check, vlan_list)  # Aplica a função de verificação para cada VLAN na lista.
            time.sleep(10)  # Aguarda 10 segundos antes de iniciar a próxima verificação.

    # Inicia a execução do loop de verificação em uma nova thread.
    threading.Thread(target=check_loop).start()
    
# Ponto de entrada da aplicação. Executa o Flask quando o script é rodado diretamente.
if __name__ == '__main__':
    app.run(debug=True)  # Inicia o servidor Flask em modo debug.
