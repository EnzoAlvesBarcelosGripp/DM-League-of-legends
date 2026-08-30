# League of Legends Data Warehouse

Este projeto implementa uma **pipeline ETL completa** para a construção de um **Data Warehouse** de League of Legends, utilizando **PostgreSQL** para armazenamento dos dados e **Power BI** para a visualização e análise das métricas extraídas durante o processo.

A pipeline utiliza duas fontes de dados:

- **Riot Games API** — fonte de dados dinâmica, utilizada principalmente para informações de jogadores, partidas e histórico;
- **Data Dragon** — fonte de dados estáticos e versionados do jogo, utilizada para complementar as informações obtidas durante a extração.

O projeto também utiliza **Docker Compose** para provisionar e executar o banco de dados PostgreSQL e o pipeline ETL em containers.
---

# Como executar

O projeto possui dois serviços no `docker-compose`:
* postgres_riot - responsável pelo Data Warehouse
* etl_pipeline - executa as etapas do ETL

O banco possui persistência dos dados atraves de um volume (`pgdata`) Docker.

As tabelas são inciadas através do arquivo `ddl.sql` em (`05_load_final`)

1. Clone o repositório e acesso a pasta raiz

```sh
git clone https://github.com/EnzoAlvesBarcelosGripp/Teste-API-Riot.git
cd Teste-API-Riot
```

2. Gere sua API key de development

