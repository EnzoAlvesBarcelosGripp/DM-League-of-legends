import logging
import os
import json
import gzip
import pandas as pd
from datetime import datetime
from Endpoints import RiotAPIClient, RiotAPIError
from Static import  DataDragonError
from extract_static_infos import download_static_data_for_versions

# path para a raiz do projeto
SRC_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# Criação dos path para o RAW data
LOAD_DIR = os.path.join(SRC_DIR, "02_Load")
# Caminho pra dim_time.csv gerada pela etapa de transformação (mesma convenção usada em dim_time.py)
DIM_TIME_PATH = os.path.join(SRC_DIR, "05_Load_final", "dim_time.csv")


def save_json(data: dict | list, folder_path: str, filename: str) -> None:
    """
    Salva os dados retirados do endpoint da Riot Games em um arquivo JSON.
    """
    os.makedirs(folder_path, exist_ok=True)
    file_path = os.path.join(folder_path, filename)
    
    with gzip.open(file_path, 'wt', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)    

    logging.info(f"Arquivo JSON salvo em: {file_path}")


def get_last_known_match_time(dim_time_path: str) -> int | None:
    """
    Lê o maior sk_time (epoch em milissegundos) já processado em execuções anteriores,
    a partir do dim_time.csv gerado pela etapa de transformação (ciclo Extract -> Transform -> Load).
    Retorna None se o arquivo ainda não existir ou estiver vazio (primeira execução do pipeline),
    caso em que a extração busca o histórico completo, limitada pelo COUNT.
    """
    if not os.path.exists(dim_time_path):
        logging.info("dim_time.csv ainda não existe. Tratando como primeira execução (sem start_time).")
        return None

    try:
        df_time = pd.read_csv(dim_time_path)
        if df_time.empty or "sk_time" not in df_time.columns:
            return None
        return int(df_time["sk_time"].max())
    except Exception as e:
        logging.warning(f"Não foi possível ler dim_time.csv para determinar o último timestamp conhecido: {e}. Tratando como primeira execução.")
        return None


def make_logging() -> None:
    LOGS_DIR = os.path.join(SRC_DIR,'Logs')
    os.makedirs(LOGS_DIR,exist_ok=True)
    # Definição do nome do arquivo .log
    timestamp_execution = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_filepath = os.path.join(LOGS_DIR,f'pipeline_{timestamp_execution}.log')
    
    logging.basicConfig(
        level= logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y%m%d_%H%M%S',
        handlers=[
            logging.FileHandler(log_filepath, encoding='utf-8'),
            logging.StreamHandler()
        ])
    return None


def main():
    make_logging()

    client = RiotAPIClient()  # já dá load_dotenv() aqui dentro, então os.getenv("COUNT") abaixo já enxerga o .env
    
    try:
        puuid = client.get_puuid_by_gamename_tagline()
    except RiotAPIError as e:
        logging.critical(f"Falha ao obter PUUID, encerrando pipeline: {e}")
        return
    try:
        # Extração de dados do endpoint League-V4 usando o PUUID
        league_data = client.get_league_entries_by_puuid(puuid)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        league_folder = os.path.join(LOAD_DIR, "League-V4")
        save_json(league_data, league_folder, f"{puuid}_{timestamp}.json.gz")
    except RiotAPIError as e:
        logging.error(f'falha ao extrair liga, pulando etapa: {e}')

    match_ids = []
    try:
        # Determina a partir de quando buscar: só partidas jogadas depois da última já conhecida,
        # evitando reprocessar/sobrepor partidas de execuções anteriores.
        count = int(os.getenv("COUNT", 120))
        last_sk_time_ms = get_last_known_match_time(DIM_TIME_PATH)

        start_time_seconds = None
        if last_sk_time_ms is not None:
            start_time_seconds = (last_sk_time_ms // 1000) + 1  # ms -> s, +1 exclui a própria partida-limite
            logging.info(f"Execução incremental: buscando partidas após {start_time_seconds} (epoch s), limite de {count}.")
        else:
            logging.info(f"Primeira execução (ou dim_time ausente): buscando as {count} partidas mais recentes.")

        # Extração de dados do endpoint Match-V5 usando o PUUID
        match_ids = client.get_match_ids_by_puuid(puuid, start_time=start_time_seconds, count=count)
        logging.info(f"{len(match_ids)} partida(s) nova(s) encontrada(s) para processar.")

        list_folder = os.path.join(LOAD_DIR, "Match-V5", "listMatchId")
        save_json(match_ids, list_folder, f"{puuid}_matches.json.gz")
    except RiotAPIError as e:
        logging.error(f'falha ao extrair dados da partida, pulando etapa: {e}')


    # loop partidas
    for i, match_id in enumerate(match_ids, start=1):
        # Extração de informações detalhadas da partida e do timeline
        try:
            path_info = os.path.join(LOAD_DIR, "Match-V5", "InfoMatch")
            path_timeline = os.path.join(LOAD_DIR, "Match-V5", "TimelineMatch")

            # Verifica se os arquivos já existem antes de salvar
            if os.path.exists(os.path.join(path_info,f"{match_id}_info.json.gz")):
                    logging.info(f"Informações da partida {match_id} já existem. Pulando a extração.")
            else:
                # Extração de informações detalhadas da partida e do timeline 
                info = client.get_match_info_by_matchid(match_id)
                save_json(info, path_info,f"{match_id}_info.json.gz")
                logging.info(f"[{i}/{len(match_ids)}] Processando partida: {match_id}")

            if os.path.exists(os.path.join(path_timeline,f"{match_id}_timeline.json.gz")):
                logging.info(f"Timeline da partida {match_id} já existe. Pulando a extração.")
            else:
               # Extração do timeline completa da partida para depois filtrar até o minuto 15)
                timeline = client.extract_early_game_timeline(match_id, max_minute=15)
                save_json(timeline, path_timeline,f"{match_id}_timeline.json.gz")
                logging.info(f"[{i}/{len(match_ids)}] Processando partida: {match_id}")

        except RiotAPIError as e:
            logging.error(f"Erro ao obter informações da partida {match_id}: {e} | Tentativa: {i} de {len(match_ids)}")
            continue

    # Dados Estáticos
    dragon_folder = os.path.join(LOAD_DIR, "DataDragon")
    try:
        versions = download_static_data_for_versions(LOAD_DIR,path_info)
        logging.info("Extração completa com sucesso!") 
    except DataDragonError as e:
        logging.error(f'Falha ao extrair lista de versões do Data Dragon: {e}')

    return
    
if __name__ == "__main__":
    main()