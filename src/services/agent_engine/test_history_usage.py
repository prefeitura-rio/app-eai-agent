#!/usr/bin/env python3
"""
Teste de usabilidade para GoogleAgentEngineHistory
Testando com user_id: 'asd'
"""

import asyncio
import time
import json
from src.services.agent_engine.history import (
    GoogleAgentEngineHistory,
)


async def test_bulk_users():
    """Teste para buscar histórico de múltiplos usuários (incluindo 'asd')"""
    print("\n=== Teste 1: Histórico bulk (múltiplos usuários) ===")
    user_ids = ["hahahahahaha1"]

    try:
        start_time = time.time()

        # Testando usando a classe diretamente com context manager
        async with GoogleAgentEngineHistory.create() as history_instance:
            results = await history_instance.get_history_bulk(
                user_ids=user_ids, session_timeout_seconds=10, use_whatsapp_format=True
            )

        end_time = time.time()

        print(f"✅ Sucesso! Tempo: {end_time - start_time:.2f}s")
        print(f"Usuários processados: {len(results)}")

        for user_id, messages in results.items():
            print(f"  {user_id}: {len(messages)} mensagens")

        return results

    except Exception as e:
        print(f"❌ Erro: {e}")
        return None


async def test_get_thread_ids():
    """Teste para buscar thread_ids"""
    print("\n=== Teste 2: Thread IDs ===")
    async with GoogleAgentEngineHistory.create() as history_instance:
        results = await history_instance.get_history_bulk_from_last_update(
            last_update="2025-08-15"
        )
    return results


async def test_delete_user_history():
    """Teste para buscar thread_ids"""
    print("\n=== Teste 3: Delete Thread IDs ===")
    async with GoogleAgentEngineHistory.create() as history_instance:
        results = await history_instance.delete_user_history(user_id="663509127")
    return results


async def main():
    """Executa todos os testes"""
    print("🚀 Iniciando testes de usabilidade para GoogleAgentEngineHistory")
    print("=" * 60)
    results = await test_delete_user_history()
    print(results)

    # results = await test_bulk_users()
    # json.dump(
    #     results,
    #     open("./src/services/agent_engine/history.json", "w"),
    #     indent=4,
    #     ensure_ascii=False,
    # )
    # print("\n" + "=" * 60)
    # Executar todos os testes
    # results = await test_get_thread_ids()
    # print("\n" + "=" * 60)

    # json.dump(
    #     results,
    #     open("./src/services/agent_engine/bq_payload.json", "w"),
    #     indent=4,
    #     ensure_ascii=False,
    # )


if __name__ == "__main__":
    asyncio.run(main())
