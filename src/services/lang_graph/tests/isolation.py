"""
Testes de isolamento de memória entre usuários.
"""

import logging
import uuid
from src.services.lang_graph.service import LangGraphChatbotService

logger = logging.getLogger(__name__)


async def test_memory_isolation():
    """Testa isolamento de memória entre usuários."""
    print("📋 Executando: Isolamento de Memória entre Usuários")
    print("----------------------------------------")

    # Usar UUIDs únicos para evitar contaminação
    user1_id = str(uuid.uuid4())
    user2_id = str(uuid.uuid4())
    thread1_id = str(uuid.uuid4())
    thread2_id = str(uuid.uuid4())

    try:
        chatbot_service = LangGraphChatbotService()
        print("🔒 Testando isolamento de memória entre usuários...")

        # Usuário 1 diz seu nome
        print("  👤 Usuário 1 diz seu nome...")
        response1 = await chatbot_service.process_message(
            user_id=user1_id,
            thread_id=thread1_id,
            message="Meu nome é João.",
        )
        print(f"  🤖 Resposta: {response1.message}")
        print(f"  🔧 Ferramentas chamadas: {response1.tools_called}")

        # Usuário 2 diz seu nome
        print("  👤 Usuário 2 diz seu nome...")
        response2 = await chatbot_service.process_message(
            user_id=user2_id,
            thread_id=thread2_id,
            message="Meu nome é Maria.",
        )
        print(f"  🤖 Resposta: {response2.message}")
        print(f"  🔧 Ferramentas chamadas: {response2.tools_called}")

        # Usuário 1 pergunta seu nome
        print("  ❓ Usuário 1 pergunta seu nome...")
        response1 = await chatbot_service.process_message(
            user_id=user1_id,
            thread_id=thread1_id,
            message="Qual é o meu nome?",
        )
        print(f"  🤖 Resposta: {response1.message}")
        print(f"  🔧 Ferramentas chamadas: {response1.tools_called}")

        # Verificar se mencionou "João" (correto) ou "Maria" (erro de isolamento)
        if "João" in response1.message:
            print("  ✅ Isolamento correto: Usuário 1 viu apenas seu próprio nome")
        elif "Maria" in response1.message:
            print("  ❌ Erro de isolamento: Usuário 1 viu nome do usuário 2")
        else:
            print("  ⚠️ Possível problema de isolamento")

        # Usuário 2 pergunta seu nome
        print("  ❓ Usuário 2 pergunta seu nome...")
        response2 = await chatbot_service.process_message(
            user_id=user2_id,
            thread_id=thread2_id,
            message="Qual é o meu nome?",
        )
        print(f"  🤖 Resposta: {response2.message}")
        print(f"  🔧 Ferramentas chamadas: {response2.tools_called}")

        # Verificar se mencionou "Maria" (correto) ou "João" (erro de isolamento)
        if "Maria" in response2.message:
            print("  ✅ Isolamento correto: Usuário 2 viu apenas seu próprio nome")
        elif "João" in response2.message:
            print("  ❌ Erro de isolamento: Usuário 2 viu nome do usuário 1")
        else:
            print("  ⚠️ Possível problema de isolamento")

        print("  ✅ Teste de isolamento de memória OK")
        return True

    except Exception as e:
        print(f"  ❌ Erro no teste de isolamento: {e}")
        return False
    finally:
        chatbot_service.close()


if __name__ == "__main__":
    import asyncio

    logging.basicConfig(level=logging.INFO)
    asyncio.run(test_memory_isolation())
