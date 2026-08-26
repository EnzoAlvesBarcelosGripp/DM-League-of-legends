import os 
import gzip
import json
import logging
import pandas as pd

SRC_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_DIR = os.path.join(SRC_DIR, "05_Load_final")

class Dim_stylePerks_Error(Exception):
    """Classe base para erros da transformação da Dim_stylePerks."""
    pass

def _get_latest_runes_file_and_version(datadragon_dir: str) -> tuple[str, str]:
    """
    Procura os arquivos 'runesReforged_{patch}.json.gz' no diretório e retorna
    o caminho do arquivo mais recente junto com a string da versão.
    """
    files = [f for f in os.listdir(datadragon_dir) if f.startswith("runesReforged_") and f.endswith(".json.gz")]
    
    if not files:
        raise FileNotFoundError(f"Nenhum arquivo runesReforged_*.json.gz encontrado em {datadragon_dir}")

    def parse_version(filename: str):
        version_str = filename.replace("runesReforged_", "").replace(".json.gz", "")
        try:
            return tuple(map(int, version_str.split('.')))
        except ValueError:
            return (0, 0, 0)

    latest_file = max(files, key=parse_version)
    latest_version = latest_file.replace("runesReforged_", "").replace(".json.gz", "")
    
    return os.path.join(datadragon_dir, latest_file), latest_version


def transform_dim_stylePerks(datadragon_dir: str) -> pd.DataFrame:
    """Lê o runesReforged.json.gz da versão mais recente e gera a dim_stylePerks.csv."""
    json_path = None
    try:
        json_path, latest_version = _get_latest_runes_file_and_version(datadragon_dir)

        with gzip.open(json_path, "rt", encoding="utf-8") as f:
            json_data = json.load(f)

        logging.info(f"Dim_stylePerks lendo dados da versão mais recente: {latest_version}")

        # Json flatten - Style -> Slots -> Runes 
        df_stylePerks = pd.json_normalize(
            json_data, 
            record_path=["slots", "runes"], 
            meta=["id", "icon"], 
            meta_prefix="style_"
        )
        
        df_stylePerks = df_stylePerks.rename(columns={"id": "perk_id", "icon": "perk_icon"})

        # Ajusta caminhos das imagens para URL completa
        base_url = f"https://ddragon.leagueoflegends.com/cdn/img/"
        df_stylePerks["style_icon"] = base_url + df_stylePerks["style_icon"]
        df_stylePerks["perk_icon"] = base_url + df_stylePerks["perk_icon"]

        cols_order = ["style_id", "perk_id", "style_icon", "perk_icon"]
        df_stylePerks = df_stylePerks[cols_order]

        df_stylePerks.insert(0, "sk_perks", range(1, len(df_stylePerks) + 1))

        final_path = os.path.join(OUTPUT_DIR, "dim_stylePerks.csv")
        os.makedirs(os.path.dirname(final_path), exist_ok=True)
        df_stylePerks.to_csv(final_path, index=False)
        
        logging.info(f'Extração das informações do arquivo {json_path} concluída com sucesso.')

        return df_stylePerks
    
    except Exception as e:
        msg_path = json_path if json_path else datadragon_dir
        logging.error(f'Erro ao transformar dados do stylePerks em {msg_path}: {e}')
        raise Dim_stylePerks_Error(f"Erro ao transformar dados do stylePerks em {msg_path}: {e}")