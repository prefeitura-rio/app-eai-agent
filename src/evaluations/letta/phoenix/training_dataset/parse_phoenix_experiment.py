# import json
# import re
# import ast


# def parse_links(input_string):
#     # Dicionário para armazenar o resultado
#     parsed_dict = {}
#     pattern = re.compile(r"(.+?):\s*(.*?)(?=\n[A-Z][a-z]+ [a-z]+:|$)", re.DOTALL)
#     matches = pattern.findall(input_string)

#     for key, value in matches:
#         clean_key = key.strip().lower().replace(" ", "_")
#         parsed_value = ast.literal_eval(value.strip())
#         parsed_dict[clean_key] = parsed_value

#     if "match_found" in parsed_dict:
#         parsed_dict["math_found"] = parsed_dict.pop("match_found")

#     return parsed_dict


# data = json.load(open("/Users/m/Downloads/eai-2025-06-30.json"))

# for item in data[7:8]:
#     output = item["output"]
#     input = item["input"]
#     annotations = item["annotations"]

#     separator = "=" * 100

#     print(separator)
#     print("ID: ", output["metadata"]["id"], "\n")
#     print("Mensagem:\n", input["mensagem_whatsapp_simulada"], "\n")
#     print(
#         "Resposta:\n",
#         output["agent_output"]["grouped"]["assistant_messages"][0]["content"],
#         "\n",
#     )
#     show_annotations = [
#         "Golden Link in Tool Calling",
#         "Golden Link in Answer",
#         "Answer Similarity",
#     ]
#     for annotation in annotations:
#         if annotation["name"] in show_annotations:
#             print("-" * 100, "\n")
#             print(annotation["name"], "\n")
#             print("Score: ", annotation["score"], "\n")

#             if "Link" in annotation["name"] and annotation["score"] == 1:
#                 d = parse_links(input_string=annotation["explanation"])
#                 print(d)
#             else:
#                 print(
#                     "Explanation: ",
#                     annotation["explanation"].replace("\\n", "\n"),
#                     "\n",
#                 )
#     print(separator)


from src.evaluations.letta.phoenix.training_dataset.evaluators import _norm_url


explanation_links = [
    {
        "url": "https://prefeitura.rio/saude/prefeitura-inaugura-centro-especializado-para-pessoas-com-autismo",
        "uri": "https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF6q2x0wzvydKRDa3NTkL0-lk3pTuZaSZAovM7qR2JcqmmVPntEzNW8i1EJEb9t2p6UCy2yTBOmEgdYH2K_9UYMVhR6JbnG4QT-O-WKVV1uMFVRyjeb_zJa5Rm41V9hvzgWrbUFAZm9JREqAVW9AfTA_B4bzibCHbR7TYFdAHLd_gPd6TvrXGUaD1S63IbVTCmJIVf_ANKLYVZ-",
        "error": None,
    },
    {
        "url": None,
        "uri": "https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGuFM6QXd_yHmOMUILGrMren8g6I14FTLORMoriG-y0KvOWcpslVDc14ksCLMAhSHmTfkCSyZ-caI9KSNT31Uwtz_J-1jaeVZ4zqn9QcsfAZoM_EYpSTxrUCE9pwI8SJ6O6ReSV8TRmN5LvKQcwjhb360CNtgRLj2WaWwS2taFvKtjkA_gikEtt-dNKOSKEfvBXAbRBINfGTU9y3nw-fGWlLvkab5VZm6vA1flAg-hR",
        "error": "Client error '403 Forbidden' for url 'https://agenciabrasil.ebc.com.br/saude/noticia/2023-07/rio-de-janeiro-cria-programa-de-descoberta-precoce-do-autismo'\nFor more information check: https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/403",
    },
    {
        "url": None,
        "uri": "https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG9Z3w623XYzVFI7jL7NG-DV_aajAaOElfrCSxWs8RS0xi3VhIuvEYpnGKHQl7U83Y6Sv3nY8C7R3Es-UgVrebVs73_qQ-ZEdnYIhCVGE5cYnCSyqR01VDlOBI3nD-5tqgThOKRyMQDzI1XeLIJ_L6uaR6P8t8O81afnmoHAQrJUTmI8VNvo9IqBV-QmDlVojTTFNw7wZT2wTmjUXO5wVj0JxiJj6gQxuuN-PA0MWiW4y3zSbptLXnB4a3HRtzCIuVV",
        "error": "",
    },
    {
        "url": "https://prefeitura.rio/cidade/evento-com-acoes-de-diversas-secretarias-no-planetario-lembra-o-dia-mundial-de-conscientizacao-do-autismo/",
        "uri": "https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHZQf0rcpmkB5XhhwVv4OUyrzUSUuwTY0cIrLUGs2HTmUnKsPf9rqdF8b-6E9eS6yDFJvGjr17smy3QUdHHQ-8e56HI378UqqOJhgwJVTaufp3aTuhV_Y9eFyCBFM15dITzKdSAVouG5mg7d7hrgqbfS5V8jSqyt2HxSXE1NhLIuoeiW_DH48kgk3iZA0ihzJ1lMfzDRVtiAd_4dspGuO6VmxlHX-urewzPHVG8jwhQtxOBZzgq42d4O83cQyKceWJpNE1H",
        "error": None,
    },
]
golden_links = [
    "https://prefeitura.rio/saude/prefeitura-inaugura-centro-especializado-para-pessoas-com-autismo/",
    "https://prefeitura.rio/cidade/evento-com-acoes-de-diversas-secretarias-no-planetario-lembra-o-dia-mundial-de-conscientizacao-do-autismo",
]


def match_golden_link(explanation_links, golden_links):
    """
    Match golden links in explanation links.
    """
    overall_count = 0
    for answer_link in explanation_links:
        url = _norm_url(answer_link.get("url"))
        url = None if url == "" else url
        answer_link["url"] = url

        count = 0
        golden_found = None
        for golden_link in golden_links:
            if str(url) in _norm_url(golden_link):
                answer_link["has_golden_link"] = True
                count += 1
                overall_count += 1
                golden_found = _norm_url(golden_link)

        answer_link["golden_link"] = golden_found
        answer_link["has_golden_link"] = True if count > 0 else False

    explanation_links = [
        {
            "has_golden_link": item.get("has_golden_link"),
            "golden_link": item.get("golden_link"),
            "url": item.get("url"),
            "uri": item.get("uri"),
            "error": item.get("error"),
        }
        for item in explanation_links
    ]
    return explanation_links, overall_count
