import json


data = json.load(open("/Users/m/Downloads/eai-2025-06-30.json"))

for item in data[:1]:
    output = item["output"]
    input = item["input"]
    annotations = item["annotations"]

    separator = "=" * 100

    print(separator)
    print("ID: ", output["metadata"]["id"], "\n")
    print("Mensagem:\n", input["mensagem_whatsapp_simulada"], "\n")
    print(
        "Resposta:\n",
        output["agent_output"]["grouped"]["assistant_messages"][0]["content"],
        "\n",
    )
    show_annotations = [
        "Golden Link in Tool Calling",
        "Golden Link in Answer",
        "Answer Similarity",
    ]
    for annotation in annotations:
        if annotation["name"] in show_annotations:
            print("-" * 100, "\n")
            print(annotation["name"], "\n")
            print("Score: ", annotation["score"], "\n")
            print("Explanation: ", annotation["explanation"].replace("\\n", "\n"), "\n")
    print(separator)
