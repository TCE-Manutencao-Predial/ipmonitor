import json
import os
import logging
from threading import Lock
from app.migration import get_data_file_path

# Configurar logging para o módulo
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class ConfigManager:
    """Gerenciador de configurações do sistema IP Monitor"""
    
    def __init__(self, config_file='app_config.json'):
        self.config_file = get_data_file_path(config_file)
        self.config_lock = Lock()
        self.config = self._load_default_config()
        self.load_config()
        
        # Se o arquivo não existir, criar com as configurações padrão
        if not os.path.exists(self.config_file):
            logging.info('[CONFIG_MANAGER] Arquivo de configuração não existe, criando com valores padrão...')
            self.save_config()
            logging.info(f'[CONFIG_MANAGER] ✅ Arquivo criado em: {self.config_file}')
    
    def _load_default_config(self):
        """Carrega configurações padrão do sistema"""
        return {
            "ping_intervals": {
                "vlan_70": 12,   # Câmeras - moderada prioridade
                "vlan_80": 10,   # Alarme - alta prioridade
                "vlan_85": 8,    # Automação Ethernet - máxima prioridade
                "vlan_86": 12,   # Automação WiFi - moderada prioridade
                "vlan_200": 15,  # Telefonia IP Fixa - baixa prioridade
                "vlan_204": 15   # Telefonia IP Móvel - baixa prioridade
            },
            "network_settings": {
                "ping_timeout": 2,
                "max_concurrent_pings": 3,
                "retry_attempts": 2
            },
            "ui_settings": {
                "auto_refresh": True,
                "refresh_rate": 5,
                "show_offline_devices": True,
                "theme": "default"
            },
            "monitoring": {
                "enable_logging": True,
                "log_level": "INFO",
                "max_log_entries": 1000,
                "alert_on_device_down": False
            },
            "vlans": {
                "active_vlans": [70, 80, 85, 86, 200, 204],
                "vlan_descriptions": {
                    "70": "VLAN 70 - Câmeras",
                    "80": "VLAN 80 - Alarme",
                    "85": "VLAN 85 - Automação Ethernet", 
                    "86": "VLAN 86 - Automação WiFi",
                    "200": "VLAN 200 - Telefonia IP Fixa",
                    "204": "VLAN 204 - Telefonia IP Móvel"
                },
                "device_types": {
                    "70": ["Câmera IP", "DVR", "NVR", "Switch PoE"],
                    "80": ["Central de Alarme", "Sensor", "Sirene", "Teclado"],
                    "85": ["CLP", "IHM", "Inversor", "Controladora", "Sensor", "UPS", "GMG"],
                    "86": ["Sensor IoT", "Gateway", "Access Point", "Controladora WiFi"],
                    "200": ["Telefone IP", "Gateway SIP", "PBX", "Conversor"],
                    "204": ["Softphone", "Gateway Mobile", "Adaptador ATA", "Roteador"]
                }
            },
            "system_info": {
                "version": "2.0.0",
                "last_updated": "",
                "admin_contact": ""
            }
        }
    
    def load_config(self):
        """Carrega configurações do arquivo"""
        logging.info('[CONFIG_MANAGER] Carregando configurações...')
        logging.info(f'[CONFIG_MANAGER] Arquivo de configuração: {self.config_file}')
        try:
            if os.path.exists(self.config_file):
                logging.info('[CONFIG_MANAGER] Arquivo de configuração encontrado')
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    loaded_config = json.load(f)
                    logging.info(f'[CONFIG_MANAGER] Configurações carregadas: {json.dumps(loaded_config, indent=2, ensure_ascii=False)}')
                    # Merge com configurações padrão para garantir integridade
                    self._merge_config(loaded_config)
                    logging.info('[CONFIG_MANAGER] ✅ Configurações mescladas com sucesso')
            else:
                logging.warning(f'[CONFIG_MANAGER] ⚠️ Arquivo {self.config_file} não existe, usando configurações padrão')
        except Exception as e:
            logging.error(f'[CONFIG_MANAGER] ❌ Erro ao carregar configurações: {e}. Usando configurações padrão.')
            logging.error('[CONFIG_MANAGER] Stack trace:', exc_info=True)
    
    def _merge_config(self, loaded_config):
        """Mescla configurações carregadas com as padrão"""
        def deep_merge(default, loaded):
            for key, value in loaded.items():
                if key in default:
                    if isinstance(default[key], dict) and isinstance(value, dict):
                        deep_merge(default[key], value)
                    else:
                        default[key] = value
                else:
                    default[key] = value
        
        deep_merge(self.config, loaded_config)
    
    def save_config(self):
        """Salva configurações no arquivo"""
        logging.info('[CONFIG_MANAGER] ========== SALVANDO CONFIGURAÇÕES ==========')
        try:
            with self.config_lock:
                # Atualiza timestamp
                from datetime import datetime
                self.config['system_info']['last_updated'] = datetime.now().isoformat()
                logging.info(f'[CONFIG_MANAGER] Timestamp atualizado: {self.config["system_info"]["last_updated"]}')
                
                logging.info(f'[CONFIG_MANAGER] Arquivo de destino: {self.config_file}')
                logging.info(f'[CONFIG_MANAGER] Configuração a salvar: {json.dumps(self.config, indent=2, ensure_ascii=False)}')
                
                # Verificar se diretório existe
                config_dir = os.path.dirname(self.config_file)
                if not os.path.exists(config_dir):
                    logging.warning(f'[CONFIG_MANAGER] Diretório {config_dir} não existe, criando...')
                    os.makedirs(config_dir, exist_ok=True)
                
                with open(self.config_file, 'w', encoding='utf-8') as f:
                    json.dump(self.config, f, indent=4, ensure_ascii=False)
                
                # Verificar se arquivo foi salvo
                if os.path.exists(self.config_file):
                    file_size = os.path.getsize(self.config_file)
                    logging.info(f'[CONFIG_MANAGER] ✅ Arquivo salvo com sucesso! Tamanho: {file_size} bytes')
                else:
                    logging.error('[CONFIG_MANAGER] ❌ Arquivo não foi criado!')
                    return False
                
                return True
        except Exception as e:
            logging.error(f'[CONFIG_MANAGER] ❌ Erro ao salvar configurações: {e}')
            logging.error('[CONFIG_MANAGER] Stack trace:', exc_info=True)
            return False
    
    def get_config(self, section=None):
        """Obtém configurações (toda ou de uma seção específica)"""
        with self.config_lock:
            if section:
                return self.config.get(section, {})
            return self.config.copy()
    
    def update_config(self, section, key, value):
        """Atualiza uma configuração específica"""
        try:
            with self.config_lock:
                if section not in self.config:
                    self.config[section] = {}
                self.config[section][key] = value
                return self.save_config()
        except Exception as e:
            print(f"Erro ao atualizar configuração: {e}")
            return False
    
    def update_section(self, section, data):
        """Atualiza uma seção inteira de configurações"""
        logging.info(f'[CONFIG_MANAGER] Atualizando seção: {section}')
        logging.info(f'[CONFIG_MANAGER] Dados da seção: {data}')
        try:
            with self.config_lock:
                if section in self.config:
                    logging.info(f'[CONFIG_MANAGER] Seção {section} existe, atualizando...')
                    logging.info(f'[CONFIG_MANAGER] Valores antigos: {self.config[section]}')
                    self.config[section].update(data)
                    logging.info(f'[CONFIG_MANAGER] Valores novos: {self.config[section]}')
                else:
                    logging.info(f'[CONFIG_MANAGER] Seção {section} não existe, criando...')
                    self.config[section] = data
                
                result = self.save_config()
                if result:
                    logging.info(f'[CONFIG_MANAGER] ✅ Seção {section} salva com sucesso')
                else:
                    logging.error(f'[CONFIG_MANAGER] ❌ Falha ao salvar seção {section}')
                return result
        except Exception as e:
            logging.error(f'[CONFIG_MANAGER] ❌ Erro ao atualizar seção {section}: {e}')
            logging.error('[CONFIG_MANAGER] Stack trace:', exc_info=True)
            return False
    
    def get_ping_interval(self, vlan):
        """Obtém intervalo de ping para uma VLAN específica"""
        return self.config['ping_intervals'].get(f'vlan_{vlan}', 10)
    
    def get_active_vlans(self):
        """Obtém lista de VLANs ativas"""
        return self.config['vlans']['active_vlans']
    
    def get_vlan_description(self, vlan):
        """Obtém descrição de uma VLAN"""
        return self.config['vlans']['vlan_descriptions'].get(str(vlan), f'VLAN {vlan}')
    
    def get_device_types(self, vlan):
        """Obtém tipos de dispositivos para uma VLAN específica"""
        return self.config['vlans']['device_types'].get(str(vlan), [])
    
    def add_device_type(self, vlan, device_type):
        """Adiciona um novo tipo de dispositivo para uma VLAN"""
        try:
            with self.config_lock:
                vlan_str = str(vlan)
                if 'device_types' not in self.config['vlans']:
                    self.config['vlans']['device_types'] = {}
                
                if vlan_str not in self.config['vlans']['device_types']:
                    self.config['vlans']['device_types'][vlan_str] = []
                
                if device_type not in self.config['vlans']['device_types'][vlan_str]:
                    self.config['vlans']['device_types'][vlan_str].append(device_type)
                    return self.save_config()
                
                return True  # Tipo já existe
        except Exception as e:
            print(f"Erro ao adicionar tipo de dispositivo: {e}")
            return False
    
    def remove_device_type(self, vlan, device_type):
        """Remove um tipo de dispositivo de uma VLAN"""
        try:
            with self.config_lock:
                vlan_str = str(vlan)
                if (vlan_str in self.config['vlans']['device_types'] and 
                    device_type in self.config['vlans']['device_types'][vlan_str]):
                    self.config['vlans']['device_types'][vlan_str].remove(device_type)
                    return self.save_config()
                return True
        except Exception as e:
            print(f"Erro ao remover tipo de dispositivo: {e}")
            return False
    
    def reset_to_defaults(self):
        """Reseta configurações para os valores padrão"""
        with self.config_lock:
            self.config = self._load_default_config()
            return self.save_config()

# Instância global do gerenciador de configurações
config_manager = ConfigManager()