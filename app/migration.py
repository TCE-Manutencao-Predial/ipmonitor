import os
import shutil
import logging
from pathlib import Path

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Diretório de dados centralizado
DATA_DIR = '/var/softwaresTCE/dados/ipmonitor'

def ensure_data_directory():
    """Garante que o diretório de dados existe"""
    try:
        os.makedirs(DATA_DIR, exist_ok=True)
        logging.info(f"[MIGRATION] Diretório de dados garantido: {DATA_DIR}")
        return True
    except Exception as e:
        logging.error(f"[MIGRATION] Erro ao criar diretório de dados: {e}")
        return False

def migrate_data_files():
    """
    Migra arquivos de dados antigos para o novo diretório centralizado.
    Executa apenas uma vez na inicialização se detectar arquivos antigos.
    """
    # Arquivos que devem ser migrados
    files_to_migrate = [
        'app_config.json',
        'ip_devices.json',
        'ips_list.json'
    ]
    
    # Verificar se já foi migrado (se os arquivos já estão no novo local)
    already_migrated = all(
        os.path.exists(os.path.join(DATA_DIR, f)) 
        for f in ['app_config.json', 'ip_devices.json']
    )
    
    if already_migrated:
        logging.info("[MIGRATION] Arquivos já estão no diretório centralizado. Migração não necessária.")
        return True
    
    # Garantir que o diretório existe
    if not ensure_data_directory():
        logging.error("[MIGRATION] Não foi possível criar o diretório de dados.")
        return False
    
    migrated_count = 0
    
    # Obter diretório raiz do projeto (um nível acima de app/)
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    logging.info(f"[MIGRATION] Iniciando migração de arquivos do diretório: {project_root}")
    
    for filename in files_to_migrate:
        old_path = os.path.join(project_root, filename)
        new_path = os.path.join(DATA_DIR, filename)
        
        try:
            # Se o arquivo existe na localização antiga
            if os.path.exists(old_path):
                # Se não existe no novo local, mover
                if not os.path.exists(new_path):
                    shutil.copy2(old_path, new_path)
                    logging.info(f"[MIGRATION] ✓ Copiado: {filename} -> {new_path}")
                    migrated_count += 1
                    
                    # Após copiar com sucesso, renomear o arquivo antigo para .old
                    backup_path = old_path + '.old'
                    try:
                        os.rename(old_path, backup_path)
                        logging.info(f"[MIGRATION] ✓ Backup criado: {backup_path}")
                    except Exception as e:
                        logging.warning(f"[MIGRATION] Não foi possível criar backup de {filename}: {e}")
                else:
                    logging.info(f"[MIGRATION] ○ Arquivo já existe no destino: {filename}")
            else:
                logging.info(f"[MIGRATION] ○ Arquivo não encontrado na origem: {filename}")
                
        except Exception as e:
            logging.error(f"[MIGRATION] ✗ Erro ao migrar {filename}: {e}")
    
    if migrated_count > 0:
        logging.info(f"[MIGRATION] Migração concluída: {migrated_count} arquivo(s) migrado(s)")
    else:
        logging.info("[MIGRATION] Nenhum arquivo necessitou migração")
    
    return True

def get_data_file_path(filename):
    """
    Retorna o caminho completo para um arquivo de dados.
    Usa o diretório centralizado.
    """
    return os.path.join(DATA_DIR, filename)

if __name__ == '__main__':
    # Teste da migração
    print("Testando migração de dados...")
    migrate_data_files()
