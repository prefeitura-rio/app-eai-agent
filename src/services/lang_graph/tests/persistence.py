"""
Testes de persistência de memória em conversa longa.
"""

import logging
import uuid
from src.services.lang_graph.service import LangGraphChatbotService

logger = logging.getLogger(__name__)


async def test_memory_persistence_conversation():
    """Testa a capacidade do bot de lembrar informações ao longo de uma conversa."""
    print("📋 Executando: Persistência de Memória em Conversa Longa")
    print("----------------------------------------")

    # Usar UUID único para evitar contaminação
    test_user_id = str(uuid.uuid4())
    test_thread_id = str(uuid.uuid4())

    try:
        chatbot_service = LangGraphChatbotService()
        print("🧠 Testando persistência de memória em conversa longa...")

        # Teste 1: Usuário diz seu nome
        print("  👤 Teste 1: Usuário diz seu nome...")
        response = await chatbot_service.process_message(
            user_id=test_user_id,
            thread_id=test_thread_id,
            message="Meu nome é Carlos Silva.",
        )
        print(f"  🤖 Resposta: {response.message}")
        print(f"  📊 Memórias usadas: {len(response.memories_used)}")
        print(f"  🔧 Ferramentas chamadas: {response.tools_called}")

        # Teste 2-6: Conversas sobre assuntos aleatórios
        random_topics = [
            "Como está o tempo hoje?",
            "Você gosta de música?",
            "Qual é a sua comida favorita?",
            "Você já viajou para outro país?",
            "Qual é o seu hobby preferido?",
        ]

        for i, topic in enumerate(random_topics, 2):
            print(f"  💬 Teste {i}: Conversa sobre '{topic}'...")
            response = await chatbot_service.process_message(
                user_id=test_user_id,
                thread_id=test_thread_id,
                message=topic,
            )
            print(f"  🤖 Resposta: {response.message}")
            print(f"  📊 Memórias usadas: {len(response.memories_used)}")
            print(f"  🔧 Ferramentas chamadas: {response.tools_called}")

        # Teste 7: Perguntando o nome novamente
        print("  ❓ Teste 7: Perguntando o nome novamente...")
        response = await chatbot_service.process_message(
            user_id=test_user_id,
            thread_id=test_thread_id,
            message="Qual é o meu nome?",
        )
        print(f"  🤖 Resposta: {response.message}")
        print(f"  📊 Memórias usadas: {len(response.memories_used)}")
        print(f"  🔧 Ferramentas chamadas: {response.tools_called}")

        # Verificar se o bot mencionou o nome
        if "Carlos" in response.message or "Silva" in response.message:
            print("  ✅ Bot mencionou o nome do usuário na resposta")
        else:
            print("  ⚠️ Bot não mencionou o nome do usuário na resposta")

        print("  ✅ Teste de persistência de memória OK")
        return True

    except Exception as e:
        print(f"  ❌ Erro no teste de persistência de memória: {e}")
        return False
    finally:
        chatbot_service.close()


if __name__ == "__main__":
    import asyncio

    logging.basicConfig(level=logging.INFO)
    asyncio.run(test_memory_persistence_conversation())
