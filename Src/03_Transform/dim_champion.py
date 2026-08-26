import os
import gzip
import json
import logging
import pandas as pd

SRC_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_DIR = os.path.join(SRC_DIR, "05_Load_final")

class Dim_championError(Exception):
    """Classe base para erros da transformação da Dim_champion."""
    pass

def _get_latest_champion_file_and_version(datadragon_dir: str) -> tuple[str, str]:
    """
    Procura os arquivos 'champion_{patch}.json.gz' no diretório e retorna
    o caminho do arquivo mais recente junto com a string da versão.
    """
    # Filtra apenas os arquivos de campeões
    files = [f for f in os.listdir(datadragon_dir) if f.startswith("champion_") and f.endswith(".json.gz")]
    
    if not files:
        raise FileNotFoundError(f"Nenhum arquivo champion_*.json.gz encontrado em {datadragon_dir}")

    def parse_version(filename: str):
        # Limpa o texto para extrair só os números: champion_14.16.1.json.gz -> 14.16.1
        version_str = filename.replace("champion_", "").replace(".json.gz", "")
        try:
            return tuple(map(int, version_str.split('.')))
        except ValueError:
            return (0, 0, 0)

    # Pega o arquivo com a maior versão
    latest_file = max(files, key=parse_version)
    
    # Extrai a versão final limpa para usarmos na URL
    latest_version = latest_file.replace("champion_", "").replace(".json.gz", "")
    
    return os.path.join(datadragon_dir, latest_file), latest_version


def transform_dim_champion(datadragon_dir: str) -> pd.DataFrame:
    """Lê o arquivo champion mais recente e gera a dim_champion.csv."""
    json_path = None
    try:
        # Recebe o caminho do arquivo e a versão (ex: '14.16.1')
        json_path, latest_version = _get_latest_champion_file_and_version(datadragon_dir)

        with gzip.open(json_path, "rt", encoding="utf-8") as f:
            data_json = json.load(f)

        logging.info(f"Dim_champion lendo dados da versão mais recente: {latest_version}")

        champion_list = []
        i = 1

        for nome_campeao, detail in data_json.get("data", {}).items():
            # Pega o nome do arquivo da imagem (ex: 'Aatrox.png')
            img_filename = detail.get("image", {}).get("full", "")
            
            # Monta a URL completa usando a variável latest_version
            img_url = f"https://ddragon.leagueoflegends.com/cdn/{latest_version}/img/champion/{img_filename}" if img_filename else ""

            campeao_dict = {
                "sk_champion": i,  
                "champion_key": int(detail.get("key", 0)),  
                "championName": detail.get("name", ""),  
                "image_full": img_url,  # Agora recebe a URL pronta
                "champion_tags": ", ".join(detail.get("tags", [])),  
            }

            champion_list.append(campeao_dict)
            i += 1

        logging.info(f"Extração das informações do arquivo {json_path} concluída com sucesso.")

        df_champions = pd.DataFrame(champion_list)

        # Padronizado para dim_champion.csv
        final_path = os.path.join(OUTPUT_DIR, "dim_champion.csv")
        os.makedirs(os.path.dirname(final_path), exist_ok=True)
        df_champions.to_csv(final_path, index=False)

        return df_champions
        
    except Exception as e:
        msg_path = json_path if json_path else datadragon_dir
        logging.error(f"Erro ao extrair informação do diretório/arquivo {msg_path}: {e}")
        raise Dim_championError(f"Erro ao extrair informação do diretório/arquivo {msg_path}: {e}")