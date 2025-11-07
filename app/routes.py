from flask import Flask, render_template, jsonify, make_response, request  # Importa as funções necessárias do Flask.
from app import ip_operations  # Importa o módulo 'ip_operations' da aplicação, que contém a função 'verificar_ips'.
import time  # Módulo para manipulação de tempo (usado para pausas e delays).
import threading  # Módulo para rodar threads em paralelo (execução simultânea).
from app import app  # Importa a instância 'app' da aplicação Flask.
import concurrent.futures  # Para execução concorrente de múltiplas tarefas.
import logging  # Adicionar logging
import json  # Para serialização de dados em logs
from app.config_manager import config_manager  # Importa o gerenciador de configurações.
from app.device_manager import device_manager  # Importa o gerenciador de dispositivos.

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Dicionário global que armazenará o status dos IPs verificados, por VLAN.
check_ip = {}

# Constante que define o caminho raiz para os endpoints da API.
RAIZ = '/ipmonitor'

# Variável global para controlar o loop de verificação
background_thread = None
should_stop = False

# Função que verifica os IPs em uma determinada VLAN em segundo plano.
# Esta função é chamada pelas threads para rodar verificações assíncronas.
def background_ip_check(vlan):
    global check_ip
    rede_base = '172.17.' + str(vlan) + '.'  # Define a base do endereço IP para a VLAN específica.
    
    logging.info(f"[BACKGROUND] Verificando em background a VLAN {vlan} e rede_base {rede_base}")

    # Chama a função 'verificar_ips' do módulo 'ip_operations' e armazena o resultado no dicionário 'check_ip'.
    result = ip_operations.verificar_ips(rede_base)
    
    # Log dos resultados antes de armazenar
    items_com_tipo = [item for item in result if item.get('tipo') and item['tipo'].strip()]
    logging.info(f"[BACKGROUND] VLAN {vlan} - Resultado: {len(result)} itens, {len(items_com_tipo)} com tipo")
    
    check_ip[vlan] = result


'''API ENDPOINTS'''        

# Define o endpoint principal para a página inicial.
@app.route('/')  # Rota para rodar localmente.
@app.route(RAIZ + '/')  # Rota que inclui o prefixo 'RAIZ' para ambiente de produção.
def index():
    # Renderiza o arquivo HTML 'index.html' como resposta.
    return render_template('index.html')

# Define o endpoint principal para a página de configurações.
@app.route('/configuracoes')  # Rota para rodar localmente.
@app.route(RAIZ + '/configuracoes')  # Rota que inclui o prefixo 'RAIZ' para ambiente de produção.
def configuracoes():
    # Obtém as configurações atuais
    config = config_manager.get_config()
    # Renderiza o arquivo HTML 'configuracoes.html' com as configurações
    return render_template('configuracoes.html', config=config)

# Define o endpoint principal para a página de gerenciamento de dispositivos.
@app.route('/dispositivos')  # Rota para rodar localmente.
@app.route(RAIZ + '/dispositivos')  # Rota que inclui o prefixo 'RAIZ' para ambiente de produção.
def dispositivos():
    # Renderiza o arquivo HTML 'dispositivos.html' sem dependências Jinja2
    return render_template('dispositivos.html')

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
        result = check_ip[int(vlan)]
        
        # Log para diagnóstico
        logging.info(f"[ROUTES] API /api/start-check/{vlan} - Retornando {len(result)} itens")
        items_com_tipo = [item for item in result if item.get('tipo') and item['tipo'].strip()]
        logging.info(f"[ROUTES] Items com tipo na resposta: {len(items_com_tipo)}")
        if items_com_tipo:
            logging.info(f"[ROUTES] Exemplo com tipo: {items_com_tipo[0]}")
        
        return jsonify(result)
    except KeyError:
        # Caso a VLAN ainda não tenha sido verificada, retorna status 204 (No Content).
        logging.warning(f"[ROUTES] VLAN {vlan} não encontrada em check_ip por enquanto.")
        return '', 204  # Resposta vazia com status 204.

