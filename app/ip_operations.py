import concurrent.futures
from ping3 import ping
from collections import deque
import json


def verificar_ips(rede_base: str):
    ip_list = [rede_base + str(i) for i in range(1, 255)]
    ip_history = deque(maxlen=10)
    
    for i in range(0,10):
        ip_history.append("off")
    
    # Dicionario para armazenar o historico de status de cada IP
    ip_status_dict = {status_history: ip_history.copy() for status_history in ip_list}

    # Dicionario para armazenar o status de cada IP apos verificao
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

    for item in ip_status_list:
        for vlan in vlan_list:
                if item['ip'] == vlan['ip']:
                     item['descricao'] = vlan['descricao']
                     break
                else:
                    item['descricao'] = '-'

    return ip_status_list


def vlan_loader():
    file_path = 'ips_list.json'
    with open(file_path, 'r', encoding = 'utf-8') as file:
        data = json.load(file)
    return data    

