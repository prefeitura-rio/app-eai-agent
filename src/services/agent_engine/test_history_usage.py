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
    print("\n=== Teste 3: Histórico bulk (múltiplos usuários) ===")
    user_ids = ["1154af1a-7bf6-441d-ae06-4590a66c0d3d-3"]

    try:
        start_time = time.time()

        # Testando usando a classe diretamente
        history_instance = await GoogleAgentEngineHistory.create()
        results = await history_instance.get_history_bulk(
            user_ids=user_ids, session_timeout_seconds=10
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


async def main():
    """Executa todos os testes"""
    print("🚀 Iniciando testes de usabilidade para GoogleAgentEngineHistory")
    print("=" * 60)

    # Executar todos os testes
    results = await test_bulk_users()
    print("\n" + "=" * 60)
    print("✅ Todos os testes concluídos!")
    # print(json.dumps(results, indent=4, ensure_ascii=False))
    json.dump(
        results,
        open("./src/services/agent_engine/results_refactor.json", "w"),
        indent=4,
        ensure_ascii=False,
    )


if __name__ == "__main__":
    asyncio.run(main())
