import json
import os
from threading import Lock
from datetime import datetime
from app.config_manager import config_manager

class IPDeviceManager:
    """Gerenciador de dispositivos IP com tipos"""
    
    def __init__(self, devices_file='ip_devices.json'):
        self.devices_file = devices_file
        self.devices_lock = Lock()
        self.devices = self._load_devices()
    
    def _load_devices(self):
        """Carrega dispositivos do arquivo JSON"""
        try:
            if os.path.exists(self.devices_file):
                with open(self.devices_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                # Se não existe, criar estrutura baseada no ips_list.json existente
                return self._migrate_from_ips_list()
        except Exception as e:
            print(f"Erro ao carregar dispositivos: {e}")
            return {"vlans": {}}
    
    def _migrate_from_ips_list(self):
        """Migra dados do ips_list.json existente"""
        try:
            if os.path.exists('ips_list.json'):
                with open('ips_list.json', 'r', encoding='utf-8') as f:
                    old_data = json.load(f)
                
                new_structure = {"vlans": {}}
                
                for vlan, devices in old_data.get('vlans', {}).items():
                    new_structure['vlans'][vlan] = []
                    for device in devices:
                        new_device = {
                            "ip": device.get("ip", ""),
                            "descricao": device.get("descricao", ""),
                            "tipo": "",  # Novo campo vazio inicialmente
                            "created_at": datetime.now().isoformat(),
                            "updated_at": datetime.now().isoformat()
                        }
                        new_structure['vlans'][vlan].append(new_device)
                
                # Salvar a nova estrutura
                self._save_devices(new_structure)
                return new_structure
            else:
                return {"vlans": {}}
        except Exception as e:
            print(f"Erro na migração: {e}")
            return {"vlans": {}}
    
    def _save_devices(self, devices_data=None):
        """Salva dispositivos no arquivo JSON"""
        try:
            with self.devices_lock:
                data_to_save = devices_data if devices_data else self.devices
                with open(self.devices_file, 'w', encoding='utf-8') as f:
                    json.dump(data_to_save, f, indent=4, ensure_ascii=False)
                return True
        except Exception as e:
            print(f"Erro ao salvar dispositivos: {e}")
            return False
    
    def get_devices_by_vlan(self, vlan):
        """Obtém dispositivos de uma VLAN específica"""
        with self.devices_lock:
            return self.devices.get('vlans', {}).get(str(vlan), [])
    
    def add_device(self, vlan, ip, descricao, tipo=""):
        """Adiciona um novo dispositivo"""
        try:
            with self.devices_lock:
                vlan_str = str(vlan)
                
                if 'vlans' not in self.devices:
                    self.devices['vlans'] = {}
                
                if vlan_str not in self.devices['vlans']:
                    self.devices['vlans'][vlan_str] = []
                
                # Verificar se IP já existe
                for device in self.devices['vlans'][vlan_str]:
                    if device['ip'] == ip:
                        return False, "IP já existe nesta VLAN"
                
                new_device = {
                    "ip": ip,
                    "descricao": descricao,
                    "tipo": tipo,
                    "created_at": datetime.now().isoformat(),
                    "updated_at": datetime.now().isoformat()
                }
                
                self.devices['vlans'][vlan_str].append(new_device)
                
                if self._save_devices():
                    return True, "Dispositivo adicionado com sucesso"
                else:
                    return False, "Erro ao salvar dispositivo"
        
        except Exception as e:
            print(f"Erro ao adicionar dispositivo: {e}")
            return False, str(e)
    
    def update_device(self, vlan, ip, descricao=None, tipo=None):
        """Atualiza um dispositivo existente"""
        try:
            with self.devices_lock:
                vlan_str = str(vlan)
                
                if vlan_str not in self.devices.get('vlans', {}):
                    return False, "VLAN não encontrada"
                
                for device in self.devices['vlans'][vlan_str]:
                    if device['ip'] == ip:
                        if descricao is not None:
                            device['descricao'] = descricao
                        if tipo is not None:
                            device['tipo'] = tipo
                        device['updated_at'] = datetime.now().isoformat()
                        
                        if self._save_devices():
                            return True, "Dispositivo atualizado com sucesso"
                        else:
                            return False, "Erro ao salvar alterações"
                
                return False, "Dispositivo não encontrado"
        
        except Exception as e:
            print(f"Erro ao atualizar dispositivo: {e}")
            return False, str(e)
    
    def delete_device(self, vlan, ip):
        """Remove um dispositivo"""
        try:
            with self.devices_lock:
                vlan_str = str(vlan)
                
                if vlan_str not in self.devices.get('vlans', {}):
                    return False, "VLAN não encontrada"
                
                devices_list = self.devices['vlans'][vlan_str]
                for i, device in enumerate(devices_list):
                    if device['ip'] == ip:
                        del devices_list[i]
                        
                        if self._save_devices():
                            return True, "Dispositivo removido com sucesso"
                        else:
                            return False, "Erro ao salvar alterações"
                
                return False, "Dispositivo não encontrado"
        
        except Exception as e:
            print(f"Erro ao remover dispositivo: {e}")
            return False, str(e)
    
    def get_device_types_by_vlan(self, vlan):
        """Obtém tipos únicos de dispositivos em uma VLAN"""
        with self.devices_lock:
            devices = self.devices.get('vlans', {}).get(str(vlan), [])
            types = set()
            for device in devices:
                if device.get('tipo'):
                    types.add(device['tipo'])
            return list(types)
    
    def search_devices(self, query, vlan=None):
        """Busca dispositivos por descrição, IP ou tipo"""
        results = []
        query_lower = query.lower()
        
        with self.devices_lock:
            vlans_to_search = [str(vlan)] if vlan else self.devices.get('vlans', {}).keys()
            
            for vlan_id in vlans_to_search:
                for device in self.devices.get('vlans', {}).get(vlan_id, []):
                    if (query_lower in device.get('descricao', '').lower() or
                        query_lower in device.get('ip', '').lower() or
                        query_lower in device.get('tipo', '').lower()):
                        
                        result = device.copy()
                        result['vlan'] = vlan_id
                        results.append(result)
        
        return results
    
    def get_statistics(self):
        """Obtém estatísticas dos dispositivos"""
        stats = {
            'total_devices': 0,
            'devices_by_vlan': {},
            'devices_by_type': {},
            'devices_with_type': 0,
            'devices_without_type': 0
        }
        
        with self.devices_lock:
            for vlan, devices in self.devices.get('vlans', {}).items():
                stats['devices_by_vlan'][vlan] = len(devices)
                stats['total_devices'] += len(devices)
                
                for device in devices:
                    device_type = device.get('tipo', '')
                    if device_type:
                        stats['devices_with_type'] += 1
                        if device_type not in stats['devices_by_type']:
                            stats['devices_by_type'][device_type] = 0
                        stats['devices_by_type'][device_type] += 1
                    else:
                        stats['devices_without_type'] += 1
        
        return stats

# Instância global do gerenciador de dispositivos
device_manager = IPDeviceManager()