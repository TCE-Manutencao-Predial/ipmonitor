import concurrent.futures
from ping3 import ping
from collections import deque
import json

def verificar_ips(rede_base: str):
    ip_list = [rede_base + str(i) for i in range(1, 255)]
    ip_history = deque(maxlen=10)
    
    print(f"Verificando rede base n° {rede_base}.")
    
    # Inicializar o histórico com "off" para cada IP
    for i in range(0, 10):
        ip_history.append("off")
    
    # Dicionário para armazenar o histórico de status de cada IP com instâncias individuais
    ip_status_dict = {ip: deque(["off"] * 10, maxlen=10) for ip in ip_list}

    # Dicionário para armazenar o status de cada IP após verificação
    ip_checked = {ip: "on" for ip in ip_list}

    def verificar_ip(ip):
        #print(f"IP n° {ip}", end='-')
        if ping(ip, timeout=5): 
            ip_status_dict[ip].append("on")
        else:
            ip_status_dict[ip].append("off")

    # Executar a verificação de IPs de forma concorrente
    with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
        executor.map(verificar_ip, ip_list)

    # Atualizar o status final de cada IP após a verificação
    for ip in ip_list:
        if ip_status_dict[ip].count("on") == 0:
            ip_checked[ip] = "off"
        else:
            ip_checked[ip] = "on"

    vlan = rede_base.split('.')[2]
    all_vlan_list = vlan_loader()
    vlan_list = all_vlan_list.get('vlans').get(vlan)
                
    ip_status_list = [{"ip": ip, "status": status} for ip, status in ip_checked.items()]
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

    return ip_status_list

def vlan_loader():
    file_path = 'ips_list.json'
    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
    return data