# Endpoint para salvar configurações
@app.route('/api/config/save', methods=['POST'])
@app.route(RAIZ + '/api/config/save', methods=['POST'])
def save_config():
    logging.info('[CONFIG] ========== INÍCIO SALVAMENTO DE CONFIGURAÇÕES ==========')
    try:
        # Log da requisição recebida
        logging.info(f'[CONFIG] Método: {request.method}')
        logging.info(f'[CONFIG] Content-Type: {request.content_type}')
        logging.info(f'[CONFIG] Headers: {dict(request.headers)}')
        
        data = request.get_json()
        logging.info(f'[CONFIG] Dados recebidos (JSON): {json.dumps(data, indent=2, ensure_ascii=False)}')
        
        # Validar dados antes de salvar
        logging.info('[CONFIG] Validando dados de configuração...')
        if not validate_config_data(data):
            logging.error('[CONFIG] ❌ Validação falhou - dados inválidos')
            return jsonify({'error': 'Dados de configuração inválidos'}), 400
        
        logging.info('[CONFIG] ✅ Validação passou')
        
        # Atualizar configurações por seção
        logging.info('[CONFIG] Atualizando configurações por seção...')
        for section, values in data.items():
            logging.info(f'[CONFIG] Atualizando seção: {section}')
            logging.info(f'[CONFIG] Valores da seção {section}: {values}')
            
            if not config_manager.update_section(section, values):
                logging.error(f'[CONFIG] ❌ Erro ao atualizar seção {section}')
                return jsonify({'error': f'Erro ao atualizar seção {section}'}), 500
            
            logging.info(f'[CONFIG] ✅ Seção {section} atualizada com sucesso')
        
        # Reiniciar serviço de background com novas configurações
        logging.info('[CONFIG] Reiniciando serviço de background...')
        restart_background_service()
        logging.info('[CONFIG] ✅ Serviço de background reiniciado')
        
        logging.info('[CONFIG] ========== CONFIGURAÇÕES SALVAS COM SUCESSO ==========')
        return jsonify({
            'success': True,
            'message': 'Configurações salvas com sucesso'
        })
    
    except Exception as e:
        logging.error(f'[CONFIG] ❌ EXCEÇÃO ao salvar configurações: {e}')
        logging.error(f'[CONFIG] Stack trace:', exc_info=True)
        return jsonify({'error': str(e)}), 500

# Endpoint para resetar configurações
@app.route('/api/config/reset', methods=['POST'])
@app.route(RAIZ + '/api/config/reset', methods=['POST'])
def reset_config():
    try:
        if config_manager.reset_to_defaults():
            restart_background_service()
            return jsonify({
                'success': True,
                'message': 'Configurações restauradas para os valores padrão'
            })
        else:
            return jsonify({'error': 'Erro ao resetar configurações'}), 500
    
    except Exception as e:
        print(f"Erro ao resetar configurações: {e}")
        return jsonify({'error': str(e)}), 500

