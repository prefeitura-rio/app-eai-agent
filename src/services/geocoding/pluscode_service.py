import json

from google.cloud.bigquery.table import Row

from src.services.geocoding.utils import (
    CustomJSONEncoder,
    geocode_address_to_plus8,
    get_bigquery_client,
)
from src.config import env as config


def get_bigquery_result(query: str):
    bq_client = get_bigquery_client()
    query_job = bq_client.query(query)
    result = query_job.result(page_size=config.GOOGLE_BIGQUERY_PAGE_SIZE)
    data = []
    for page in result.pages:
        for row in page:
            row: Row
            row_data = dict(row.items())
            data.append(row_data)

    data_str = json.dumps(data, cls=CustomJSONEncoder, indent=2, ensure_ascii=False)

    return json.loads(data_str)


async def get_pluscode_equipments(address):
    plus8 = geocode_address_to_plus8(address=address)
    query = f"""
            SELECT
                eq.plus8,
                eq.plus10,
                eq.plus11,
                t.categoria,
                eq.secretaria_responsavel,
                eq.nome_oficial,
                eq.nome_popular,
                eq.endereco.logradouro,
                eq.endereco.numero,
                eq.endereco.complemento,
                COALESCE(eq.bairro.bairro, eq.endereco.bairro) as bairro,
                eq.bairro.regiao_planejamento,
                eq.bairro.regiao_administrativa,
                eq.bairro.subprefeitura,
                eq.contato,
                eq.ativo,
                eq.aberto_ao_publico,
                eq.horario_funcionamento,
                eq.update_at
            FROM `rj-iplanrio.plus_codes.codes` t, unnest(equipamentos) as eq
        WHERE t.plus8 = "{plus8}"
    """
    data = get_bigquery_result(query=query)
    return data


async def get_category_equipments():
    query = f"""
        SELECT
            DISTINCT categoria
        FROM `rj-iplanrio.plus_codes.codes`
        WHERE categoria IS NOT NULL
    """
    data = get_bigquery_result(query=query)
    categories = []
    for d in data:
        categories.append(d["categoria"])

    return categories


# if __name__ == "__main__":
#     cat = asyncio.run(get_category_equipments())
#     data = asyncio.run(get_pluscode_equipments(address="Avenida Presidente Vargas, 1"))

#     print(cat)
#     print(data)
