-- 1. CRIAÇÃO DE SCHEMA
CREATE SCHEMA IF NOT EXISTS dw_riot;
SET search_path TO dw_riot, public;

-- 2. TABELAS DIMENSIONAIS

-- Dimensão Tempo
CREATE TABLE IF NOT EXISTS dim_time (
    sk_time BIGINT PRIMARY KEY, -- Epoch timestamp em milissegundos
    "year" INT NOT NULL,
    "month" INT NOT NULL CHECK (month BETWEEN 1 AND 12),
    "day" INT NOT NULL CHECK (day BETWEEN 1 AND 31),
    "hour" INT NOT NULL CHECK (hour BETWEEN 0 AND 23),
    "minute" INT NOT NULL CHECK (minute BETWEEN 0 AND 59),
    "seconds" INT NOT NULL CHECK (seconds BETWEEN 0 AND 59)
);

-- Dimensão Jogador (Totalmente sincronizada com o Python)
CREATE TABLE IF NOT EXISTS dim_player (
    sk_player INT PRIMARY KEY,
    puuid VARCHAR(100) NOT NULL UNIQUE,
    game_name VARCHAR(100),
    tag_line VARCHAR(50),
    region VARCHAR(20),
    profile_iconId INT,
    is_main_account BOOLEAN NOT NULL DEFAULT FALSE
);

-- Dimensão Campeão (Atualizada para receber tags e imagens)
CREATE TABLE IF NOT EXISTS dim_champion (
    sk_champion INT PRIMARY KEY,
    champion_key INT NOT NULL UNIQUE,
    championName VARCHAR(100) NOT NULL,
    image_full VARCHAR(150),
    champion_tags VARCHAR(150)
);

-- Dimensão Feitiços de Invocador (Summoner Spells)
CREATE TABLE IF NOT EXISTS dim_summoner (
    sk_summonerspell INT PRIMARY KEY,
    id INT NOT NULL UNIQUE,
    "full" VARCHAR(150)
);

-- Dimensão Runas / Estilos de Runas
CREATE TABLE IF NOT EXISTS dim_stylePerks (
    sk_perks INT PRIMARY KEY,
    style_id INT NOT NULL,
    perk_id INT NOT NULL,
    style_icon VARCHAR(150),
    perk_icon VARCHAR(150),
    CONSTRAINT uk_style_perk UNIQUE (style_id, perk_id)
);

-- Dimensão Informações da Partida (Atualizada com flags de surrender e versão do jogo)
CREATE TABLE IF NOT EXISTS dim_info_match (
    sk_info_match INT PRIMARY KEY,
    match_id VARCHAR(50) NOT NULL UNIQUE,
    game_duration INT NOT NULL CHECK (game_duration >= 0),
    game_version VARCHAR(50),
    platform_id VARCHAR(20),
    game_ended_in_surrender BOOLEAN,
    game_ended_in_early_surrender BOOLEAN
);

-- 3. TABELAS FATO

