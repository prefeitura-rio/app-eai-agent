import json

print(
    json.dumps(
        {
            "ideal_response": """Para pagar o IPTU no Rio de Janeiro, a forma mais comum e recomendada é através do portal *Carioca Digital*.

Você pode acessar o portal pelo link: https://carioca.rio

No portal, você pode emitir a 2ª via da guia e as cotas.

*Importante*:
*   A Prefeitura do Rio não envia boletos de IPTU por WhatsApp ou SMS, exceto via canal oficial 1746 para alguns serviços.
*   O pagamento via PIX é aceito, mas apenas através do QR Code gerado no portal Carioca Digital.
*   Fique atento a golpes e utilize apenas os canais oficiais.

Existem outras opções como pagamento em débito automático, parcelamento de débitos anteriores e atendimento presencial.

Gostaria de detalhes sobre alguma dessas outras formas ou informações, como parcelamento ou atendimento presencial?

_Informações e datas podem mudar. Confira sempre o link oficial._"""
        },
        ensure_ascii=False,
    )
)
