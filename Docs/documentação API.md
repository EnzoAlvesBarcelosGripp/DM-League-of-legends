# Como Funciona?

* Primeiro é necessario criar uma conta no [**riot developer**](https://developer.riotgames.com/), ao criar você  terá acesso a uma **API key**.


## CHAVES DE API DE DESENVOLVIMENTO
* A chave de API gerada para você ao acessar o portal do desenvolvedor é uma chave de API de desenvolvimento. Essas chaves provisórias são concedidas temporariamente para produtos que não se destinam ao uso público, mas que se beneficiam de um acesso temporário à API. O objetivo de uma chave de API de desenvolvimento é permitir que você experimente a API da Riot Games e, potencialmente, desenvolva um protótipo de produto para disponibilizar à comunidade. Elas também são desativadas a cada 24 horas; portanto, você precisará renovar a sua regularmente para mantê-la ativa.

## CHAVES DE API PESSOAIS
* Você pode solicitar uma chave de API pessoal registrando seu produto. Chaves de API pessoais devem ser usadas para produtos destinados apenas ao desenvolvedor ou a uma pequena comunidade privada. Esses produtos podem ser registrados sem passar pelo processo de verificação, mas não serão aprovados para aumentos nos limites de taxa (*rate limits*). Você pode solicitar acesso às APIs Padrão, mas não à API de Torneios. Chaves pessoais exigem uma descrição detalhada do produto.

* Usos aceitáveis ​​para uma chave de API pessoal incluem:

    * bots para sites de streaming, fóruns, servidores de comunicação por voz, etc.
    * exibir suas próprias estatísticas pessoais em seu site pessoal
    * projetos pessoais para coletar suas próprias estatísticas
    * pesquisa pessoal
    * projetos destinados a uso pessoal e não para produção
* O limite de taxa para chaves pessoais é, por definição, bastante restrito:

    * 20 requisições a cada 1 segundo
    * 100 requisições a cada 2 minutos
    > Observe que os limites de taxa são aplicados por região. Por exemplo, com o limite de taxa acima, você poderia fazer 20 requisições a cada 1 segundo para os endpoints de League of Legends das regiões NA e EUW simultaneamente.

* Você não pode executar sua aplicação para uso público utilizando uma chave pessoal, independentemente de quanto tempo leve o processo de aprovação da sua chave de produção. Observe que o uso público inclui testes alfa/beta abertos.

## SEGURANÇA DA CHAVE DE API
* Para finalizar o assunto sobre chaves de API, é importante mencionar que sua chave provavelmente será revogada se não estiver devidamente protegida. Proteger sua chave de API é um requisito para publicar um projeto, c**onforme estabelecido nas Políticas Gerais. Se constatarmos que sua chave não está protegida adequadamente, tomaremos providências para protegê-la para você. 😉

## Códigos de Resposta
* A API da Riot Games retorna todos os dados em formato JSON válido. Algumas linguagens de programação oferecem suporte nativo a JSON. Para aquelas que não oferecem, você pode encontrar uma biblioteca adequada em https://www.json.org.

* Observe que nossas APIs retornam apenas valores não vazios para economizar largura de banda. O valor zero é considerado vazio, assim como strings vazias, listas vazias e valores nulos (*null*). Qualquer campo numérico não retornado pode ser considerado como 0 (ou *null*, conforme sua preferência). Qualquer campo do tipo lista não retornado pode ser considerado uma lista vazia ou *null*. Qualquer campo do tipo String não retornado pode ser considerado uma string vazia ou *null*.

### CÓDIGOS DE RESPOSTA 2XX
* Para códigos de resposta 200, você sempre pode esperar o corpo de resposta documentado na página de referência da API. Apenas os códigos de resposta 200 garantem o retorno de um corpo de resposta no formato JSON.

* Para códigos de resposta diferentes de 200, observe o seguinte:

    * Não há garantia de retorno de um corpo de resposta.

* Se houver um corpo de resposta, não há garantia de que ele esteja no formato JSON.
* Atualmente, retornamos JSON com informações de depuração legíveis por humanos, mas a estrutura e o conteúdo dessas informações estão sujeitos a alterações. Por exemplo...
```json
    {
        "status": {
            "message": "Unauthorized",
            "status_code": 401,
        }
    }
```
> Não há garantia de que os campos `status`, `message` e `status_code` sempre existam ou permaneçam constantes para um determinado código de resposta. 4. A lógica da sua aplicação deve lidar com falhas de maneira adequada (graceful failure) com base apenas no código de resposta, sem depender do corpo da resposta.

### CÓDIGOS DE ERRO 4XX
* A classe de códigos de erro 4xx destina-se a indicar que o cliente não forneceu uma solicitação válida. Abaixo estão os códigos de erro da classe 4xx mais comuns que você pode encontrar ao usar a API.

    * **400 (Bad Request / Solicitação Inválida)** Este erro indica que há um erro de sintaxe na solicitação e que, portanto, ela foi recusada. O cliente não deve continuar fazendo solicitações semelhantes sem modificar a sintaxe ou as solicitações que estão sendo feitas.

        * Motivos Comuns

            1. Um parâmetro fornecido está em formato incorreto (por exemplo, uma string em vez de um número inteiro).
            2. Um parâmetro fornecido é inválido (por exemplo, `beginTime` e `startTime` especificam um intervalo de tempo muito grande).
            3. Um parâmetro obrigatório não foi fornecido.
    * **401 (Unauthorized / Não Autorizado)** Este erro indica que a solicitação feita não continha as credenciais de autenticação necessárias (por exemplo, uma chave de API) e, portanto, o acesso do cliente foi negado. O cliente não deve continuar fazendo solicitações semelhantes sem incluir uma chave de API na solicitação.

        * Motivos Comuns

            1. Uma chave de API não foi incluída na solicitação.
    * **403 (Forbidden / Proibido)** Este erro indica que o servidor entendeu a solicitação, mas recusa-se a autorizá-la. Não é feita distinção entre um caminho inválido ou credenciais de autorização inválidas (por exemplo, uma chave de API). O cliente não deve continuar fazendo solicitações semelhantes.

        * Motivos Comuns

            1. Uma chave de API inválida foi fornecida com a solicitação da API.
            2. Uma chave de API presente em uma lista de bloqueio (blacklist) foi fornecida com a solicitação da API.
            3. A solicitação da API referia-se a um caminho incorreto ou não suportado.
    * **404 (Not Found / Não Encontrado)** Este erro indica que o servidor não encontrou uma correspondência para a solicitação da API feita. Não é indicado se a condição é temporária ou permanente.

        * Motivos Comuns

            1. O ID ou nome fornecido não corresponde a nenhum recurso existente (por exemplo, não há nenhum Invocador correspondente ao ID especificado).
            2. Não há recursos que correspondam aos parâmetros especificados.
    * **415 (Unsupported Media Type / Tipo de Mídia Não Suportado)** Este erro indica que o servidor recusa-se a processar a solicitação porque o corpo da solicitação está em um formato não suportado.

        * Motivos Comuns

            1. O cabeçalho `Content-Type` não foi definido adequadamente. 
    * **429 (Limite de Taxa Excedido)** Este erro indica que a aplicação esgotou o número máximo de chamadas de API permitidas para um determinado período. Se o cliente receber uma resposta de "Limite de Taxa Excedido" (Rate Limit Exceeded), ele deve processar essa resposta e interromper novas chamadas de API pelo período, em segundos, indicado pelo cabeçalho `Retry-After`. Aplicações que violem esta política podem ter seu acesso desativado para preservar a integridade da API. Consulte nossa documentação sobre Limitação de Taxa (Rate Limiting) abaixo para obter mais informações sobre como verificar se você atingiu o limite e como evitar essa situação.

        * Motivos Comuns

            1. Chamadas de API não reguladas.

### Códigos de erro 5XX
* A classe de códigos de erro 5xx indica que o servidor reconhece ter encontrado um erro ou que é incapaz de processar a solicitação. Abaixo estão os códigos de erro da classe 5xx mais comuns que você pode encontrar ao utilizar a API.

    * 500 (Erro Interno do Servidor) Este erro indica uma condição inesperada ou uma exceção que impediu o servidor de atender a uma solicitação da API.

    * 503 (Serviço Indisponível) Este erro indica que o servidor está temporariamente indisponível para processar solicitações devido a um motivo desconhecido. A resposta de Serviço Indisponível implica uma condição temporária que será resolvida após algum tempo.

## Limitação de Taxa (Rate Limiting)
* Para controlar o uso da API da Riot Games, estabelecemos limites quanto ao número de vezes que os *endpoints* podem ser acessados ​​em um determinado período. Esses limites existem para minimizar abusos, manter um alto nível de estabilidade e proteger contra a sobrecarga os sistemas que sustentam a API. Como esses sistemas são os mesmos que viabilizam nossos jogos, uma sobrecarga prejudicaria a experiência dos jogadores — e nossa prioridade absoluta é proteger essa experiência.

### TIPOS DE LIMITAÇÃO DE TAXA
* Existem três tipos de limites utilizados na infraestrutura da API: limites de taxa por aplicação, por método e por serviço.

1. Limites de Taxa da Aplicação
* O primeiro tipo de limite é aplicado com base em cada chave de API e é chamado de limite de taxa da aplicação. Os limites de taxa da aplicação são aplicados por região. Cada chamada feita a qualquer endpoint da API da Riot Games em uma determinada região conta para o limite de taxa da aplicação referente àquela chave naquela região. Por exemplo, chamadas para a API de dados estáticos não contam para o limite de taxa da aplicação.
2. Limites de Taxa por Método
* O segundo tipo de limite é aplicado individualmente a cada endpoint (ou "método") para uma determinada chave de API e é chamado de limite de taxa por método. Os limites de taxa por método também são aplicados por região. Cada chamada feita a qualquer endpoint da API da Riot Games em uma determinada região conta para o limite de taxa do método e da chave de API específicos naquela região.
3. Limites de Taxa de Serviço
* O terceiro tipo de limite é aplicado individualmente a cada serviço e é chamado de limite de taxa de serviço. Os limites de taxa de serviço também são aplicados por região. Cada chamada feita a qualquer endpoint de um determinado serviço da API da Riot Games em uma região específica conta para o limite de taxa de serviço daquele serviço nessa região. Quando os limites de taxa de serviço se aplicam, nós os documentamos, incluindo quais endpoints fazem parte do serviço sujeito a essa limitação.

> Não confunda limites de taxa de método com limites de taxa de serviço. Os limites de taxa de método aplicam-se individualmente a cada aplicação. Os limites de taxa de serviço aplicam-se ao serviço e são compartilhados por todas as aplicações que fazem chamadas para esse serviço.

4. Outros Limites
* Estes limites impostos pela infraestrutura da API não são os únicos mecanismos de controle de acesso aos dados fornecidos. Alguns dos serviços subjacentes a determinados *endpoints* também podem implementar seus próprios limites de taxa (*rate limits*), independentemente da infraestrutura da API. Nesses casos, você receberá uma resposta de erro 429, mas o cabeçalho `X-Rate-Limit-Type` não estará incluído na resposta. Esse cabeçalho só será incluído quando o limite de taxa for aplicado pela infraestrutura de borda (*edge infrastructure*) da API.

> Embora nossa política seja não revelar os detalhes de funcionamento do nosso controle de limites de taxa, para fins de implementação do seu código, você pode assumir que a contagem (o *bucket*) é iniciada no momento em que você faz a primeira chamada à API.

# End Points

* Há varios  **Service**, que agrupam os endpoints por informações específicas.

## Account

* Há $8$ **endpoints**, deles os que não são do *esports*, a seguir a 1 exemplo desses **endpoints**.
    * `/riot/account/v1/accounts/by-puuid/{puuid}`
        * **Path Parameters**

        |Name|Value|Data Type|
        |:----:|:----:|:----|
        |puuid|`-`|string|

        ---
        * **Response Body**

        |Name|Data Type|Description|
        |:----:|:----:|:----|
        |puuid|string|Encrypted PUUID. Exact length of 78 characters.|
        |gameName|string|This field may be excluded from the response if the account doesn't have a gameName.|
        |tagLine|string|his field may be excluded from the response if the account doesn't have a tagLine.|
        
## Champion Mastery

* `/lol/champion-mastery/v4/champion-masteries/by-puuid/{encryptedPUUID}`
* Há $4$ **endpoints**, deles os que não são do *esports*, a seguir a 1 exemplo desses **endpoints**.
    * **Path Parameters**

    | Name | Value | Data Type |
    | :---: | :---: | :---: |
    | encryptedPUUID | `-` | string |

    * **Response Body**

     Name | Data Type | Description |
     :---: | :---: | :---: |
     puuid | string | Player Universal Unique Identifier. Exact length of 78 characters. (Encrypted) |
     championPointsUntilNextLevel | long | Number of points needed to achieve next level. Zero if player reached maximum champion level for this champion. |
     chestGranted | boolean | Is chest granted for this champion or not in current season. |
     championId | long | Champion ID for this entry. |
     lastPlayTime | long | Last time this champion was played by this player - in Unix milliseconds time format. |
     championLevel | int | Champion level for specified player and champion combination. |
     championPoints | int | Total number of champion points for this player and champion combination - they are used to determine championLevel. |
     championPointsSinceLastLevel | long | Number of points earned since current level has been achieved. |
     markRequiredForNextLevel | int | - |
     championSeasonMilestone | int | - |
     nextSeasonMilestone | NextSeasonMilestonesDto | - |
     tokensEarned | int | The token earned for this champion at the current championLevel. When the championLevel is advanced the tokensEarned resets to 0. |
     milestoneGrades | List[string] | - |

## Champion

* `/lol/platform/v3/champion-rotations`
* Há $1$ **endpoints**, deles os que não são do *esports*, a seguir a 1 exemplo desses **endpoints**.
    * **Path Parameters**

     Name   Value | Data Type |
     :---: | :---: | :---: |
     - | ` ` | - |

    ---

    * **Response Body**

    | Name | Data Type | Description |
    | :---: | :---: | :---: |
    | newplayer | array | A list of champion IDs available to players under summoner level 11 |
    | sr | array | A list of champion IDs available to all players on Summoner's Rift |    

## Clash

* `/lol/clash/v1/players/by-puuid/{puuid}`
* Há $5$ **endpoints**, deles os que não são do *esports*, a seguir a 1 exemplo desses **endpoints**.
    * **Path Parameters**

    | Name | Value | Data Type |
    | :---: | :---: | :---: |
    | puuid | `-` | string |

    ---

    * **Response Body**

    | Name | Data Type | Description |
    | :---: | :---: | :---: |
    | puuid | string | - |
    | teamId | string | - |
    | position | string | (Legal values: UNSELECTED, FILL, TOP, JUNGLE, MIDDLE, BOTTOM, UTILITY) |
    | role | string | (Legal values: CAPTAIN, MEMBER) |

## League Exp

* `/lol/league-exp/v4/entries/{queue}/{tier}/{division}`
* Há $1$ **endpoints**, deles os que não são do *esports*, a seguir a 1 exemplo desses **endpoints**.
    * **Path Parameters**

    | Name | Value | Data Type |
    | :---: | :---: | :---: |
    | queue | `-` | string |
    | tier | `-` | string |
    | division | `-` | string |

    ---

    * **Query Parameters**

    | Name | Value | Data Type |
    | :---: | :---: | :---: |
    | page | `1` | int |

    ---

    * **Response Body**

    | Name | Data Type | Description |
    | :---: | :---: | :---: |
    | leagueId | string | - |
    | summonerId | string | Player's summonerId (Encrypted) |
    | puuid | string | Player's encrypted puuid. |
    | queueType | string | - |
    | tier | string | - |
    | rank | string | The player's division within a tier. |
    | leaguePoints | int | - |
    | wins | int | Winning team on Summoners Rift. First placement in Teamfight Tactics. |
    | losses | int | Losing team on Summoners Rift. Second through eighth placement in Teamfight Tactics. |
    | hotStreak | boolean | - |
    | veteran | boolean | - |
    | freshBlood | boolean | - |
    | inactive | boolean | - |
    | miniSeries | MiniSeriesDTO | - |

## League

* `/lol/league/v4/challengerleagues/by-queue/{queue}`
* Há $5$ **endpoints**, deles os que não são do *esports*, a seguir a 1 exemplo desses **endpoints**.
    * **Path Parameters**

    | Name | Value | Data Type |
    | :---: | :---: | :---: |
    | queue | `-` | string |

    ---

    * **Response Body**

    | Name | Data Type | Description |
    | :---: | :---: | :---: |
    | leagueId | string | - |
    | entries | List[LeagueItemDTO] | - |
    | tier | string | - |
    | name | string | - |
    | queue | string | - |

## Lol Challenges

* `/lol/challenges/v1/challenges/config`
* Há $6$ **endpoints**, deles os que não são do *esports*, a seguir a 1 exemplo desses **endpoints**.
    * **Path Parameters**

    | Name | Value | Data Type |
    | :---: | :---: | :---: |
    | - | `-` | - |

    ---

    * **Response Body**

    | Name | Data Type | Description |
    | :---: | :---: | :---: |
    | id | long | - |
    | localizedNames | Map[String, Map[String, string]] | - |
    | state | State | - |
    | tracking | Tracking | - |
    | startTimestamp | long | - |
    | endTimestamp | long | - |
    | leaderboard | boolean | - |
    | thresholds | Map[String, double] | - |
## Lol Rso Match

* `/lol/rso-match/v1/matches/ids`
* Há $3$ **endpoints**, deles os que não são do *esports*, a seguir a 1 exemplo desses **endpoints**.
    * **Path Parameters**

    | Name | Value | Data Type |
    | :---: | :---: | :---: |
    | - | `-` | - |

    ---

    * **Header Parameters**

    | Name | Value | Data Type | Description |
    | :---: | :---: | :---: | :---: |
    | Authorization | `-` | string | - |

    ---

    * **Query Parameters**

    | Name | Value | Data Type | Description |
    | :---: | :---: | :---: | :---: |
    | count | `20` | int | Defaults to 20. Valid values: 0 to 100. Number of match ids to return. |
    | start | `0` | int | Defaults to 0. Start index. |
    | type | `-` | string | Filter the list of match ids by the type of match. This filter is mutually inclusive of the queue filter meaning any match ids returned must match both the queue and type filters. |
    | queue | `-` | int | Filter the list of match ids by a specific queue id. This filter is mutually inclusive of the type filter meaning any match ids returned must match both the queue and type filters. |
    | endTime | `-` | long | Epoch timestamp in seconds. |
    | startTime | `-` | long | Epoch timestamp in seconds. The matchlist started storing timestamps on June 16th, 2021. Any matches played before June 16th, 2021 won't be included in the results if the startTime filter is set. |

    ---

    * **Response Body**

    | Name | Data Type | Description |
    | :---: | :---: | :---: |
    | List[string] | array | - |

## Lol Status

* `/lol/status/v4/platform-data`
* Há $1$ **endpoints**, deles os que não são do *esports*, a seguir a 1 exemplo desses **endpoints**.
    * **Path Parameters**

    | Name | Value | Data Type |
    | :---: | :---: | :---: |
    | - | `-` | - |

    ---

    * **Response Body**

    | Name | Data Type | Description |
    | :---: | :---: | :---: |
    | id | string | - |
    | name | string | - |
    | locales | List[string] | - |
    | maintenances | List[StatusDto] | - |
    | incidents | List[StatusDto] | - |


## Match

* `/lol/match/v5/matches/by-puuid/{puuid}/ids`
* Há $4$ **endpoints**, deles os que não são do *esports*, a seguir a 1 exemplo desses **endpoints**.
    * **Path Parameters**

    | Name | Value | Data Type |
    | :---: | :---: | :---: |
    | puuid | `-` | String |

    ---

    * **Query Parameters**

    | Name | Value | Data Type | Description |
    | :---: | :---: | :---: | :---: |
    | startTime | `-` | long | Epoch timestamp in seconds. The matchlist started storing timestamps on June 16th, 2021. Any matches played before June 16th, 2021 won't be included in the results if the startTime filter is set. |
    | endTime | `-` | long | Epoch timestamp in seconds. |
    | queue | `-` | int | Filter the list of match ids by a specific queue id. This filter is mutually inclusive of the type filter meaning any match ids returned must match both the queue and type filters. |
    | type | `-` | string | Filter the list of match ids by the type of match. This filter is mutually inclusive of the queue filter meaning any match ids returned must match both the queue and type filters. |
    | start | `0` | int | Defaults to 0. Start index. |
    | count | `20` | int | Defaults to 20. Valid values: 0 to 100. Number of match ids to return. |

    ---

    * **Response Body**

    | Name | Data Type | Description |
    | :---: | :---: | :---: |
    | List[string] | array | - |

## Summoner

* `/lol/summoner/v4/summoners/by-puuid/{encryptedPUUID}`
* Há $2$ **endpoints**, deles os que não são do *esports*, a seguir a 1 exemplo desses **endpoints**.
    * **Path Parameters**

    | Name | Value | Data Type |
    | :---: | :---: | :---: |
    | encryptedPUUID | `-` | string |

    ---

    * **Response Body**

    | Name | Data Type | Description |
    | :---: | :---: | :---: |
    | profileIconId | int | ID of the summoner icon associated with the summoner. |
    | revisionDate | long | Date summoner was last modified specified as epoch milliseconds. The following events will update this timestamp: profile icon change, playing the tutorial or advanced tutorial, finishing a game, summoner name change. |
    | puuid | string | Encrypted PUUID. Exact length of 78 characters. |
    | summonerLevel | long | Summoner level associated with the summoner. |