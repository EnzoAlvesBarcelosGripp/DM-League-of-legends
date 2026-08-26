import json
import os
import logging
import gzip
from Static import DataDragon,DataDragonError

def save_json(data: dict | list, folder_path: str, filename: str) -> None:
    """
    Salva os dados retirados do endpoint da Riot Games em um arquivo JSON.
    """
    os.makedirs(folder_path, exist_ok=True)
    file_path = os.path.join(folder_path, filename)
    
    with gzip.open(file_path, 'wt', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)    

    logging.info(f"Arquivo JSON salvo em: {file_path}")

def get_game_versions_from_matches(info_folder_path: str) -> list[str]:
    """
    Lê os arquivos JSONs de partidas em InfoMatch e extrai as versões únicas.
    """
    Versions = []

    if not os.path.exists(info_folder_path):
        logging.error(f'Pasta {info_folder_path} não foi encontrada.')
        raise DataDragonError(f'Falha ao procurar a pasta {info_folder_path}.')

    # os.listdir retorna uma lista com os nomes de todos os arquivos em um path
    for file_name in os.listdir(info_folder_path):
        # Passamos a buscar pelos arquivos comprimidos
        if file_name.endswith('.json.gz'):
            file_path = os.path.join(info_folder_path,file_name)
            try:
                # Usamos gzip.open em modo leitura de texto ('rt')
                with gzip.open(file_path, 'rt', encoding='utf-8') as f:
                    data = json.load(f)

                    # Acessa o 'gameVersion' da partida, dentro do Nó 'Info'
                    game_version = data.get("info", {}).get("gameVersion")
                    if game_version:
                        patch_base = ".".join(game_version.split(".")[:2])
                        Versions.append(patch_base)
                    if game_version:
                        Versions.append(game_version)
            except Exception as e:
                logging.error(f"Erro ao ler o arquivo {file_name}.")
                raise Exception(f'Falha ao ler arquivo {file_name}: {e} ')

    # Usa set para retirar as duplicadas, set são list sem valores duplicados
    return list(set(Versions)) 


def download_static_data_for_versions(load_dir: str, info_folder_path: str) -> None:
    """
    Extrai do Data Dragon apenas os dados estáticos do ÚLTIMO patch presente nas partidas.
    """
    # Pega as versões únicas das partidas extraídas
    game_versions = get_game_versions_from_matches(info_folder_path)

    if not game_versions:
        logging.error('Nenhuma versão de partida encontrada para processar dados estáticos.')
        raise DataDragonError('Nenhuma versão de partida encontrada para processar dados estáticos.')

    dragon = DataDragon()
    try:
        # A lista do Data Dragon já vem ordenada do patch MAIS NOVO para o MAIS ANTIGO
        dragon_versions = dragon.get_list_versions()
    except DataDragonError as e:
        logging.error(f'Falha ao obter lista de versões: {e}')
        raise DataDragonError(f'Falha ao obter lista de versões, endpoint {dragon.url}/api/versions.json')

    # Extrai apenas os prefixos "XX.YY" das nossas partidas (ex: "14.16")
    unique_patches = {
        '.'.join(each_game_version.split('.')[:2])
        for each_game_version in game_versions
    }

    # Como a lista da Riot é decrescente, o primeiro match que encontrarmos será o MAIS RECENTE
    latest_matching_version = None
    for patch_ddragon in dragon_versions:
        # Extrai a base do patch do Data Dragon (ex: "14.16.1" vira "14.16")
        base_patch = '.'.join(patch_ddragon.split('.')[:2])
        if base_patch in unique_patches:
            latest_matching_version = patch_ddragon
            break # Achou o mais recente? Para o loop!

    if latest_matching_version:
        logging.info(f'Baixando dados estáticos apenas para o patch mais recente: {latest_matching_version}')
        
        # Seta a versão no objeto do Data Dragon
        dragon.set_version(latest_matching_version)

        # Pasta alvo agora é direto na raiz do DataDragon
        target_folder = os.path.join(load_dir, "DataDragon")

        try:
            # Salva os arquivos com o patch no nome
            champions = dragon.get_champion_data()
            save_json(champions, target_folder, f'champion_{latest_matching_version}.json.gz')

            summoners = dragon.get_summoner_spell_data()
            save_json(summoners, target_folder, f'summoner_{latest_matching_version}.json.gz')

            runes = dragon.get_runes_reforged_data()
            save_json(runes, target_folder, f'runesReforged_{latest_matching_version}.json.gz')

        except DataDragonError as e:
            logging.error(f"Erro ao baixar dados para a versão {latest_matching_version}: {e}")
            raise DataDragonError(f'Erro ao baixar dados para a versão {latest_matching_version}')
    else:
        logging.warning("Nenhuma versão compatível encontrada no Data Dragon para as partidas atuais.")  