Acesse o [site oficial](https://developer.riotgames.com/) da **API Riot Games** faça login com sua conta e gere a sua `API key` 

3. Configure as váriaveis de ambiente

Remova `.example` do arquivo `.env.example`.

Configure as váriaveis, apenas um exemplo abaixo:

```text
# API
RIOT_API_KEY=RGAPI-xxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
GAME_NAME=JogadorExemplo 
TAG_LINE=BR1
COUNT=100 
TIMEZONE=America/Sao_Paulo # Fuso horário, seguindo a lista padrão IANA: exemplo: America/Sao_Paulo

# Banco de Dados
DB_USER=postgres 
DB_PASSWORD=sua_senha_segura
DB_NAME=dw_riot
DB_PORT=5432
```

4. Execute o projeto via docker-compose

```sh
docker-compose up --build
```

O docker inicia o PostgresSQL e agurda o healtcheck do banco antes da execução do **ETL**.

5. Concectar o PostgresSQL ao Power BI

Após nenhuma mensagem de erro, basta baixar o arquivo `.pbix` pelo **Power BI** e realizar a conexão com o banco com os dados postos na `.env`.

# Sobre o projeto

O objetivo deste projeto é possibilitar vizualizações personalizadas de estatísticas e metricas em uma conta específica no League of Legends, para tal: é necessário aplicar um pipeline de ETL e combinar com a vizualização dos dados.

O pipeline coleta as informações de um jogador e suas respectivas partidas, com as combinação do `GameName + Tagline` que permite conseguir a **puuid** (equivalente ao **id**) via API.

## Fluxo

O projeto é divido em 6 etapas, descrita abaixo:

```text
                         RIOT GAMES API
                               │
                               ▼
                     ┌───────────────────┐
                     │   01 - EXTRAÇÃO   │
                     │                   │
                     │ Riot API          │
                     │ Data Dragon       │
                     └─────────┬─────────┘
                               │
                               ▼
                     ┌───────────────────┐
                     │    02 - LOAD      │
                     │                   │
                     │ Dados brutos      │
                     │ JSON / GZIP       │
                     └─────────┬─────────┘
                               │
                               ▼
                     ┌───────────────────┐
                     │ 03 - TRANSFORM    │
                     │                   │
                     │ Dimensões         │
                     │ Tabelas fato      │
                     └─────────┬─────────┘
                               │
                               ▼
                     ┌───────────────────┐
                     │ 04 - VALIDAÇÃO    │
                     |                   |
                     │ Verificação de:   │
                     │ Qualidade,        │
                     │ Integridade,      │
                     │ Granularidade     │
                     └─────────┬─────────┘
                               │
                               ▼
                     ┌───────────────────┐
                     │ 05 - LOAD FINAL   │
                     │                   │
                     │ PostgreSQL        │
                     │ Data Warehouse    │
                     └─────────┬─────────┘
                               │
                               ▼
                     ┌───────────────────┐
                     │ 06 - VISUALIZAÇÃO │
                     │                   │
                     │Power BI           │
                     └───────────────────┘
```

a **arquitetura** segue o mesmo padrão do fluxo, separado pelas etapas:

```text
Docs/
│   ├── img/
│   ├── Dicionário de dad...
│   └── documentação AP...
Src/
│   ├── 01_Extraction/
│   ├── 02_Load/
│   │   ├── DataDragon/
│   │   └── Match-V5/
│   │       ├── InfoMatch/
│   │       ├── listMatchId/
│   │       └── TimelineMatch/
│   ├── 03_Transform/
│   ├── 04_Validação/
│   ├── 05_Load_final/
│   ├── 06_Vizualização/
|   └── Logs/
```

# 01-Extração

É a etapa que faz as requisições para ambas as API's e obtém os arquivos `json` retornados pelos endpoints.

A 4 arquivos python, sendo `main.py` o orquestrador que chama as classes e funções dos outros 3 arquivos. Para as informações mais detalhadas das classes, funções e dos endpoints consumidos de cada arquivo clique em [saiba mais](/Docs/Documentação%20Extração.md)

* Através do `GameName + Tagline` informado pela `.env` é obtido pelos endpoints:
    1. O `puuid` do jogador.
    2. O `SummonerId` do Jogador.
    3. Obtenção de informações gerais do estado atual da conta (total de vitórias, derrotas, ranque atual, etc).
    4. Obtenção de informações detalhadas de cada partida (o **numero de partidas** é informado via `.env`).
    5. Obtenção de certas informações minuto a minuto de cada partida.

## Tratamento/Otimizações de requisições  - Destaque

Devido ao **rate limit** da ``API key de development `` (versão totalmente gratuita) ser de **20 requests a cada 10 segundos** e **100 requests a cada 2 minutos** é uma obrigação haver um tratamento mais robusto, o tratamento que foi aplicado usa o header `Retry-after` e um sistema de N° de tentativas de `Retry-after` para evitar loops infinitos e um tempo máximo de espera aceitável. 

Pensando na segunda ou posterior vez que esta pipeline for executado, é feito sempre na primeira execução é feito uma busca no arquivo `time.csv` (em `05_Load_Final`) para verificar o valor do ultimo `sk_time`, em que `sk_time` é o **valor do timestamp (em ms - formato original)** de quando a equivalente foi criada (o ultimo valor é sempre a partida mais recente), caso tenha um valor de `sk_time` esse valor é convertido para segundos e é passado pelo parametro `start_time`, fazendo assim que o ponto de partida sejam apenas partidas que não foram requisicionadas em outras execuções e evitando que partidas entre o tempo da ultima execução e a nova sejam perdidas.

Outro tratamento dado é em relação ao numero de partidas puxads, como o endpoint [`/lol/match/v5/matches/by-puuid/{puuid}/ids`](https://developer.riotgames.com/apis#match-v5/GET_getMatchIdsByPUUID) (que retorna uma lista de **matchids**) tem um limite de 100 itens por lista, foi paginado o numero total de partidas a serem extraídas para lotes de 100, exemplo: caso esteja sendo requisicionado **120** partidas a função responsável irá fazer uma chamada extraindo as 100 primeiras partidas e depois irá fazer outro chamado para as 20 partidas.

Com a lista de `matchId` (id de todas as partidas a serem puxadas) é feito uma verificação antes de requisitar `/lol/match/v5/matches/{match_id}` e `/lol/match/v5/matches/{match_id}/timeline` para evitar requisições desnecessárias.

No momento de salvar todos os aqruivos `.json` ou `.json.gz` é feito uma verificação se o arquivo já existe dentro de `02_Load` para evitar arquivos duplicados.

---

# 02-Load (camada bruta)


E estruturada de forma que cada endpoint da **API Riot Games** fique em uma pasta diferente, as pastas funcionam como uma camada para armazenar os arquivos brutos, ajudando na otimização da extração e mantendo a informação bruta guardada.


```text
02_Load/ 
│ ├── DataDragon/ 
│     ├── champion_*.json.gz 
│     ├── runesReforged_*.json.gz 
│     └── summoner_*.json.gz 
│ ├── League-V4/ 
│     └── {puuid}.json.gz 
│ └── Match-V5/ 
    ├── InfoMatch/ 
        └── {matchid}.json.gz 
    ├── TimelineMatch/
        └── {matchid}.json.gz  
    └── listMatchId/
        └── {puuid}.json.gz 
```

# 03-Transformação

Os dados são extraídos diretamento dos arquivos brutos e direcionadas a modelagem star schema, demostrada abaixo

![Modelagem DW](/Docs/img/drawSQL-image-export-2026-08-16.webp)

## Dimensões

Foram definidas 6 dimensões:

* **dim_time** - Guarda o ``time_stamp`` (em ms) da criação da partida em ``sk_time`` e o seu equivalente em: ano, mes, dia, hora, minuto e segundo.
    * **Granularidade**: 1 para cada partida.
* **dim_player** - Guarda informações gerais de cada jogador nas partidas, como: o `puuid` de cada jogador, `game_name`, `tag_line` e uma variavel booleana para identificar o registro do jogador principal.
    * **Granularidade**: 9 para cada partida + conta principal, caso um jogador se repita (caso da conta principal que se repete em todas as partidas puxadas) o seu registro não é duplicado.
* **dim_stylePerks** - Guarda informações para identificar as runas utilizadas.
    * **Granularidade**: todas as informações retiradas do endpoint no patch da partida mais recente `/cdn/{version}/data/en_US/runesReforged.json`, na versão da partida mais recente da execução do pipeline.
* **dim_info_match** - Guarda informações gerais de cada partida, como: o `matchid` da partida, `gameduration`, `gameversion` e a servidor `plataform_id`. As partidas são salvas de forma decrescente, mais recentes são os ultimos registros.
    * **Granularidade**: 1 para cada partida.
* **dim_champions**: Guarda informações de todos os campeões, como: `champion_key`, `champion_name`, url para o icone do campeão e suas classes.
    * **Granularidade**: todas as informações retiradas do endpoint no patch da partida mais recente `/cdn/{version}/data/en_US/champion.json`, na versão da partida mais recente da execução do pipeline.
* **dim_summoner**: guarda informações para identificar os feitiços de invocador utlizados.
    * **Granularidade**: todas as informações retiradas do endpoint no patch da partida mais recente `/cdn/{version}/data/en_US/summoner.json`, na versão da partida mais recente da execução do pipeline.

## Fatos

Foram definidos 2 fatos:

* fct_match_participant: que contém metricas diversas metricas de uma partida, como: dano recebido, dano causado, tipo de dano causado, etc.
    * **Granularidade**: 10 registros para cada partida, em que todas as partidas teve ter uma conta principal.
* fct_pdl_hist: contém as informações de elo referente a conta principal.
    * **Granularidade**: 1 por execução do pipeline, registra o elo depois da ultima partida extraída.

## Fluxo da transformação

Primeiro é feito a extração das informações dos arquivos vindo do **DataDragon**, já que estes são dados estátiscos. Após é feito a extração das informações vindas das partidas (**Riot Games API**) e por fim a extração e transformação de metricas que não existem de forma direta nas fatos. Segue um exemplo visual do fluxo:

```text
Dados estáticos (DataDragon)
    │ 
    ├──► dim_champion 
    ├──► dim_stylePerks 
    └──► dim_summoner 
            │ 
            ▼ 
Dados das partidas (Riot Games API)
    │ 
    ├──► dim_time 
    ├──► dim_player 
    └──► dim_info_match 
            │ 
            ▼ 
    ┌───────────────┐ 
    │ Tabelas fato  │ 
    ├───────────────┤ 
    │ fct_match_    │ 
    │ participant   │ 
    │               │ 
    │ fct_pdl_hist  │ 
    └───────────────┘
```

Para saber todos os metodos e classes usadas clique em [saiba mais - A ser feito](/Docs/)

* **OBS:** todos os arquivos são salvos em (`05_Load_final`) em `.csv`.

# 04-Validação

Após realizado a extração e transformação dos dados brutos é preciso verificar/confirmar que eles cumpram: a **granularidade** definida das dimensões e fatos, se há consistencia dos dados, unicidade das chaves, unicidades dos `puuids`, se existe apenas uma conta principal, nas fatos é verificado se há correspondência nas dimensões. 

Apenas após passar por todas as verificações o pipeline seguirá, caso falhe em alguma é levantado o erro e cancela a execução de toda a pipeline.

Para saber cada verificação aplicada clique em [saiba mais - A ser feito](/Docs/)

# 05-Load Final (load no banco de dados)

O carregamento final é realizado em **PostgresSQL** e o é criado conforme o star schema já apresentado.

Para fazer a conexão é usado a biblioteca **sqlalchemy** que após ler as informações de conexão com o banco via `.env` é criado a **URL** de conexão com a engine se ligando ao PostgresSQL. 

Primeiro é carregado todas as tabelas das dimensões para apenas depois carregar as tabelas fatos. 

A inserção é feita de forma full load, ou seja, todos os dados do banco de dados são previamente removidos para depois realizar as inserções.

# 06-Power BI

A vizualização é estrutura em 3 páginas, a primeira é sobre informações gerais da conta principal, contém uma tabela com a evolução de elo da conta, uma tabela com os **3 campeões** mais jogados e algumas estatiscas gerais desses campeões, e 3 tabelas (geradas com a extensão `html contender`) que representam as ultimas 3 partidas da extraídas, sendo o fundo azul uma vitória e o fundo vermelho uma derrota. O gif mostra a pagina em si e algumas das interatividades entre o card e a tabela.

![Pagina 1](/Docs/img/Pagina%201.gif)

A segunda pagina é sobre informações das ultimas 3 partidas, contém graficos de permance nos primeiros 15 minutos, graficos de danos (causados e recebidos) além de outras informações gerais sobre o desempenho do jogador na partida em questão. O gif mostra o caminho interagindo com as tabelas da pagina 1 e o caminho "padrão" que leva apenas as estatisticas da ultima partida.

![Pagina 1-2](/Docs/img/pagina%201%20-%202.gif)

A terceira pagina é sobre informações do desempenho do jogador com os campeões, nela há dados aglomerados de todas as partidas com aquele campeão, há tambem cards que mudam suas estatiscas conforme a classe selecionada do campeão de forma que estatiscas que seja possível agregar dados para todos os tipos de campeões, exemplo: caso o campeão seja tanto suporte e tanque é possível ver o desempenho de ambas classes ao mudar o filtro de classe, e evita que classes opostas (suporte e assasinos) tenham que ver as mesmas estatisticas. O gif demonstra o caminho até a terceira pagina e como funciona os cards iterativos.

![Pagina 3](/Docs/img/pagina%203.gif)

# Proximos passos

* Terminar/melhorar a documentação.
    * Finalizar a documentação mais detalhada das etapas **03 e 04** (transformação e validação)
* Verificar por melhorias de lógicas de aplicação e melhorias de eficiencia de código.
* Implementar uma pagina de vizualização por lanes.