-- Fato 1: Desempenho do Participante na Partida
CREATE TABLE IF NOT EXISTS fct_match_participant (
    -- Chaves Estrangeiras / Estrutura
    sk_info_match INT NOT NULL REFERENCES dim_info_match(sk_info_match),
    sk_time BIGINT NOT NULL REFERENCES dim_time(sk_time),
    gameCreation BIGINT NOT NULL,
    sk_player INT NOT NULL REFERENCES dim_player(sk_player),
    sk_champion INT NOT NULL REFERENCES dim_champion(sk_champion),
    sk_primary_style INT NOT NULL REFERENCES dim_stylePerks(sk_perks),
    sk_sub_style INT NOT NULL REFERENCES dim_stylePerks(sk_perks),
    sk_sub_style_2 INT NOT NULL REFERENCES dim_stylePerks(sk_perks),
    sk_summoner1 INT NOT NULL REFERENCES dim_summoner(sk_summonerspell),
    sk_summoner2 INT NOT NULL REFERENCES dim_summoner(sk_summonerspell),
    teamId INT NOT NULL CHECK (teamId IN (100, 200)),
    
    -- Metadados e Resultado
    win BOOLEAN NOT NULL,
    summonerLevel INT NOT NULL,

    -- Métricas de Combate Brutas
    kills INT NOT NULL CHECK (kills >= 0),
    deaths INT NOT NULL CHECK (deaths >= 0),
    assists INT NOT NULL CHECK (assists >= 0),
    goldEarned INT NOT NULL CHECK (goldEarned >= 0),
    damageDealtToTurrets INT NOT NULL CHECK (damageDealtToTurrets >= 0),
    detectorWardsPlaced INT NOT NULL CHECK (detectorWardsPlaced >= 0),

    -- Múltiplos Abates e Eventos
    doubleKills INT NOT NULL CHECK (doubleKills >= 0),
    tripleKills INT NOT NULL CHECK (tripleKills >= 0),
    quadraKills INT NOT NULL CHECK (quadraKills >= 0),
    pentaKills INT NOT NULL CHECK (pentaKills >= 0),
    firstBloodAssist BOOLEAN NOT NULL,
    firstBloodKill BOOLEAN NOT NULL,
    firstTowerKill BOOLEAN NOT NULL,

    -- Tipos de Dano e Suporte
    magicDamageDealtToChampions INT NOT NULL CHECK (magicDamageDealtToChampions >= 0),
    magicDamageTaken INT NOT NULL CHECK (magicDamageTaken >= 0),
    physicalDamageDealtToChampions INT NOT NULL CHECK (physicalDamageDealtToChampions >= 0),
    physicalDamageTaken INT NOT NULL CHECK (physicalDamageTaken >= 0),
    trueDamageDealtToChampions INT NOT NULL CHECK (trueDamageDealtToChampions >= 0),
    trueDamageTaken INT NOT NULL CHECK (trueDamageTaken >= 0),
    totalDamageDealtToChampions INT NOT NULL CHECK (totalDamageDealtToChampions >= 0),
    totalDamageTaken INT NOT NULL CHECK (totalDamageTaken >= 0),
    totalDamageShieldedOnTeammates INT NOT NULL CHECK (totalDamageShieldedOnTeammates >= 0),
    totalHealsOnTeammates INT NOT NULL CHECK (totalHealsOnTeammates >= 0),
    totalTimeSpentDead INT NOT NULL CHECK (totalTimeSpentDead >= 0),

    -- Challenges / Visão
    controlWardTimeCoverageInRiverOrEnemyHalf NUMERIC(5,4),
    controlWardsPlaced INT NOT NULL CHECK (controlWardsPlaced >= 0),
    wardTakedowns INT NOT NULL CHECK (wardTakedowns >= 0),
    soloKills INT NOT NULL CHECK (soloKills >= 0),
    junglerKillsEarlyJungle INT NOT NULL CHECK (junglerKillsEarlyJungle >= 0),
    killsOnLanersEarlyJungleAsJungler INT NOT NULL CHECK (killsOnLanersEarlyJungleAsJungler >= 0),
    epicMonsterSteals INT NOT NULL CHECK (epicMonsterSteals >= 0),

    -- Métricas Derivadas
    kda NUMERIC(6,2) NOT NULL CHECK (kda >= 0),
    damagePerMinute NUMERIC(8,2) NOT NULL CHECK (damagePerMinute >= 0),
    goldPerMinute NUMERIC(8,2) NOT NULL CHECK (goldPerMinute >= 0),
    csPerMinute NUMERIC(8,2) NOT NULL CHECK (csPerMinute >= 0),
    killParticipation NUMERIC(5,4) NOT NULL CHECK (killParticipation BETWEEN 0 AND 1),
    teamDamagePercentage NUMERIC(5,4) NOT NULL CHECK (teamDamagePercentage BETWEEN 0 AND 1),

    -- Vantagens da Fase de Rotas (15 min)
    laningPhaseGoldAdvantage NUMERIC(10,2),
    laningPhaseExpAdvantage NUMERIC(10,2),
    laningPhaseCsAdvantage NUMERIC(10,2),

    CONSTRAINT pk_fct_match_participant PRIMARY KEY (sk_info_match, sk_player)
);

-- Fato 2: Acompanhamento temporal de pontos 
CREATE TABLE IF NOT EXISTS fct_pdl_hist (
    sk_player INT NOT NULL REFERENCES dim_player(sk_player),
    sk_time BIGINT NOT NULL REFERENCES dim_time(sk_time),
    tier VARCHAR(20) NOT NULL CHECK (tier IN ('IRON','BRONZE','SILVER','GOLD','PLATINUM','EMERALD','DIAMOND','MASTER','GRANDMASTER','CHALLENGER')),
    "rank" VARCHAR(5) NOT NULL CHECK (rank IN ('I','II','III','IV')),
    leaguePoints INT NOT NULL CHECK (leaguePoints >= 0),
    wins INT NOT NULL CHECK (wins >= 0),
    losses INT NOT NULL CHECK (losses >= 0),
    delta_pdl INT NOT NULL DEFAULT 0,

    CONSTRAINT pk_fct_pdl_hist PRIMARY KEY (sk_player, sk_time)
);

CREATE INDEX IF NOT EXISTS idx_fct_participant_player ON fct_match_participant(sk_player);
CREATE INDEX IF NOT EXISTS idx_fct_participant_champion ON fct_match_participant(sk_champion);
CREATE INDEX IF NOT EXISTS idx_fct_participant_time ON fct_match_participant(sk_time);
CREATE INDEX IF NOT EXISTS idx_fct_pdl_hist_time ON fct_pdl_hist(sk_time);