# Endpoint de teste para diagnóstico de tipos
@app.route('/api/debug/devices/<int:vlan>')
@app.route(RAIZ + '/api/debug/devices/<int:vlan>')
def debug_devices(vlan):
    try:
        devices = device_manager.get_devices_by_vlan(vlan)
        return jsonify({
            'vlan': vlan,
            'total_devices': len(devices),
            'devices_with_type': [d for d in devices if d.get('tipo')],
            'all_devices': devices
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Endpoint para testar configurações
@app.route('/api/config/test', methods=['POST'])
@app.route(RAIZ + '/api/config/test', methods=['POST'])
def test_config():
    try:
        data = request.get_json()
        
        # Simular teste das configurações
        test_results = {
            'ping_tests': 0,
            'network_connectivity': True,
            'config_validity': True
        }
        
        # Testar algumas configurações básicas
        if 'network_settings' in data:
            timeout = data['network_settings'].get('ping_timeout', 2)
            if timeout < 1 or timeout > 10:
                test_results['config_validity'] = False
        
        if 'ping_intervals' in data:
            for vlan, interval in data['ping_intervals'].items():
                if interval < 5 or interval > 300:
                    test_results['config_validity'] = False
                test_results['ping_tests'] += 1
        
        message = f"Teste concluído. {test_results['ping_tests']} intervalos testados."
        if not test_results['config_validity']:
            message += " Alguns valores estão fora dos limites recomendados."
        
        return jsonify({
            'success': True,
            'message': message,
            'details': test_results
        })
    
    except Exception as e:
        print(f"Erro ao testar configurações: {e}")
        return jsonify({'error': str(e)}), 500

# Endpoints para gerenciar dispositivos
@app.route('/api/devices/<int:vlan>', methods=['GET'])
@app.route(RAIZ + '/api/devices/<int:vlan>', methods=['GET'])
def get_devices(vlan):
    try:
        devices = device_manager.get_devices_by_vlan(vlan)
        return jsonify({'success': True, 'devices': devices})
    except Exception as e:
        print(f"Erro ao obter dispositivos: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/devices/<int:vlan>', methods=['POST'])
@app.route(RAIZ + '/api/devices/<int:vlan>', methods=['POST'])
def add_device(vlan):
    try:
        data = request.get_json()
        ip = data.get('ip')
        descricao = data.get('descricao')  # Corrigido para usar 'descricao'
        tipo = data.get('tipo', '')
        
        if not ip or not descricao:
            return jsonify({'error': 'IP e descrição são obrigatórios'}), 400
        
        success, message = device_manager.add_device(vlan, ip, descricao, tipo)
        
        if success:
            return jsonify({'success': True, 'message': message})
        else:
            return jsonify({'error': message}), 400
    
    except Exception as e:
        print(f"Erro ao adicionar dispositivo: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/devices/<int:vlan>/<string:ip>', methods=['PUT'])
@app.route(RAIZ + '/api/devices/<int:vlan>/<string:ip>', methods=['PUT'])
def update_device(vlan, ip):
    try:
        data = request.get_json()
        descricao = data.get('descricao')  # Corrigido para usar 'descricao'
        tipo = data.get('tipo')
        
        success, message = device_manager.update_device(vlan, ip, descricao, tipo)
        
        if success:
            return jsonify({'success': True, 'message': message})
        else:
            return jsonify({'error': message}), 400
    
    except Exception as e:
        print(f"Erro ao atualizar dispositivo: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/devices/<int:vlan>', methods=['DELETE'])
@app.route(RAIZ + '/api/devices/<int:vlan>', methods=['DELETE'])
def delete_device(vlan):
    try:
        data = request.get_json()
        ip = data.get('ip')
        
        if not ip:
            return jsonify({'error': 'IP é obrigatório'}), 400
        
        success, message = device_manager.delete_device(vlan, ip)
        
        if success:
            return jsonify({'success': True, 'message': message})
        else:
            return jsonify({'error': message}), 400
    
    except Exception as e:
        print(f"Erro ao remover dispositivo: {e}")
        return jsonify({'error': str(e)}), 500

# Endpoints para gerenciar tipos de dispositivos
@app.route('/api/device-types/<int:vlan>', methods=['GET'])
@app.route(RAIZ + '/api/device-types/<int:vlan>', methods=['GET'])
def get_device_types(vlan):
    try:
        # Tipos configurados no sistema
        configured_types = config_manager.get_device_types(vlan)
        # Tipos únicos já usados na VLAN
        used_types = device_manager.get_device_types_by_vlan(vlan)
        
        # Combinar e remover duplicatas
        all_types = list(set(configured_types + used_types))
        all_types.sort()
        
        return jsonify({
            'success': True, 
            'types': all_types,
            'configured_types': configured_types,
            'used_types': used_types
        })
    except Exception as e:
        print(f"Erro ao obter tipos de dispositivos: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/device-types/<int:vlan>', methods=['POST'])
@app.route(RAIZ + '/api/device-types/<int:vlan>', methods=['POST'])
def add_device_type(vlan):
    try:
        data = request.get_json()
        device_type = data.get('type')
        
        if not device_type:
            return jsonify({'error': 'Tipo de dispositivo é obrigatório'}), 400
        
        success = config_manager.add_device_type(vlan, device_type)
        
        if success:
            return jsonify({'success': True, 'message': 'Tipo adicionado com sucesso'})
        else:
            return jsonify({'error': 'Erro ao adicionar tipo'}), 500
    
    except Exception as e:
        print(f"Erro ao adicionar tipo de dispositivo: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/device-types/<int:vlan>', methods=['DELETE'])
@app.route(RAIZ + '/api/device-types/<int:vlan>', methods=['DELETE'])
def delete_device_type(vlan):
    try:
        data = request.get_json()
        device_type = data.get('type')
        
        if not device_type:
            return jsonify({'error': 'Tipo é obrigatório'}), 400
        
        success = config_manager.remove_device_type(vlan, device_type)
        
        if success:
            return jsonify({'success': True, 'message': 'Tipo removido com sucesso'})
        else:
            return jsonify({'error': 'Erro ao remover tipo'}), 500
    
    except Exception as e:
        print(f"Erro ao remover tipo de dispositivo: {e}")
        return jsonify({'error': str(e)}), 500

# Função para validar dados de configuração
def validate_config_data(data):
    """Valida se os dados de configuração estão corretos"""
    logging.info('[VALIDATION] Iniciando validação de dados...')
    logging.info(f'[VALIDATION] Dados a validar: {json.dumps(data, indent=2, ensure_ascii=False)}')
    try:
        # Validar intervalos de ping
        if 'ping_intervals' in data:
            logging.info('[VALIDATION] Validando ping_intervals...')
            for vlan, interval in data['ping_intervals'].items():
                logging.info(f'[VALIDATION] VLAN {vlan}: intervalo = {interval} (tipo: {type(interval).__name__})')
                if not isinstance(interval, (int, float)) or interval < 5 or interval > 300:
                    logging.error(f'[VALIDATION] ❌ Intervalo inválido para {vlan}: {interval}')
                    return False
            logging.info('[VALIDATION] ✅ ping_intervals válido')
        
        # Validar configurações de rede
        if 'network_settings' in data:
            logging.info('[VALIDATION] Validando network_settings...')
            network = data['network_settings']
            if 'ping_timeout' in network:
                logging.info(f'[VALIDATION] ping_timeout = {network["ping_timeout"]} (tipo: {type(network["ping_timeout"]).__name__})')
                if not isinstance(network['ping_timeout'], (int, float)) or network['ping_timeout'] < 1 or network['ping_timeout'] > 10:
                    logging.error(f'[VALIDATION] ❌ ping_timeout inválido: {network["ping_timeout"]}')
                    return False
            if 'max_concurrent_pings' in network:
                logging.info(f'[VALIDATION] max_concurrent_pings = {network["max_concurrent_pings"]} (tipo: {type(network["max_concurrent_pings"]).__name__})')
                if not isinstance(network['max_concurrent_pings'], int) or network['max_concurrent_pings'] < 1 or network['max_concurrent_pings'] > 10:
                    logging.error(f'[VALIDATION] ❌ max_concurrent_pings inválido: {network["max_concurrent_pings"]}')
                    return False
            if 'retry_attempts' in network:
                logging.info(f'[VALIDATION] retry_attempts = {network["retry_attempts"]} (tipo: {type(network["retry_attempts"]).__name__})')
                if not isinstance(network['retry_attempts'], int) or network['retry_attempts'] < 0 or network['retry_attempts'] > 5:
                    logging.error(f'[VALIDATION] ❌ retry_attempts inválido: {network["retry_attempts"]}')
                    return False
            logging.info('[VALIDATION] ✅ network_settings válido')
        
        logging.info('[VALIDATION] ✅ Todos os dados são válidos')
        return True
    except Exception as e:
        logging.error(f'[VALIDATION] ❌ Erro na validação: {e}')
        logging.error('[VALIDATION] Stack trace:', exc_info=True)
        return False

# Função para reiniciar o serviço de background
def restart_background_service():
    """Reinicia o serviço de background com as novas configurações"""
    global should_stop, background_thread
    
    logging.info('[CONFIG] Solicitando parada do serviço de background...')
    # Sinalizar para parar o thread atual
    should_stop = True
    
    # NÃO aguardar aqui - deixar o thread parar naturalmente
    # O novo thread será iniciado imediatamente
    logging.info('[CONFIG] Flag should_stop definida como True')
    
    # Resetar flag e iniciar novo serviço em uma thread separada
    # para não bloquear a resposta HTTP
    def restart_async():
        global should_stop
        logging.info('[CONFIG] Aguardando 1 segundo antes de reiniciar...')
        time.sleep(1)
        should_stop = False
        logging.info('[CONFIG] Iniciando novo serviço de background...')
        start_background_service()
        logging.info('[CONFIG] Serviço de background reiniciado')
    
    # Executar restart em thread separada
    restart_thread = threading.Thread(target=restart_async, daemon=True)
    restart_thread.start()
    logging.info('[CONFIG] Thread de restart iniciada')

# Função que inicia o serviço de verificação de IPs em segundo plano.
def start_background_service():
    global background_thread, should_stop
    
    print("Iniciando serviço de verificação em background.")
    
    # Função interna que define um loop de verificação das VLANs.
    def check_loop():
        while not should_stop:
            # Obter VLANs ativas das configurações
            vlan_list = config_manager.get_active_vlans()
            
            # Usar configurações de concurrent pings
            max_workers = config_manager.get_config('network_settings').get('max_concurrent_pings', 3)
            
            # Usar um pool de threads para verificar VLANs simultaneamente
            with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
                executor.map(background_ip_check, vlan_list)
            
            # Aguardar intervalo configurado (usar o menor intervalo como base)
            ping_intervals = config_manager.get_config('ping_intervals')
            min_interval = min(ping_intervals.values()) if ping_intervals else 10
            
            # Verificar se deve parar durante o sleep
            for _ in range(int(min_interval)):
                if should_stop:
                    break
                time.sleep(1)

    # Inicia a execução do loop de verificação em uma nova thread.
    background_thread = threading.Thread(target=check_loop, daemon=True)
    background_thread.start()
    
# Ponto de entrada da aplicação. Executa o Flask quando o script é rodado diretamente.
if __name__ == '__main__':
    app.run(debug=True)  # Inicia o servidor Flask em modo debug.
