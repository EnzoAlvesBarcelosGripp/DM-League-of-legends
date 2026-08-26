import os
import re
import json
import gzip
import logging
import pandas as pd
from datetime import datetime, timezone
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError
from dotenv import load_dotenv

SRC_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_DIR = os.path.join(SRC_DIR, "05_Load_final")

load_dotenv() # estava causando conflito .env.example

class dim_timeError(Exception):
    """Classe base para erros da transformação."""
    pass

def _build_time_dict(sk_time: int, target_tz: ZoneInfo) -> dict:
    """Converte um epoch (ms) em um registro de dim_time, aplicando o fuso configurado."""
    dt_utc = datetime.fromtimestamp(sk_time / 1000, tz=timezone.utc)
    dt_local = dt_utc.astimezone(target_tz)

    return {
        "sk_time": sk_time,  # mantém epoch em milissegundos
        "year": dt_local.year,
        "month": dt_local.month,
        "day": dt_local.day,
        "hour": dt_local.hour,
        "minute": dt_local.minute,
        "seconds": dt_local.second,
    }

def _collect_match_times(info_folder_path: str) -> list[dict]:
    """Extrai os timestamps de criação das partidas (gameCreation) dos JSONs de InfoMatch."""
    time_list = []
    list_dir = os.listdir(info_folder_path)

    tz_env = os.getenv("TIMEZONE")
    target_tz = ZoneInfo(tz_env)

    for json_file in list_dir:
        if not json_file.endswith(".json.gz"):
            continue

        try:
            with gzip.open(os.path.join(info_folder_path, json_file), "rt", encoding="utf-8") as f:
                json_data = json.load(f)

            game_creation = json_data.get("info", {}).get("gameCreation")

            if game_creation:
                time_list.append(_build_time_dict(game_creation, target_tz))

        except Exception as e:
            logging.error(f"Erro ao processar {json_file} (partidas): {e}")

    return time_list

def _collect_pdl_snapshot_times(pdl_folder_path: str) -> list[dict]:
    """Extrai os timestamps de coleta dos snapshots de PDL, a partir do nome do arquivo.
    Usa a MESMA lógica de conversão que fct_pdl.py, pra garantir que o sk_time bata exatamente."""
    time_list = []

    if not pdl_folder_path or not os.path.isdir(pdl_folder_path):
        logging.warning(f"Pasta de snapshots de PDL não encontrada ou não informada: {pdl_folder_path}")
        return time_list

    tz_env = os.getenv("TIMEZONE")
    target_tz = ZoneInfo(tz_env)

    for json_file in os.listdir(pdl_folder_path):
        if not json_file.endswith(".json.gz"):
            continue

        filename_clean = json_file.replace(".json.gz", "")
        parts = filename_clean.rsplit("_", 2)

        if len(parts) != 3:
            continue

        try:
            timestamp_str = f"{parts[1]}_{parts[2]}"  # Ex: "20240813_144900"
            dt_obj = datetime.strptime(timestamp_str, "%Y%m%d_%H%M%S")
            sk_time_file = int(dt_obj.timestamp() * 1000)

            time_list.append(_build_time_dict(sk_time_file, target_tz))

        except Exception as e:
            logging.error(f"Erro ao processar {json_file} (PDL): {e}")

    return time_list

def transform_dim_time(info_folder_path: str, pdl_folder_path: str = None) -> pd.DataFrame:
    """Lê os JSONs de InfoMatch (partidas) e de snapshots de PDL, e gera a tabela dimensional Dim_time
    cobrindo todos os timestamps usados como sk_time em qualquer tabela fato do modelo."""

    tz_env = os.getenv("TIMEZONE")
    if not tz_env:
        raise dim_timeError("A variável de ambiente TIMEZONE não está definida no .env.")
    try:
        ZoneInfo(tz_env)
    except ZoneInfoNotFoundError as e:
        raise dim_timeError(f"Fuso horário inválido configurado na variável TIMEZONE: '{tz_env}'. Informe uma string IANA válida (ex: 'America/Sao_Paulo'): {e}")

    try:
        time_list = _collect_match_times(info_folder_path)
        time_list += _collect_pdl_snapshot_times(pdl_folder_path)

        df_time = pd.DataFrame(time_list)

        # Remove duplicatas: várias partidas/snapshots podem compartilhar o mesmo sk_time
        # (ex: vários jogadores coletados no mesmo lote de PDL) — dim_time precisa de 1 linha por sk_time.
        df_time = df_time.drop_duplicates(subset=["sk_time"], keep="first").reset_index(drop=True)

        path_final = os.path.join(OUTPUT_DIR, "dim_time.csv")
        os.makedirs(os.path.dirname(path_final), exist_ok=True)
        df_time.to_csv(path_final, index=False)

        return df_time

    except Exception as e:
        logging.error(f'Erro ao transformar dados de tempo: {e}')
        raise dim_timeError(f'Erro ao transformar dados de tempo: {e}')