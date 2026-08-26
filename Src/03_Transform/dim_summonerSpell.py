import os 
import gzip
import json
import logging
import pandas as pd

SRC_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_DIR = os.path.join(SRC_DIR, "05_Load_final")

class Dim_summonerSpell_Error(Exception):
    """Classe base para erros da transformação da Dim_summonerSpell."""
    pass

def _get_latest_spell_file_and_version(datadragon_dir: str) -> tuple[str, str]:
    """
    Procura os arquivos 'summoner_{patch}.json.gz' no diretório e retorna
    o caminho do arquivo mais recente junto com a string da versão.
    """
    files = [f for f in os.listdir(datadragon_dir) if f.startswith("summoner_") and f.endswith(".json.gz")]
    
    if not files:
        raise FileNotFoundError(f"Nenhum arquivo summoner_*.json.gz encontrado em {datadragon_dir}")

    def parse_version(filename: str):
        version_str = filename.replace("summoner_", "").replace(".json.gz", "")
        try:
            return tuple(map(int, version_str.split('.')))
        except ValueError:
            return (0, 0, 0)

    latest_file = max(files, key=parse_version)
    latest_version = latest_file.replace("summoner_", "").replace(".json.gz", "")
    
    return os.path.join(datadragon_dir, latest_file), latest_version


def transform_dim_summonerSpell(datadragon_dir: str) -> pd.DataFrame:
    """Lê o summoner.json.gz da versão mais recente e gera a dim_summoner.csv."""
    json_path = None
    try:
        json_path, latest_version = _get_latest_spell_file_and_version(datadragon_dir)

        with gzip.open(json_path, "rt", encoding="utf-8") as f:
            json_data = json.load(f)

        logging.info(f"Dim_summoner lendo dados da versão mais recente: {latest_version}")

        summoner_list = []
        i = 1

        for name_spell, itens in json_data.get('data', {}).items():
            img_filename = itens.get('image', {}).get('full', '')
            img_url = f"https://ddragon.leagueoflegends.com/cdn/{latest_version}/img/spell/{img_filename}" if img_filename else ""

            summoner_dict = {
                "sk_summonerspell": i,
                "id": int(itens.get('key', 0)),
                "full": img_url
            }

            summoner_list.append(summoner_dict)
            i += 1

        logging.info(f'Extração das informações do arquivo {json_path} concluída com sucesso.')

        df_summoner = pd.DataFrame(summoner_list)

        final_path = os.path.join(OUTPUT_DIR, "dim_summoner.csv")
        os.makedirs(os.path.dirname(final_path), exist_ok=True)
        df_summoner.to_csv(final_path, index=False)

        return df_summoner

    except Exception as e:
        msg_path = json_path if json_path else datadragon_dir
        logging.error(f'Erro ao transformar dados do summoner spell em {msg_path}: {e}')
        raise Dim_summonerSpell_Error(f"Erro ao transformar dados do summoner spell em {msg_path}: {e}")