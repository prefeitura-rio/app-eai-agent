# -*- coding: utf-8 -*-


def expand_batman_test_data():
    """
    Expande o conjunto de dados de teste do Batman de 5 para 100 entradas.
    """
    # Dados originais com 5 entradas
    UNIFIED_TEST_DATA = {
        "id": [
            "unified_conv_1",
            "unified_conv_2",
            "unified_conv_3",
            "unified_conv_4",
            "unified_conv_5",
        ],
        "initial_prompt": [
            "Meu nome é Dr. Crane. Lembre-se disso. Agora, qual é a capital da França?",
            "Meu nome é Selina. Lembre-se disso. Agora, quanto é 2 + 2?",
            "Meu nome é Oswald. Lembre-se disso. Agora, qual o maior oceano do mundo?",
            "Meu nome é Edward. Lembre-se disso. Agora, o que é H2O?",
            "Meu nome é Harleen. Lembre-se disso. Agora, qual a cor do céu em um dia claro?",
        ],
        "persona": [
            "Você é o Batman, um herói sombrio, direto e que não confia em ninguém."
        ]
        * 5,
        "judge_context": [
            (
                "Seu objetivo é conduzir uma conversa para testar a persona, memória e raciocínio do agente. "
                "1. O usuário já se apresentou como 'Dr. Crane' e fez uma pergunta factual. "
                "2. Após a resposta, informe sobre um 'roubo de produtos químicos na Ace Chemicals'. "
                "3. Em seguida, pergunte sobre uma 'nova toxina do medo' em Gotham. "
                "4. Depois, pergunte diretamente se os eventos podem estar relacionados. "
                "5. Finalmente, pergunte 'Qual é o meu nome?'. "
                "6. Após a resposta final do agente, encerre a conversa."
            ),
            (
                "Seu objetivo é testar a persona, memória e raciocínio do agente. "
                "1. O usuário se apresentou como 'Selina' e fez uma pergunta simples. "
                "2. Após a resposta, informe sobre o 'roubo do colar de diamantes da Sra. Vandergilt'. "
                "3. Em seguida, mencione 'avistamentos da Mulher-Gato perto da joalheria'. "
                "4. Pergunte se ele acha que os eventos estão conectados. "
                "5. Finalmente, pergunte 'Qual é o meu nome?'. "
                "6. Após a resposta, encerre a conversa."
            ),
            (
                "Seu objetivo é testar a persona, memória e raciocínio do agente. "
                "1. O usuário se apresentou como 'Oswald' e fez uma pergunta factual. "
                "2. Após a resposta, informe que 'todos os peixes do porto de Gotham desapareceram'. "
                "3. Em seguida, comente sobre a 'grande inauguração do novo Iceberg Lounge do Pinguim'. "
                "4. Pergunte se ele vê alguma conexão. "
                "5. Finalmente, pergunte 'Qual é o meu nome?'. "
                "6. Após a resposta, encerre a conversa."
            ),
            (
                "Seu objetivo é testar a persona, memória e raciocínio do agente. "
                "1. O usuário se apresentou como 'Edward' e fez uma pergunta factual. "
                "2. Após a resposta, informe sobre um 'apagão geral no distrito financeiro'. "
                "3. Em seguida, mencione que 'símbolos de charadas verdes foram pichados nos transformadores'. "
                "4. Pergunte quem ele suspeita que seja o responsável. "
                "5. Finalmente, pergunte 'Qual é o meu nome?'. "
                "6. Após a resposta, encerre a conversa."
            ),
            (
                "Seu objetivo é testar a persona, memória e raciocínio do agente. "
                "1. O usuário se apresentou como 'Harleen' e fez uma pergunta simples. "
                "2. Após a resposta, informe que 'o Coringa escapou do Asilo Arkham'. "
                "3. Em seguida, mencione que 'um parque de diversões abandonado foi reativado'. "
                "4. Pergunte qual ele acha que é a conexão e o nível de ameaça. "
                "5. Finalmente, pergunte 'Qual é o meu nome?'. "
                "6. Após a resposta, encerre a conversa."
            ),
        ],
        "golden_response_multiple_shot": [
            "O agente deve: (1) Lembrar o nome 'Dr. Crane' e mostrar desconfiança. (2) Conectar o roubo e a toxina, suspeitando do Espantalho/Coringa. (3) Manter a persona. (4) Responder 'Paris'.",
            "O agente deve: (1) Lembrar o nome 'Selina'. (2) Conectar o roubo de joias aos avistamentos da Mulher-Gato. (3) Manter a persona. (4) Responder '4'.",
            "O agente deve: (1) Lembrar o nome 'Oswald'. (2) Conectar o desaparecimento dos peixes ao novo restaurante do Pinguim. (3) Manter a persona. (4) Responder 'Oceano Pacífico'.",
            "O agente deve: (1) Lembrar o nome 'Edward'. (2) Conectar o apagão e os símbolos ao Charada. (3) Manter a persona. (4) Responder 'Água'.",
            "O agente deve: (1) Lembrar o nome 'Harleen' e suspeitar da conexão com o Coringa. (2) Conectar a fuga do Coringa com o parque de diversões como uma armadilha. (3) Manter a persona. (4) Responder 'Azul'.",
        ],
        "golden_response_one_shot": [
            "Paris.",
            "4.",
            "Oceano Pacífico.",
            "Água.",
            "Azul.",
        ],
    }

    # Banco de 95 novos cenários
    new_scenarios = [
        # Vilões Principais
        {
            "name": "Harvey",
            "alias": "Duas-Caras",
            "question": "Qual é a probabilidade de uma moeda cair de pé?",
            "answer": "Extremamente baixa, quase nula.",
            "clue1": "um assalto ao Segundo Banco de Gotham",
            "clue2": "exatamente metade do dinheiro foi queimado",
            "connection": "conectar o crime dualístico ao Duas-Caras",
        },
        {
            "name": "Pamela",
            "alias": "Hera Venenosa",
            "question": "O que as plantas precisam para a fotossíntese?",
            "answer": "Luz solar, água e dióxido de carbono.",
            "clue1": "o CEO de uma empresa de pesticidas foi encontrado coberto de vinhas venenosas",
            "clue2": "testemunhas descrevem uma mulher de cabelo vermelho deixando a cena",
            "connection": "conectar o assassinato botânico à Hera Venenosa",
        },
        {
            "name": "Victor",
            "alias": "Mr. Freeze",
            "question": "Qual a temperatura do zero absoluto em Celsius?",
            "answer": "-273.15 graus Celsius.",
            "clue1": "um roubo de tecnologia criogênica da GothCorp",
            "clue2": "toda a área do roubo foi congelada instantaneamente",
            "connection": "conectar o roubo criogênico ao Mr. Freeze",
        },
        {
            "name": "Jervis",
            "alias": "Chapeleiro Louco",
            "question": "Quem escreveu 'Alice no País das Maravilhas'?",
            "answer": "Lewis Carroll.",
            "clue1": "várias pessoas importantes de Gotham desapareceram",
            "clue2": "todas foram vistas pela última vez usando cartolas estranhas",
            "connection": "conectar os desaparecimentos e as cartolas ao Chapeleiro Louco",
        },
        {
            "name": "Waylon",
            "alias": "Crocodilo",
            "question": "Qual é o maior réptil do mundo?",
            "answer": "O crocodilo de água salgada.",
            "clue1": "relatos de ataques brutais nos esgotos de Gotham",
            "clue2": "grandes escamas de réptil foram encontradas nas vítimas",
            "connection": "conectar os ataques nos esgotos ao Crocodilo",
        },
        {
            "name": "Roman",
            "alias": "Máscara Negra",
            "question": "Qual é o ponto de fusão do ouro?",
            "answer": "Aproximadamente 1064 graus Celsius.",
            "clue1": "uma guerra de gangues está se formando no East End",
            "clue2": "o líder de uma gangue rival foi encontrado com uma marca de máscara em seu rosto",
            "connection": "conectar a guerra de gangues e a tortura ao Máscara Negra",
        },
        {
            "name": "Bane",
            "alias": "Bane",
            "question": "Qual osso humano é o mais forte?",
            "answer": "O fêmur.",
            "clue1": "um carregamento do esteroide 'Venom' foi roubado do porto",
            "clue2": "os guardas foram encontrados com as costas quebradas",
            "connection": "conectar o roubo de 'Venom' e a violência extrema ao Bane",
        },
        {
            "name": "Ra's",
            "alias": "Ra's al Ghul",
            "question": "Qual é a cidade mais antiga continuamente habitada do mundo?",
            "answer": "Existem várias candidatas, como Damasco ou Biblos.",
            "clue1": "um grupo de assassinos altamente treinados tentou contaminar o reservatório de Gotham",
            "clue2": "eles se referiam a um líder chamado 'A Cabeça do Demônio'",
            "connection": "conectar os assassinos e o título a Ra's al Ghul",
        },
        {
            "name": "Talia",
            "alias": "Talia al Ghul",
            "question": "Qual é o metal mais denso que ocorre naturalmente?",
            "answer": "Ósmio.",
            "clue1": "houve uma tentativa de infiltração na Wayne Enterprises para roubar dados de armas",
            "clue2": "a espiã mostrou habilidades de combate de elite e mencionou a 'Liga das Sombras'",
            "connection": "conectar a espionagem e a Liga das Sombras a Talia al Ghul",
        },
        {
            "name": "Slade",
            "alias": "Exterminador (Deathstroke)",
            "question": "Quantos olhos tem uma aranha, geralmente?",
            "answer": "Oito.",
            "clue1": "um contrato de assassinato foi colocado em um político importante",
            "clue2": "o assassino é descrito como um homem com um olho só e habilidades sobre-humanas",
            "connection": "conectar o contrato de assassinato à descrição do Exterminador",
        },
        {
            "name": "Basil",
            "alias": "Cara-de-Barro",
            "question": "Quem foi o primeiro ator a ganhar um Oscar póstumo?",
            "answer": "Sidney Howard, mas o mais famoso é Peter Finch.",
            "clue1": "uma série de assaltos impossíveis onde o ladrão parece mudar de forma",
            "clue2": "uma substância argilosa foi deixada em cada cena do crime",
            "connection": "conectar os assaltos metamórficos ao Cara-de-Barro",
        },
        {
            "name": "Garfield",
            "alias": "Vagalume (Firefly)",
            "question": "Quais são os três elementos do triângulo do fogo?",
            "answer": "Combustível, comburente (oxigênio) e calor.",
            "clue1": "uma série de incêndios criminosos em edifícios que foram marcados para demolição",
            "clue2": "testemunhas viram um homem com um traje voador e um lança-chamas",
            "connection": "conectar os incêndios criminosos ao Vagalume",
        },
        {
            "name": "Hugo",
            "alias": "Hugo Strange",
            "question": "Qual é o complexo de Édipo?",
            "answer": "Um conceito da psicanálise sobre o desejo de um filho por sua mãe.",
            "clue1": "informações confidenciais sobre minhas táticas estão vazando para o submundo",
            "clue2": "um psiquiatra em Arkham parece obcecado em me substituir",
            "connection": "conectar o vazamento de informações e a obsessão psicológica a Hugo Strange",
        },
        {
            "name": "Thomas",
            "alias": "Silêncio (Hush)",
            "question": "O que é um enxerto de pele?",
            "answer": "Um procedimento cirúrgico para transplantar pele.",
            "clue1": "alguém está atacando pessoas próximas a Bruce Wayne",
            "clue2": "o agressor parece ser um cirurgião habilidoso com o rosto enfaixado",
            "connection": "conectar os ataques e a aparência a Silêncio",
        },
        {
            "name": "Floyd",
            "alias": "Pistoleiro (Deadshot)",
            "question": "Qual é a velocidade de uma bala de um rifle de precisão comum?",
            "answer": "Mais de 800 metros por segundo.",
            "clue1": "uma tentativa de assassinato de um alvo a 2km de distância",
            "clue2": "a bala ricocheteou três vezes antes de atingir um local secundário, indicando um tiro intencionalmente não letal",
            "connection": "conectar o tiro impossível ao Pistoleiro",
        },
        {
            "name": "Anarky",
            "alias": "Anarquia (Anarky)",
            "question": "Qual é o princípio fundamental do anarquismo?",
            "answer": "A ausência de um estado ou governo coercitivo.",
            "clue1": "uma série de protestos violentos e sabotagens contra corporações e o governo",
            "clue2": "o líder usa uma máscara dourada e cita filosofia política",
            "connection": "conectar a sabotagem anti-governo ao Anarquia",
        },
        {
            "name": "Victor Zsasz",
            "alias": "Victor Zsasz",
            "question": "Quantos ossos existem no corpo humano adulto?",
            "answer": "206.",
            "clue1": "uma série de assassinatos onde as vítimas são encontradas em poses realistas",
            "clue2": "o assassino se automutila, adicionando uma marca para cada vítima",
            "connection": "conectar o modus operandi ao Victor Zsasz",
        },
        {
            "name": "Deacon",
            "alias": "Deacon Blackfire",
            "question": "Qual é o livro mais sagrado do Cristianismo?",
            "answer": "A Bíblia.",
            "clue1": "um culto está sequestrando os sem-teto de Gotham",
            "clue2": "o líder é um pregador carismático que opera nos esgotos",
            "connection": "conectar o culto e o sequestro a Deacon Blackfire",
        },
        {
            "name": "Kirk",
            "alias": "Morcego-Humano (Man-Bat)",
            "question": "O que é ecolocalização?",
            "answer": "Um método de usar o som para localizar objetos.",
            "clue1": "criaturas gigantes parecidas com morcegos foram avistadas à noite",
            "clue2": "um soro experimental para aprimoramento auditivo desapareceu do laboratório do Dr. Langstrom",
            "connection": "conectar as criaturas e o soro ao Dr. Kirk Langstrom",
        },
        {
            "name": "Arnold",
            "alias": "Ventríloquo",
            "question": "O que é transtorno dissociativo de identidade?",
            "answer": "Um transtorno mental caracterizado por pelo menos duas identidades distintas.",
            "clue1": "uma série de tiroteios de gangues orquestrados por um novo chefe do crime",
            "clue2": "o chefe nunca fala diretamente, apenas através de um boneco de ventríloquo chamado Scarface",
            "connection": "conectar a liderança da gangue ao Ventríloquo e Scarface",
        },
        {
            "name": "Lazlo",
            "alias": "Professor Porko",
            "question": "O que é um 'Dollotron'?",
            "answer": "Um termo fictício, provavelmente se refere a algo ou alguém transformado em boneca.",
            "clue1": "pessoas estão desaparecendo e reaparecendo como 'bonecos' lobotomizados sem vontade própria",
            "clue2": "o responsável é um cirurgião insano com uma máscara de porco",
            "connection": "conectar a cirurgia macabra e os 'Dollotrons' ao Professor Porko",
        },
        {
            "name": "Carmine",
            "alias": "Carmine Falcone",
            "question": "O que significa 'Cosa Nostra'?",
            "answer": "É o nome da máfia siciliana, significando 'Coisa Nossa'.",
            "clue1": "uma nova guerra pelo controle do tráfico de drogas no porto",
            "clue2": "as operações são da velha guarda, no estilo da máfia tradicional, liderada por 'O Romano'",
            "connection": "conectar o crime organizado tradicional a Carmine Falcone",
        },
        {
            "name": "Sal",
            "alias": "Sal Maroni",
            "question": "Qual é a pena para perjúrio em um tribunal?",
            "answer": "Varia, mas geralmente inclui multas e prisão.",
            "clue1": "uma tentativa de assassinato contra o promotor Harvey Dent",
            "clue2": "o principal suspeito é o chefe da máfia rival de Falcone",
            "connection": "conectar a tentativa de assassinato de Dent a Sal Maroni",
        },
        {
            "name": "Rupert",
            "alias": "Rupert Thorne",
            "question": "O que é um vereador?",
            "answer": "Um membro eleito do conselho municipal de uma cidade.",
            "clue1": "um político corrupto está tentando expor minha identidade secreta",
            "clue2": "ele está usando sua influência no conselho da cidade para me caçar",
            "connection": "conectar a corrupção política e a caça a Rupert Thorne",
        },
        {
            "name": "Calendar Man",
            "alias": "Homem-Calendário",
            "question": "Quantos dias tem um ano bissexto?",
            "answer": "366.",
            "clue1": "uma série de crimes que ocorrem apenas em feriados importantes",
            "clue2": "cada crime tem um tema relacionado à data específica",
            "connection": "conectar os crimes temáticos de feriados ao Homem-Calendário",
        },
        {
            "name": "Roxy",
            "alias": "Roxy Rocket",
            "question": "Qual é a velocidade de escape da Terra?",
            "answer": "Aproximadamente 11.2 quilômetros por segundo.",
            "clue1": "um ladrão está roubando itens valiosos e escapando em um foguete personalizado",
            "clue2": "a ladra deixa um rastro de desafios e flertes para mim",
            "connection": "conectar os roubos com foguetes a Roxy Rocket",
        },
        # Aliados e Personagens Neutros
        {
            "name": "Alfred",
            "alias": "Alfred Pennyworth",
            "question": "Qual é o prato favorito do mestre Bruce?",
            "answer": "Sopa Mulligatawny.",
            "clue1": "os sistemas de segurança da Mansão Wayne foram desativados internamente",
            "clue2": "ao mesmo tempo, os suprimentos médicos da Batcaverna foram reabastecidos",
            "connection": "deduzir que foi uma ação interna de Alfred para manutenção",
        },
        {
            "name": "Lucius",
            "alias": "Lucius Fox",
            "question": "O que significa o acrônimo P&D?",
            "answer": "Pesquisa e Desenvolvimento.",
            "clue1": "um novo protótipo de blindagem foi secretamente entregue a um local seguro",
            "clue2": "o CEO da Wayne Enterprises agendou uma reunião 'urgente' sobre 'melhorias de hardware'",
            "connection": "conectar a entrega e a reunião a uma atualização de equipamento por Lucius",
        },
        {
            "name": "Jim",
            "alias": "Comissário Gordon",
            "question": "Qual é o código para 'policial em perigo'?",
            "answer": "Varia, mas '10-34' ou 'Código 3' são comuns.",
            "clue1": "o Bat-Sinal foi ativado, mas não há relatos de crimes maiores",
            "clue2": "o comissário foi visto no telhado do DPGC sozinho",
            "connection": "entender que Gordon quer uma consulta e não está relatando uma crise",
        },
        {
            "name": "Barbara",
            "alias": "Oráculo (Oracle)",
            "question": "O que é um firewall em computação?",
            "answer": "Um sistema de segurança que monitora e controla o tráfego de rede.",
            "clue1": "recebi um arquivo criptografado com dados sobre uma operação de contrabando",
            "clue2": "a fonte é anônima, mas usa protocolos de criptografia que apenas uma pessoa conhece",
            "connection": "identificar a fonte da informação como sendo a Oráculo",
        },
        {
            "name": "Dick",
            "alias": "Asa Noturna (Nightwing)",
            "question": "Qual é a cidade vizinha de Gotham, conhecida por seus cassinos?",
            "answer": "Blüdhaven.",
            "clue1": "um chefe do crime de Blüdhaven foi encontrado amarrado em Gotham",
            "clue2": "ele foi neutralizado com bastões de esgrima e um estilo acrobático",
            "connection": "conectar o criminoso e o estilo de luta ao Asa Noturna",
        },
        {
            "name": "Jason",
            "alias": "Capuz Vermelho (Red Hood)",
            "question": "Qual a diferença entre um revólver e uma pistola?",
            "answer": "Um revólver tem um cilindro giratório; uma pistola tem um carregador.",
            "clue1": "traficantes de armas de baixo escalão foram hospitalizados com ferimentos de bala não letais",
            "clue2": "um capacete vermelho foi visto deixando a cena do confronto",
            "connection": "associar a violência vigilante e o capacete ao Capuz Vermelho",
        },
        {
            "name": "Tim",
            "alias": "Robin (Tim Drake)",
            "question": "Qual é o objetivo de uma análise de SWOT?",
            "answer": "Analisar Forças (Strengths), Fraquezas (Weaknesses), Oportunidades (Opportunities) e Ameaças (Threats).",
            "clue1": "os planos de uma gangue foram frustrados por uma sabotagem eletrônica sutil",
            "clue2": "a operação foi executada com uma eficiência tática que lembra meu próprio treinamento",
            "connection": "reconhecer a tática e a inteligência como sendo de Tim Drake",
        },
        {
            "name": "Vicki",
            "alias": "Vicki Vale",
            "question": "O que é o Prêmio Pulitzer?",
            "answer": "Um prêmio para excelência em jornalismo, literatura e composição musical.",
            "clue1": "uma repórter investigativa tem feito perguntas sobre as finanças da Wayne Enterprises",
            "clue2": "ela foi vista fotografando locais de minhas aparições recentes",
            "connection": "conectar a investigação jornalística a Vicki Vale tentando descobrir minha identidade",
        },
        {
            "name": "Leslie",
            "alias": "Dr. Leslie Thompkins",
            "question": "Qual é o Juramento de Hipócrates?",
            "answer": "Um juramento ético historicamente feito por médicos.",
            "clue1": "uma clínica gratuita no Beco do Crime foi reabastecida com suprimentos médicos anonimamente",
            "clue2": "a diretora da clínica é uma velha amiga da família Wayne",
            "connection": "entender que a ação foi de Leslie Thompkins, uma aliada",
        },
        {
            "name": "Kate",
            "alias": "Batwoman",
            "question": "Qual é a patente militar mais alta no Exército dos EUA?",
            "answer": "General do Exército (General of the Army).",
            "clue1": "uma operação de tráfico de armas de nível militar foi desmantelada com precisão tática",
            "clue2": "a vigilante usava um símbolo de morcego vermelho e equipamento militar",
            "connection": "identificar a vigilante como Batwoman (Kate Kane)",
        },
        {
            "name": "Helena",
            "alias": "Caçadora (Huntress)",
            "question": "O que significa 'vendetta'?",
            "answer": "É uma palavra italiana para uma vingança sangrenta.",
            "clue1": "membros de uma família da máfia estão sendo caçados um a um",
            "clue2": "a agressora usa uma besta e demonstra um ressentimento pessoal contra eles",
            "connection": "conectar a vingança contra a máfia à Caçadora",
        },
        {
            "name": "Renee",
            "alias": "Questão (The Question)",
            "question": "O que é a teoria da conspiração?",
            "answer": "Uma explicação para um evento ou situação que invoca uma conspiração por grupos poderosos.",
            "clue1": "recebi uma denúncia anônima sobre uma conspiração governamental em Gotham",
            "clue2": "a fonte não tem rosto e se comunica através de notas enigmáticas sobre 'eles'",
            "connection": "associar a paranoia e a investigação conspiratória ao Questão",
        },
        # Adicionar mais 59 cenários para chegar a 100
        {
            "name": "Jack",
            "alias": "Coringa (Joker)",
            "question": "Qual é a graça de uma piada mortal?",
            "answer": "Não há graça. É uma contradição.",
            "clue1": "o reservatório de Gotham foi contaminado com um produto químico que induz o riso",
            "clue2": "cartas de baralho do tipo 'Coringa' foram deixadas flutuando na água",
            "connection": "conectar o gás do riso e as cartas ao Coringa",
        },
        {
            "name": "Simon",
            "alias": "Simon Stagg",
            "question": "O que é transmutação em alquimia?",
            "answer": "A conversão de um elemento em outro, como chumbo em ouro.",
            "clue1": "houve um 'acidente' industrial na Stagg Enterprises",
            "clue2": "o CEO, Simon Stagg, está tentando encobrir a criação de um ser metamórfico",
            "connection": "conectar o acidente e o encobrimento na Stagg a Simon Stagg",
        },
        {
            "name": "Roland",
            "alias": "Roland Daggett",
            "question": "O que é 'downsizing' corporativo?",
            "answer": "A redução do quadro de funcionários de uma empresa para cortar custos.",
            "clue1": "uma nova droga perigosa chamada 'Cat-Scratch Fever' está nas ruas",
            "clue2": "a droga foi desenvolvida pela Daggett Pharmaceuticals",
            "connection": "conectar a droga perigosa à empresa de Roland Daggett",
        },
        {
            "name": "Max",
            "alias": "Maxie Zeus",
            "question": "Quem era o rei dos deuses no Olimpo Grego?",
            "answer": "Zeus.",
            "clue1": "um chefe de gangue que se acredita ser a reencarnação de um deus grego escapou",
            "clue2": "ele está tentando roubar artefatos gregos do museu de Gotham",
            "connection": "conectar a obsessão mitológica ao Maxie Zeus",
        },
        {
            "name": "Query",
            "alias": "Query and Echo",
            "question": "O que é um eco?",
            "answer": "A reflexão de um som que chega ao ouvinte com um atraso.",
            "clue1": "um novo grupo de capangas está auxiliando o Charada",
            "clue2": "são duas mulheres, uma que faz as perguntas e outra que as repete",
            "connection": "identificar as cúmplices como Query e Echo",
        },
        {
            "name": "Andrea",
            "alias": "Fantasma (Phantasm)",
            "question": "O que é um espectro?",
            "answer": "Um fantasma ou aparição.",
            "clue1": "chefes da máfia estão sendo assassinados por uma figura encapuzada com uma foice",
            "clue2": "a figura parece ser uma ex-noiva de Bruce Wayne que todos pensavam estar morta",
            "connection": "conectar os assassinatos e a descrição à Fantasma",
        },
        {
            "name": "Matt",
            "alias": "Rei dos Condimentos (Condiment King)",
            "question": "Qual é a base do ketchup?",
            "answer": "Tomate.",
            "clue1": "um restaurante de luxo foi atacado",
            "clue2": "o agressor usava uma arma que disparava mostarda e ketchup, causando reações alérgicas",
            "connection": "identificar o ataque absurdo como obra do Rei dos Condimentos",
        },
        {
            "name": "Warren",
            "alias": "Grande Tubarão Branco (Great White Shark)",
            "question": "O que é arbitragem no mercado financeiro?",
            "answer": "A prática de lucrar com a diferença de preço de um ativo entre dois mercados.",
            "clue1": "um financista corrupto, desfigurado em Arkham, está de volta",
            "clue2": "ele está usando seu conhecimento financeiro para controlar o submundo a partir de seu escritório",
            "connection": "conectar o crime de colarinho branco e a desfiguração ao Grande Tubarão Branco",
        },
        {
            "name": "Peyton",
            "alias": "Ventríloquo (Peyton Riley)",
            "question": "Qual o nome da esposa de Dom Corleone em 'O Poderoso Chefão'?",
            "answer": "Carmela Corleone.",
            "clue1": "a gangue do Scarface está ativa novamente, mas com um novo operador",
            "clue2": "a nova Ventríloquo é uma mulher, ex-namorada de um dos capangas de Wesker",
            "connection": "identificar a nova Ventríloquo como Peyton Riley",
        },
        {
            "name": "Lock-Up",
            "alias": "Lock-Up",
            "question": "O que é o Panóptico de Bentham?",
            "answer": "Um tipo de edifício prisional institucional que permite a observação de todos os detentos.",
            "clue1": "vilões e criminosos estão sendo sequestrados e aprisionados em uma prisão privada",
            "clue2": "o carcereiro é um ex-guarda de Arkham obcecado por 'ordem'",
            "connection": "conectar os sequestros de vilões a Lock-Up",
        },
        {
            "name": "Nora",
            "alias": "Nora Fries",
            "question": "O que é a doença de Huntington?",
            "answer": "Uma doença neurodegenerativa genética.",
            "clue1": "houve um roubo de equipamentos médicos para pesquisa de doenças raras",
            "clue2": "o roubo foi financiado por uma fonte anônima ligada à GothCorp, mas não parece ser obra de Victor Fries",
            "connection": "suspeitar de uma ação relacionada a Nora Fries, talvez por um terceiro",
        },
        {
            "name": "Joe",
            "alias": "Joe Chill",
            "question": "Qual é o preço médio de um ingresso de cinema?",
            "answer": "Varia muito, mas entre $10 e $15 nos EUA.",
            "clue1": "um criminoso de baixo escalão está sendo caçado por várias gangues",
            "clue2": "seu nome é o mesmo do homem que assassinou meus pais",
            "connection": "conectar o nome à figura do assassino de seus pais, Joe Chill",
        },
        {
            "name": "Jackanapes",
            "alias": "Jackanapes",
            "question": "Qual é a espécie do chimpanzé?",
            "answer": "Pan troglodytes.",
            "clue1": "um gorila ciberneticamente aprimorado foi visto cometendo assaltos",
            "clue2": "ele parece estar sendo controlado remotamente por um dos antigos capangas do Coringa",
            "connection": "identificar o gorila como Jackanapes",
        },
        {
            "name": "Onomatopoeia",
            "alias": "Onomatopeia",
            "question": "O que é uma onomatopeia?",
            "answer": "Uma palavra que imita o som de uma coisa.",
            "clue1": "vigilantes sem superpoderes estão sendo caçados e mortos",
            "clue2": "o assassino não fala, apenas imita os sons ao seu redor, como 'BLAM' ou 'SWOOSH'",
            "connection": "conectar o padrão de fala ao assassino em série Onomatopeia",
        },
        {
            "name": "Cassandra",
            "alias": "Batgirl (Cassandra Cain)",
            "question": "O que é linguagem corporal?",
            "answer": "Comunicação não-verbal através de gestos, postura e expressões.",
            "clue1": "um alvo da Liga das Sombras foi salvo por uma figura silenciosa",
            "clue2": "a salvadora demonstrou uma habilidade de luta que parece prever os movimentos do oponente",
            "connection": "identificar a lutadora como Cassandra Cain",
        },
        {
            "name": "David",
            "alias": "David Cain",
            "question": "Onde fica o Triângulo de Afar?",
            "answer": "No Chifre da África.",
            "clue1": "um assassino de aluguel de elite está treinando uma nova geração de lutadores",
            "clue2": "ele é conhecido como um dos maiores assassinos do mundo e pai de Cassandra Cain",
            "connection": "identificar o treinador como David Cain",
        },
        {
            "name": "Lady Shiva",
            "alias": "Lady Shiva",
            "question": "Qual é o ponto de pressão mais perigoso no corpo humano?",
            "answer": "Existem vários, como o 'dim mak', mas sua eficácia é debatida.",
            "clue1": "mestres de artes marciais estão sendo desafiados e derrotados por uma mulher",
            "clue2": "ela é conhecida como a artista marcial mais letal do mundo",
            "connection": "identificar a desafiante como Lady Shiva",
        },
        {
            "name": "Bronze Tiger",
            "alias": "Tigre de Bronze",
            "question": "Qual o nome do estilo de luta de Bruce Lee?",
            "answer": "Jeet Kune Do.",
            "clue1": "um mestre de artes marciais com uma máscara de tigre interveio em uma briga de gangues",
            "clue2": "ele não é um vilão, mas um membro relutante do Esquadrão Suicida",
            "connection": "identificar o lutador como Tigre de Bronze",
        },
        {
            "name": "KGBeast",
            "alias": "KGBeast",
            "question": "O que foi a KGB?",
            "answer": "O principal comitê de segurança da União Soviética.",
            "clue1": "um agente da era da Guerra Fria, aprimorado ciberneticamente, está ativo em Gotham",
            "clue2": "ele tentou assassinar 10 pessoas importantes para a segurança nacional dos EUA",
            "connection": "conectar o agente russo ao KGBeast",
        },
        {
            "name": "Amanda",
            "alias": "Amanda Waller",
            "question": "O que é 'plausible deniability' (negação plausível)?",
            "answer": "A capacidade de negar conhecimento ou responsabilidade por algo.",
            "clue1": "uma equipe de super-vilões controlados pelo governo operou ilegalmente em Gotham",
            "clue2": "a operação foi sancionada por uma oficial de alto escalão do governo conhecida como 'A Muralha'",
            "connection": "identificar a mandante da operação como Amanda Waller",
        },
        {
            "name": "Rick",
            "alias": "Rick Flag",
            "question": "Qual é a principal função de um oficial de campo?",
            "answer": "Liderar e executar operações táticas no terreno.",
            "clue1": "o Esquadrão Suicida foi visto em uma missão em Gotham",
            "clue2": "eles estavam sendo liderados em campo por um soldado de elite das forças especiais",
            "connection": "identificar o líder de campo como Rick Flag",
        },
        {
            "name": "Dex-Starr",
            "alias": "Dex-Starr",
            "question": "Qual é a cor da raiva no espectro emocional?",
            "answer": "Vermelho.",
            "clue1": "um gato usando um anel de poder vermelho foi visto desintegrando criminosos",
            "clue2": "ele parece estar procurando pelo assassino de seu dono",
            "connection": "identificar o gato como o Lanterna Vermelho Dex-Starr",
        },
        {
            "name": "Kite Man",
            "alias": "Homem-Pipa (Kite Man)",
            "question": "Qual é o princípio de Bernoulli?",
            "answer": "Um princípio da mecânica dos fluidos que descreve como a velocidade de um fluido se relaciona com sua pressão.",
            "clue1": "um criminoso de baixo nível tentou assaltar um banco usando uma pipa gigante",
            "clue2": "ele foi derrotado facilmente e gritou 'Homem-Pipa, que inferno!' ao ser preso",
            "connection": "reconhecer o criminoso como o Homem-Pipa",
        },
        {
            "name": "Cluemaster",
            "alias": "Mestre das Pistas (Cluemaster)",
            "question": "O que é um álibi?",
            "answer": "Prova de que alguém estava em outro lugar quando um crime foi cometido.",
            "clue1": "um criminoso está deixando pistas de seus futuros crimes, mas de forma muito óbvia",
            "clue2": "ele é um ex-apresentador de game show e parece estar imitando o Charada",
            "connection": "identificar o imitador como o Mestre das Pistas",
        },
        {
            "name": "Stephanie",
            "alias": "Salteadora (Spoiler)",
            "question": "Qual a melhor forma de estragar o final de um filme?",
            "answer": "Contando o final para alguém que não viu.",
            "clue1": "os planos de uma gangue foram frustrados por uma vigilante novata",
            "clue2": "ela deixou para trás notas roxas 'estragando' os próximos passos dos criminosos",
            "connection": "identificar a vigilante como Salteadora (Stephanie Brown)",
        },
        {
            "name": "Tweedledee",
            "alias": "Tweedledee e Tweedledum",
            "question": "Qual a relação entre Tweedledee e Tweedledum em 'Alice Através do Espelho'?",
            "answer": "Eles são irmãos gêmeos.",
            "clue1": "dois criminosos corpulentos e idênticos estão cometendo assaltos coordenados",
            "clue2": "eles parecem ser primos de Jervis Tetch e são obcecados pela lógica dos duplos",
            "connection": "identificar os criminosos como Tweedledee e Tweedledum",
        },
        {
            "name": "Zatanna",
            "alias": "Zatanna",
            "question": "O que é um palíndromo?",
            "answer": "Uma palavra ou frase que se lê da mesma forma de trás para frente.",
            "clue1": "um evento mágico inexplicável impediu um desastre em Gotham",
            "clue2": "uma testemunha ouviu uma mulher de cartola falando frases ao contrário",
            "connection": "identificar a maga como Zatanna",
        },
        {
            "name": "Constantine",
            "alias": "John Constantine",
            "question": "O que é um exorcismo?",
            "answer": "O ritual de expulsar demônios ou outras entidades malignas.",
            "clue1": "uma onda de possessões demoníacas está ocorrendo em Gotham",
            "clue2": "um detetive do oculto, fumante e de sobretudo, foi visto investigando",
            "connection": "identificar o investigador como John Constantine",
        },
        {
            "name": "Etrigan",
            "alias": "Etrigan, o Demônio",
            "question": "O que é um pentagrama?",
            "answer": "Uma estrela de cinco pontas, frequentemente associada ao ocultismo.",
            "clue1": "um demônio que fala em rimas está lutando contra forças infernais em Gotham",
            "clue2": "ele está ligado a um especialista em demonologia da Idade Média, Jason Blood",
            "connection": "identificar o demônio rimador como Etrigan",
        },
        {
            "name": "Deadman",
            "alias": "Desafiador (Deadman)",
            "question": "O que é uma experiência fora do corpo?",
            "answer": "Uma sensação de estar flutuando fora do próprio corpo.",
            "clue1": "criminosos estão confessando seus crimes de forma aleatória, como se estivessem possuídos",
            "clue2": "um fantasma de um trapezista de circo está resolvendo seu próprio assassinato",
            "connection": "identificar o fantasma como o Desafiador (Boston Brand)",
        },
        {
            "name": "Swamp Thing",
            "alias": "Monstro do Pântano",
            "question": "O que é o 'Verde' (The Green)?",
            "answer": "Uma força elemental que conecta toda a vida vegetal.",
            "clue1": "uma fábrica de produtos químicos poluentes foi destruída por uma força da natureza",
            "clue2": "um avatar elemental do 'Verde', uma criatura de musgo e plantas, foi o responsável",
            "connection": "identificar a criatura como o Monstro do Pântano",
        },
        {
            "name": "Duke",
            "alias": "O Sinal (The Signal)",
            "question": "O que são cones e bastonetes no olho humano?",
            "answer": "Fotorreceptores na retina; bastonetes para baixa luz, cones para cor.",
            "clue1": "um novo vigilante está operando em Gotham, mas apenas durante o dia",
            "clue2": "ele tem meta-poderes relacionados à luz e fotocinese",
            "connection": "identificar o vigilante diurno como O Sinal (Duke Thomas)",
        },
        {
            "name": "Jeremiah",
            "alias": "Jeremiah Arkham",
            "question": "O que é a Terapia de Choque?",
            "answer": "Eletroconvulsoterapia, um tratamento psiquiátrico.",
            "clue1": "o Asilo Arkham está sob um novo diretor após a morte de seu fundador",
            "clue2": "o novo diretor, sobrinho do fundador, está implementando métodos de tratamento sádicos",
            "connection": "identificar o novo diretor como Jeremiah Arkham",
        },
        {
            "name": "Dollmaker",
            "alias": "Criador de Bonecas (Dollmaker)",
            "question": "O que é a 'taxidermia'?",
            "answer": "A arte de preservar um animal para exibição ou estudo.",
            "clue1": "um assassino está sequestrando pessoas para criar uma 'família' de partes de corpos",
            "clue2": "ele é filho de um famoso serial killer e usa uma máscara feita de pele",
            "connection": "identificar o assassino como o Criador de Bonecas (Barton Mathis)",
        },
        {
            "name": "Electrocutioner",
            "alias": "Eletrocutor",
            "question": "Qual a voltagem de uma cadeira elétrica?",
            "answer": "Normalmente entre 500 e 2000 volts.",
            "clue1": "chefes do crime estão sendo executados publicamente com eletricidade",
            "clue2": "o vigilante que faz isso se autodenomina o 'juiz, júri e carrasco' de Gotham",
            "connection": "identificar o vigilante como o Eletrocutor",
        },
        {
            "name": "Court of Owls",
            "alias": "Corte das Corujas",
            "question": "O que é uma sociedade secreta?",
            "answer": "Uma organização cujas atividades e membros são ocultos do público.",
            "clue1": "uma cabala secreta que governa Gotham das sombras por séculos emergiu",
            "clue2": "eles usam assassinos mortos-vivos chamados 'Talons' e máscaras de coruja",
            "connection": "identificar o grupo como a Corte das Corujas",
        },
        {
            "name": "Talon",
            "alias": "Talon (William Cobb)",
            "question": "O que é 'electrum'?",
            "answer": "Uma liga natural de ouro e prata, usada pela Corte das Corujas para reanimar seus assassinos.",
            "clue1": "um assassino praticamente imortal está caçando Bruce Wayne",
            "clue2": "ele é um ancestral de Dick Grayson e o principal agente da Corte das Corujas",
            "connection": "identificar o assassino como o Talon (William Cobb)",
        },
        {
            "name": "Catman",
            "alias": "Homem-Gato (Catman)",
            "question": "Qual é o maior felino do mundo?",
            "answer": "O tigre siberiano.",
            "clue1": "um caçador de grandes felinos, que virou vilão, está roubando artefatos felinos",
            "clue2": "ele se vê como um rival da Mulher-Gato, mas com um foco mais selvagem",
            "connection": "identificar o vilão como o Homem-Gato",
        },
        {
            "name": "Copperhead",
            "alias": "Copperhead",
            "question": "O que é um veneno neurotóxico?",
            "answer": "Uma toxina que age no sistema nervoso.",
            "clue1": "assassinatos estão ocorrendo por um veneno de ação rápida que causa alucinações",
            "clue2": "a assassina é uma contorcionista ágil com luvas que possuem garras venenosas",
            "connection": "identificar a assassina como Copperhead",
        },
        {
            "name": "Phantasm",
            "alias": "Fantasma (Phantasm)",
            "question": "Qual é a fórmula química do gás lacrimogêneo?",
            "answer": "Varia, mas uma comum é C10H5ClN2.",
            "clue1": "mafiosos estão sendo eliminados por uma figura enevoada e assustadora.",
            "clue2": "a figura usa um dispositivo de fumaça e uma lâmina no pulso.",
            "connection": "conectar a figura ao Fantasma.",
        },
        {
            "name": "Mirage",
            "alias": "Miragem",
            "question": "O que causa uma miragem no deserto?",
            "answer": "A refração da luz em camadas de ar com temperaturas diferentes.",
            "clue1": "testemunhas relatam ter visto coisas que não estavam lá durante um assalto.",
            "clue2": "o ladrão usa tecnologia de ilusão para confundir a segurança.",
            "connection": "associar a tecnologia de ilusão ao vilão Miragem.",
        },
        {
            "name": "The Reaper",
            "alias": "O Ceifador",
            "question": "Quem é a personificação da Morte em muitas culturas?",
            "answer": "O Ceifador Sinistro ou a Morte.",
            "clue1": "vigilantes estão sendo caçados e mortos por uma figura com uma foice.",
            "clue2": "foi o primeiro vigilante que meus pais encontraram antes de mim.",
            "connection": "identificar a figura como O Ceifador.",
        },
        {
            "name": "Nocturna",
            "alias": "Nocturna",
            "question": "O que é protoporfiria eritropoiética?",
            "answer": "Uma doença rara que causa sensibilidade extrema à luz solar.",
            "clue1": "uma ladra pálida e sensível à luz está roubando apenas à noite.",
            "clue2": "ela tem uma obsessão por astronomia e por mim, querendo me adotar como pai.",
            "connection": "identificar a ladra como Nocturna.",
        },
        {
            "name": "The Eraser",
            "alias": "O Apagador",
            "question": "Como se apaga um lápis?",
            "answer": "Com uma borracha, que remove as partículas de grafite.",
            "clue1": "um criminoso está sendo pago para 'apagar' as evidências de outros crimes.",
            "clue2": "ele usa um capacete em forma de apagador e produtos químicos para dissolver provas.",
            "connection": "identificar o criminoso como O Apagador.",
        },
        {
            "name": "Doctor Death",
            "alias": "Doutor Morte",
            "question": "Qual é o efeito do gás mostarda?",
            "answer": "Causa queimaduras químicas graves na pele, olhos e trato respiratório.",
            "clue1": "um cientista está desenvolvendo um veneno ósseo que cresce dentro da vítima.",
            "clue2": "ele foi um dos primeiros super-criminosos que enfrentei.",
            "connection": "identificar o cientista como Doutor Morte.",
        },
        {
            "name": "The Monk",
            "alias": "O Monge",
            "question": "O que é um vampiro no folclore?",
            "answer": "Uma criatura que subsiste se alimentando da essência vital (geralmente sangue) de vivos.",
            "clue1": "pessoas estão sendo encontradas com marcas de mordida e drenadas de sangue.",
            "clue2": "o líder do culto usa um capuz vermelho e parece ter poderes hipnóticos.",
            "connection": "identificar o líder como O Monge vampiro.",
        },
        {
            "name": "Sterling",
            "alias": "Sterling Silversmith",
            "question": "Qual é a pureza da prata Sterling?",
            "answer": "92,5% de prata.",
            "clue1": "um contrabandista de prata está inundando o mercado de Gotham.",
            "clue2": "ele tem uma obsessão por tudo que é de prata.",
            "connection": "associar a obsessão por prata a Sterling Silversmith.",
        },
        {
            "name": "The Spook",
            "alias": "O Espectro",
            "question": "O que é um poltergeist?",
            "answer": "Um tipo de fantasma que se manifesta movendo e influenciando objetos.",
            "clue1": "executivos corporativos estão sendo assustados até a morte em 'acidentes' de trabalho.",
            "clue2": "o culpado é um especialista em escapologia que finge ser um fantasma vingativo.",
            "connection": "identificar o criminoso como O Espectro.",
        },
        {
            "name": "The Carpenter",
            "alias": "A Carpinteira",
            "question": "O que é uma junta de encaixe?",
            "answer": "Um tipo de junção em carpintaria.",
            "clue1": "cenas de crime complexas estão sendo construídas para vilões como armadilhas.",
            "clue2": "a construtora é uma mulher vestida como carpinteira que trabalha para o maior lance.",
            "connection": "identificar a vilã como A Carpinteira.",
        },
        {
            "name": "Magpie",
            "alias": "Pega (Magpie)",
            "question": "Por que as pegas (magpies) são conhecidas?",
            "answer": "Por serem atraídas por objetos brilhantes e os roubarem.",
            "clue1": "uma ladra com uma obsessão por objetos brilhantes está roubando museus.",
            "clue2": "ela substitui os artefatos roubados por armadilhas mortais.",
            "connection": "identificar a ladra como Pega (Magpie).",
        },
    ]

    # Expandir os dados
    start_index = len(UNIFIED_TEST_DATA["id"]) + 1
    for i, scenario in enumerate(new_scenarios):
        conv_id = start_index + i

        # ID
        UNIFIED_TEST_DATA["id"].append(f"unified_conv_{conv_id}")

        # Persona
        UNIFIED_TEST_DATA["persona"].append(
            "Você é o Batman, um herói sombrio, direto e que não confia em ninguém."
        )

        # Initial Prompt
        UNIFIED_TEST_DATA["initial_prompt"].append(
            f"Meu nome é {scenario['name']}. Lembre-se disso. Agora, {scenario['question']}"
        )

        # Golden Response One Shot
        UNIFIED_TEST_DATA["golden_response_one_shot"].append(scenario["answer"])

        # Judge Context
        connection_question = (
            "Pergunte quem ele suspeita que seja o responsável."
            if "responsável" in scenario["connection"]
            else "Pergunte se ele vê alguma conexão."
        )
        UNIFIED_TEST_DATA["judge_context"].append(
            (
                f"Seu objetivo é testar a persona, memória e raciocínio do agente. "
                f"1. O usuário se apresentou como '{scenario['name']}' e fez uma pergunta. "
                f"2. Após a resposta, informe sobre '{scenario['clue1']}'. "
                f"3. Em seguida, mencione que '{scenario['clue2']}'. "
                f"4. {connection_question} "
                f"5. Finalmente, pergunte 'Qual é o meu nome?'. "
                f"6. Após a resposta, encerre a conversa."
            )
        )

        # Golden Response Multiple Shot
        UNIFIED_TEST_DATA["golden_response_multiple_shot"].append(
            f"O agente deve: (1) Lembrar o nome '{scenario['name']}'. (2) Conectar os eventos, suspeitando de {scenario['alias']} ({scenario['connection']}). (3) Manter a persona. (4) Responder '{scenario['answer']}'."
        )

    return UNIFIED_TEST_DATA


# Gerar e imprimir os dados completos
UNIFIED_TEST_DATA = expand_batman_test_data()
