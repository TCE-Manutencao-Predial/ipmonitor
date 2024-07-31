import concurrent.futures
from ping3 import ping

REDE_BASE = "172.17.86."

ip_list = [REDE_BASE + str(i) for i in range(1, 255)]
ip_status_dict = {ip: "on" for ip in ip_list}

def verificar_ips_sem_uso():

    def verificar_ip(ip):
        if not ping(ip, timeout=2): 
            ip_status_dict[ip] = "off"
        
    with concurrent.futures.ThreadPoolExecutor(max_workers=255) as executor:
        executor.map(verificar_ip, ip_list)
        
    ip_status_list = [{"ip": ip, "status": status} for ip, status in ip_status_dict.items()]

    return ip_status_list





