import os
import shutil
import logging
from pathlib import Path

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Diretório de dados centralizado
DATA_DIR = '/var/softwaresTCE/ipmonitor'

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
    Migra arquivos de dados antigos para o diretório do backend.
    No contexto de produção, esta função não faz nada pois o deploy.sh
    já cuida da migração. Mantida para compatibilidade.
    """
    # Em produção, os arquivos já estão no lugar certo via deploy.sh
    # Esta função existe apenas para compatibilidade e desenvolvimento local
    if not os.path.exists(DATA_DIR):
        logging.warning(f"[MIGRATION] Diretório {DATA_DIR} não existe. Usando diretório local.")
        return False
    
    logging.info("[MIGRATION] Usando diretório de dados: " + DATA_DIR)
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
