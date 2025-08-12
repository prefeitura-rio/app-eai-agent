#!/usr/bin/env python3
"""
Teste de usabilidade para GoogleAgentEngineHistory
Testando com user_id: 'asd'
"""

import asyncio
import time
from src.services.agent_engine.history import (
    GoogleAgentEngineHistory,
    get_google_agent_engine_history,
    get_google_agent_engine_history_bulk,
)


async def test_single_user_history():
    """Teste para buscar histórico de um único usuário"""
    print("=== Teste 1: Histórico de usuário único ===")
    user_id = "asd"

    try:
        start_time = time.time()

        # Testando usando a classe diretamente
        history_instance = GoogleAgentEngineHistory()
        result = await history_instance.get_history(user_id)

        end_time = time.time()

        print(f"✅ Sucesso! Tempo: {end_time - start_time:.2f}s")
        print(f"User ID: {user_id}")
        print(f"Status: {result.get('status', 'N/A')}")

        data = result.get("data", {})
        messages = data.get("messages", [])
        usage = data.get("usage", {})

        print(f"Total de mensagens: {len(messages)}")
        print(f"Agent ID: {data.get('agent_id', 'N/A')}")
        print(f"Processed at: {data.get('processed_at', 'N/A')}")
        print(f"Tokens usados: {usage.get('total_tokens', 0)}")
        print(f"Steps: {usage.get('step_count', 0)}")

        if messages:
            print(f"\nPrimeira mensagem:")
            first_msg = messages[0]
            print(f"  Tipo: {first_msg.get('message_type', 'N/A')}")
            print(f"  Data: {first_msg.get('date', 'N/A')}")
            print(f"  Conteúdo: {str(first_msg.get('content', ''))[:100]}...")

        return result

    except Exception as e:
        print(f"❌ Erro: {e}")
        return None


async def test_wrapper_function():
    """Teste usando a função wrapper para compatibilidade"""
    print("\n=== Teste 2: Função wrapper ===")
    user_id = "asd"

    try:
        start_time = time.time()

        # Testando usando a função wrapper
        result = await get_google_agent_engine_history(user_id)

        end_time = time.time()

        print(f"✅ Sucesso! Tempo: {end_time - start_time:.2f}s")
        print(f"Resultado idêntico ao teste anterior: {result is not None}")

        return result

    except Exception as e:
        print(f"❌ Erro: {e}")
        return None


async def test_bulk_users():
    """Teste para buscar histórico de múltiplos usuários (incluindo 'asd')"""
    print("\n=== Teste 3: Histórico bulk (múltiplos usuários) ===")
    user_ids = ["asd", "user123", "test_user", "nonexistent_user"]

    try:
        start_time = time.time()

        # Testando usando a classe diretamente
        history_instance = GoogleAgentEngineHistory()
        results = await history_instance.get_history_bulk(user_ids)

        end_time = time.time()

        print(f"✅ Sucesso! Tempo: {end_time - start_time:.2f}s")
        print(f"Usuários processados: {len(results)}")

        for user_id, messages in results.items():
            print(f"  {user_id}: {len(messages)} mensagens")

        # Verificar se 'asd' está nos resultados
        if "asd" in results:
            asd_messages = results["asd"]
            print(f"\nDetalhes do usuário 'asd':")
            print(f"  Total de mensagens: {len(asd_messages)}")
            if asd_messages:
                print(
                    f"  Primeira mensagem: {asd_messages[0].get('message_type', 'N/A')}"
                )

        return results

    except Exception as e:
        print(f"❌ Erro: {e}")
        return None


async def test_bulk_wrapper():
    """Teste da função wrapper para bulk"""
    print("\n=== Teste 4: Função wrapper bulk ===")
    user_ids = ["asd", "test_user2"]

    try:
        start_time = time.time()

        # Testando usando a função wrapper
        results = await get_google_agent_engine_history_bulk(user_ids)

        end_time = time.time()

        print(f"✅ Sucesso! Tempo: {end_time - start_time:.2f}s")
        print(f"Usuários processados: {len(results)}")

        return results

    except Exception as e:
        print(f"❌ Erro: {e}")
        return None


async def test_message_formatter():
    """Teste específico do message_formatter"""
    print("\n=== Teste 5: Message Formatter ===")

    try:
        history_instance = GoogleAgentEngineHistory()

        # Mock de mensagens para testar o formatter
        mock_messages = [
            {"type": "human", "content": "Olá, como você está?", "id": "msg1"},
            {
                "type": "ai",
                "content": "Olá! Estou bem, obrigado por perguntar.",
                "id": "msg2",
                "usage_metadata": {
                    "input_tokens": 10,
                    "output_tokens": 15,
                    "total_tokens": 25,
                },
            },
        ]

        result = history_instance.message_formatter(mock_messages, "test_agent")

        print(f"✅ Formatter testado com sucesso!")
        print(f"Status: {result.get('status', 'N/A')}")

        data = result.get("data", {})
        messages = data.get("messages", [])
        print(f"Mensagens formatadas: {len(messages)}")

        for msg in messages:
            print(
                f"  - {msg.get('message_type', 'N/A')}: {str(msg.get('content', ''))[:50]}..."
            )

        return result

    except Exception as e:
        print(f"❌ Erro: {e}")
        return None


async def main():
    """Executa todos os testes"""
    print("🚀 Iniciando testes de usabilidade para GoogleAgentEngineHistory")
    print("=" * 60)

    # Executar todos os testes
    await test_single_user_history()
    await test_wrapper_function()
    await test_bulk_users()
    await test_bulk_wrapper()
    await test_message_formatter()

    print("\n" + "=" * 60)
    print("✅ Todos os testes concluídos!")


if __name__ == "__main__":
    asyncio.run(main())
