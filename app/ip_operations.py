import concurrent.futures
from ping3 import ping
from collections import deque
import json
import threading  # PH: Importa threading para criar threads
import time       # PH: Importa time para usar sleep

# PH: Variáveis globais para cache e controle de threads
ip_status_list_cache = []
cache_lock = threading.Lock()       # PH: Lock para garantir thread safety
stop_event = threading.Event()      # PH: Evento para controlar a parada da thread
background_thread = None            # PH: Variável para a thread de background

def verificar_ips(rede_base: str):
    with cache_lock:  # PH: Garante acesso seguro ao cache
        data = ip_status_list_cache.copy()  # PH: Copia os dados do cache
    return data  # PH: Retorna os dados em cache imediatamente

def update_cache(rede_base: str):
    global ip_status_list_cache  # PH: Declara variável global
    ip_list = [rede_base + str(i) for i in range(1, 255)]
    ip_history = deque(maxlen=10)
    
    for i in range(0,10):
        ip_history.append("off")
    
    # Dicionário para armazenar o histórico de status de cada IP
    ip_status_dict = {status_history: ip_history.copy() for status_history in ip_list}

    # Dicionário para armazenar o status de cada IP após verificação
    ip_checked = {ip: "on" for ip in ip_list}

    def verificar_ip(ip):
        if ping(ip, timeout=5): 
            ip_status_dict[ip].append("on")
        
    with concurrent.futures.ThreadPoolExecutor(max_workers=255) as executor:
        executor.map(verificar_ip, ip_list)

    for ip in ip_list:
        if ip_status_dict[ip].count("on") == 0:
            ip_checked[ip] = "off"
        else:
            ip_checked[ip] = "on"   

    vlan = rede_base.split('.')[2]
    all_vlan_list = vlan_loader()
    vlan_list = all_vlan_list.get('vlans').get(vlan)
                
    ip_status_list = [{"ip": ip, "status": status} for ip, status in ip_checked.items() if status == "off"]
    if vlan_list != None:
        for item in ip_status_list:
            for vlan in vlan_list:
                if item['ip'] == vlan['ip']:
                    item['descricao'] = vlan['descricao']
                    break
                else:
                    item['descricao'] = '-'
    else:
        for item in ip_status_list:
            item['descricao'] = '-'

    with cache_lock:  # PH: Garante acesso seguro ao atualizar o cache
        ip_status_list_cache = ip_status_list  # PH: Atualiza o cache com os novos dados

def background_updater(rede_base: str):
    while not stop_event.is_set():  # PH: Verifica se deve parar a thread
        update_cache(rede_base)     # PH: Atualiza o cache
        time.sleep(30)              # PH: Aguarda 30 segundos antes da próxima atualização

def start_background_thread(rede_base: str):
    global background_thread, stop_event  # PH: Declara variáveis globais

    # PH: Encerra a thread anterior se estiver rodando
    if background_thread and background_thread.is_alive():
        stop_event.set()
        background_thread.join()

    stop_event = threading.Event()  # PH: Reinicia o evento de parada

    # PH: Inicia a nova thread de background
    background_thread = threading.Thread(target=background_updater, args=(rede_base,))
    background_thread.daemon = True  # PH: Define a thread como daemon
    background_thread.start()

def vlan_loader():
    file_path = 'ips_list.json'
    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
    return data
