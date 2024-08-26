import concurrent.futures
from ping3 import ping
from collections import deque


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
        if ping(ip, timeout=6): 
            ip_status_dict[ip].append("on")
        
    with concurrent.futures.ThreadPoolExecutor(max_workers=255) as executor:
        executor.map(verificar_ip, ip_list)

    for ip in ip_list:
            if ip_status_dict[ip].count("on") == 0:
                ip_checked[ip] = "off"
            else:
                ip_checked[ip] = "on"
                
    ip_status_list = [{"ip": ip, "status": status} for ip, status in ip_checked.items()]

    return ip_status_list

    

