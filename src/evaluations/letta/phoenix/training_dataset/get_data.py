import pandas as pd

#path = r"app-eai-agent/src/evaluations/letta/phoenix/training_dataset/exported_typesense_carioca-digital_data.csv"
collection_name = "1746"

#print the path of the file
print(f"the current path is: {__file__}")

df = pd.read_csv(f"/home/brunoalmeida/projects/ed_rio/app-eai-agent/src/evaluations/letta/phoenix/training_dataset/exported_typesense_{collection_name}_data.csv", encoding="utf-8")
# filter where titulo lower is like "iptu"

titulos_list = [
    "Fiscalização de estacionamento irregular de veículo",
"Remoção de entulho e bens inservíveis",
"Reparo de lâmpada apagada",
"Reparo de buraco, deformação ou afundamento na pista",
"Reparo de Luminária",
"Remoção de resíduos no logradouro",
"Manutenção/Desobstrução de ramais de águas pluviais e ralos",
"Poda de árvore em logradouro",
"Verificação de ar condicionado inoperante no ônibus",
"Fiscalização de perturbação do sossego",
"Controle de roedores e caramujos africanos",
"Capina em logradouro",
"Reparo de sinal de trânsito apagado",
"Varrição de logradouro",
"Fiscalização de obras em imóvel privado",
"Reposição de tampão ou grelha",
"Verificação de frequência irregular da coleta domiciliar com retirada do resíduo",
"Resgate de animais silvestres",
"Vistoria em foco de Aedes Aegypti (Dengue, Chikungunya e Zika)",
"Remoção de veículo abandonado em via pública",
"Solicitação de transporte da gestante para a maternidade",
"Vistoria técnica em situações de maus tratos de animais domésticos",
"Fiscalização de comércio ambulante",
"Fiscalização de má conduta do motorista/despachante",
"Remoção de árvore em logradouro",
"Atendimento à pessoas em situação de rua",
"Fiscalização de obstáculo fixo na calçada",
"Fiscalização de atividades econômicas sem alvará",
"Fiscalização de calçadas ou vias públicas obstruídas e uso indevido de equipamento público",
"Reparo de poste alto apagado",
"Vistoria em imóvel com rachadura e infiltração",
"Fiscalização de buraco na calçada",
"Solicitação de orientações sobre o alvará pela internet",
"Reparo de bloco de lâmpadas apagadas",
"Remoção de resíduos de poda",
"Avaliação de risco de queda da árvore",
"Vistoria em ameaça de desabamento de estrutura",
"Fiscalização de má condição do ônibus",
"Solicitação de correção de falhas e de cadastro no portal e app 1746",
"Conservação de bueiros, galerias, ramais de águas pluviais e ralos",
"Limpeza de praças e parques",
"Verificação de escassez ou intervalo irregular das linhas de ônibus",
"Notificação ao proprietário para limpeza de resíduos em terreno baldio",
"Manutenção de mobiliário, brinquedos e equipamentos esportivos em praças e parques públicos",
"Reparo de lâmpada piscando",
"Limpeza de ralos",
"Solicitação de balizamento de trânsito",
"Solicitação de cópia de planta baixa, de corte ou de situação",
]
# if titulo in titulos_list:
#df = df[df['titulo'].isin(titulos_list)]

# print(df.shape)

# print the titles that are not in the dataframe but in the list
# for titulo in titulos_list:
#     if titulo not in df['titulo'].values:
#         print(f'"{titulo}",')

NOT_IN_LIST = [
    "Reparo de lâmpada apagada",
    "Fiscalização de comércio ambulante",
    "Atendimento à pessoas em situação de rua",
    "Fiscalização de calçadas ou vias públicas obstruídas e uso indevido de equipamento público",
    "Reparo de poste alto apagado",
    "Reparo de bloco de lâmpadas apagadas",
    "Conservação de bueiros, galerias, ramais de águas pluviais e ralos",
    "Verificação de escassez ou intervalo irregular das linhas de ônibus",
    "Reparo de lâmpada piscando",
    "Solicitação de cópia de planta baixa, de corte ou de situação",
]

keywords = ["planta"]  # list of strings to check
mask = df['titulo_texto_normalizado'].str.lower().apply(lambda x: all(k in x for k in keywords))
df = df[mask]


for id, titulo in df[['id', 'titulo']].values:
    print(f'id: {id}, titulo: "{titulo}",')
    #print(f'"{titulo}",')
