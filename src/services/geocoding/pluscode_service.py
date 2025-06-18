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
        with
        equipamentos as (
            select
                t.plus8 as plus8_grid,
                eq.plus8,
                eq.plus10,
                eq.plus11,
                cast(eq.distancia_metros as int64) as distancia_metros,
                t.secretaria_responsavel,
                t.categoria,
                eq.tipo_equipamento,
                eq.nome_oficial,
                eq.nome_popular,
                eq.endereco.logradouro,
                eq.endereco.numero,
                eq.endereco.complemento,
                coalesce(eq.bairro.bairro, eq.endereco.bairro) as bairro,
                eq.bairro.regiao_planejamento,
                eq.bairro.regiao_administrativa,
                eq.bairro.subprefeitura,
                eq.contato,
                eq.ativo,
                eq.aberto_ao_publico,
                eq.horario_funcionamento,
                eq.updated_at,
            from `rj-iplanrio.plus_codes.codes` t, unnest(equipamentos) as eq
            where t.plus8 = "{plus8}"
            qualify
                row_number() over (
                    partition by t.plus8, t.secretaria_responsavel, t.categoria
                    order by cast(eq.distancia_metros as int64)
                )
                = 1
        ),

        controle as (
            select distinct
                concat(trim(secretaria_responsavel), "__", trim(tipo)) tipo_controle,
            from `rj-iplanrio.plus_codes.controle_tipos_equipamentos`
            where use = '0'
        )

        select *
        from equipamentos eq
        where
            concat(eq.secretaria_responsavel, "__", eq.categoria)
            not in (select tipo_controle from controle)
        order by eq.secretaria_responsavel, eq.categoria, eq.distancia_metros
    """
    data = get_bigquery_result(query=query)
    return data


async def get_category_equipments():
    query = f"""
        with
            equipamentos as (
                SELECT
                    DISTINCT 
                    secretaria_responsavel,
                    categoria
                FROM `rj-iplanrio.plus_codes.codes`
                WHERE categoria IS NOT NULL
            ),

            controle as (
                select distinct
                    concat(trim(secretaria_responsavel), "__", trim(tipo)) tipo_controle,
                from `rj-iplanrio.plus_codes.controle_tipos_equipamentos`
                where use = '0'
            )

        select *
        from equipamentos eq
        where
            concat(eq.secretaria_responsavel, "__", eq.categoria)
            not in (select tipo_controle from controle)
        order by eq.secretaria_responsavel, eq.categoria
    """
    data = get_bigquery_result(query=query)
    categories = []
    for d in data:
        categories.append(
            {
                "secretaria_responsavel": d["secretaria_responsavel"],
                "categoria": d["categoria"],
            }
        )
    categories.sort()
    return categories


# if __name__ == "__main__":
#     cat = asyncio.run(get_category_equipments())
#     data = asyncio.run(get_pluscode_equipments(address="Avenida Presidente Vargas, 1"))

#     print(cat)
#     print(data)
