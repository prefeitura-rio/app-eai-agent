# -*- coding: utf-8 -*-

UNIFIED_TEST_DATA = {
    "id": [
        "unified_conv_1",
        "unified_conv_2",
        "unified_conv_3",
        "unified_conv_4",
        "unified_conv_5",
    ],
    "initial_prompt": [
        # Task 1: Teste de Raciocínio e Memória com Vilão
        "Meu nome é Dr. Crane. Lembre-se disso. Agora, qual é a capital da França?",
        # Task 2: Teste de Raciocínio Dedutivo e Memória com Aliada/Antagonista
        "Meu nome é Selina. Lembre-se disso. Agora, quanto é 2 + 2?",
        # Task 3: Teste de Conexão de Eventos e Memória
        "Meu nome é Oswald. Lembre-se disso. Agora, qual o maior oceano do mundo?",
        # Task 4: Teste de Identificação de Padrão e Memória
        "Meu nome é Edward. Lembre-se disso. Agora, o que é H2O?",
        # Task 5: Teste de Avaliação de Ameaça e Memória
        "Meu nome é Harleen. Lembre-se disso. Agora, qual a cor do céu em um dia claro?",
    ],
    "persona": [
        "Você é o Batman, um herói sombrio, direto e que não confia em ninguém."
    ]
    * 5,
    # --- Para a condução da conversa ---
    "judge_context": [
        # Contexto 1
        (
            "Seu objetivo é conduzir uma conversa para testar a persona, memória e raciocínio do agente. "
            "1. O usuário já se apresentou como 'Dr. Crane' e fez uma pergunta factual. "
            "2. Após a resposta, informe sobre um 'roubo de produtos químicos na Ace Chemicals'. "
            "3. Em seguida, pergunte sobre uma 'nova toxina do medo' em Gotham. "
            "4. Depois, pergunte diretamente se os eventos podem estar relacionados. "
            "5. Finalmente, pergunte 'Qual é o meu nome?'. "
            "6. Após a resposta final do agente, encerre a conversa."
        ),
        # Contexto 2
        (
            "Seu objetivo é testar a persona, memória e raciocínio do agente. "
            "1. O usuário se apresentou como 'Selina' e fez uma pergunta simples. "
            "2. Após a resposta, informe sobre o 'roubo do colar de diamantes da Sra. Vandergilt'. "
            "3. Em seguida, mencione 'avistamentos da Mulher-Gato perto da joalheria'. "
            "4. Pergunte se ele acha que os eventos estão conectados. "
            "5. Finalmente, pergunte 'Qual é o meu nome?'. "
            "6. Após a resposta, encerre a conversa."
        ),
        # Contexto 3
        (
            "Seu objetivo é testar a persona, memória e raciocínio do agente. "
            "1. O usuário se apresentou como 'Oswald' e fez uma pergunta factual. "
            "2. Após a resposta, informe que 'todos os peixes do porto de Gotham desapareceram'. "
            "3. Em seguida, comente sobre a 'grande inauguração do novo Iceberg Lounge do Pinguim'. "
            "4. Pergunte se ele vê alguma conexão. "
            "5. Finalmente, pergunte 'Qual é o meu nome?'. "
            "6. Após a resposta, encerre a conversa."
        ),
        # Contexto 4
        (
            "Seu objetivo é testar a persona, memória e raciocínio do agente. "
            "1. O usuário se apresentou como 'Edward' e fez uma pergunta factual. "
            "2. Após a resposta, informe sobre um 'apagão geral no distrito financeiro'. "
            "3. Em seguida, mencione que 'símbolos de charadas verdes foram pichados nos transformadores'. "
            "4. Pergunte quem ele suspeita que seja o responsável. "
            "5. Finalmente, pergunte 'Qual é o meu nome?'. "
            "6. Após a resposta, encerre a conversa."
        ),
        # Contexto 5
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
    # --- Para o julgamento final (múltiplos juízes usarão isso) ---
    "golden_response_multiple_shot": [
        # Sumário 1
        "O agente deve: (1) Lembrar o nome 'Dr. Crane' e mostrar desconfiança. (2) Conectar o roubo e a toxina, suspeitando do Espantalho/Coringa. (3) Manter a persona. (4) Responder 'Paris'.",
        # Sumário 2
        "O agente deve: (1) Lembrar o nome 'Selina'. (2) Conectar o roubo de joias aos avistamentos da Mulher-Gato. (3) Manter a persona. (4) Responder '4'.",
        # Sumário 3
        "O agente deve: (1) Lembrar o nome 'Oswald'. (2) Conectar o desaparecimento dos peixes ao novo restaurante do Pinguim. (3) Manter a persona. (4) Responder 'Oceano Pacífico'.",
        # Sumário 4
        "O agente deve: (1) Lembrar o nome 'Edward'. (2) Conectar o apagão e os símbolos ao Charada. (3) Manter a persona. (4) Responder 'Água'.",
        # Sumário 5
        "O agente deve: (1) Lembrar o nome 'Harleen' e suspeitar da conexão com o Coringa. (2) Conectar a fuga do Coringa com o parque de diversões como uma armadilha. (3) Manter a persona. (4) Responder 'Azul'.",
    ],
    # --- Para a avaliação de turno único (semantic_correctness) ---
    "golden_response_one_shot": [
        "Paris.",
        "4.",
        "Oceano Pacífico.",
        "Água.",
        "Azul.",
    ],
}
