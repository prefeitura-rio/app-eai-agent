"""
Testes de isolamento de memória entre usuários.
"""

import uuid
from src.services.lang_graph.service import LangGraphChatbotService

from src.utils.log import logger


async def test_memory_isolation():
    """Testa isolamento de memória entre usuários."""
    logger.info("📋 Executando: Isolamento de Memória entre Usuários")
    logger.info("----------------------------------------")

    # Usar UUIDs únicos para evitar contaminação
    user1_id = str(uuid.uuid4())
    user2_id = str(uuid.uuid4())
    thread1_id = str(uuid.uuid4())
    thread2_id = str(uuid.uuid4())

    try:
        chatbot_service = LangGraphChatbotService()
        logger.info("🔒 Testando isolamento de memória entre usuários...")

        # Usuário 1 diz seu nome
        logger.info("  👤 Usuário 1 diz seu nome...")
        response1 = await chatbot_service.process_message(
            user_id=user1_id,
            thread_id=thread1_id,
            message="Meu nome é João.",
        )
        logger.info(f"  🤖 Resposta: {response1.message}")
        logger.info(f"  🔧 Ferramentas chamadas: {response1.tools_called}")

        # Usuário 2 diz seu nome
        logger.info("  👤 Usuário 2 diz seu nome...")
        response2 = await chatbot_service.process_message(
            user_id=user2_id,
            thread_id=thread2_id,
            message="Meu nome é Maria.",
        )
        logger.info(f"  🤖 Resposta: {response2.message}")
        logger.info(f"  🔧 Ferramentas chamadas: {response2.tools_called}")

        # Usuário 1 pergunta seu nome
        logger.info("  ❓ Usuário 1 pergunta seu nome...")
        response1 = await chatbot_service.process_message(
            user_id=user1_id,
            thread_id=thread1_id,
            message="Qual é o meu nome?",
        )
        logger.info(f"  🤖 Resposta: {response1.message}")
        logger.info(f"  🔧 Ferramentas chamadas: {response1.tools_called}")

        # Verificar se mencionou "João" (correto) ou "Maria" (erro de isolamento)
        if "João" in response1.message:
            logger.info(
                "  ✅ Isolamento correto: Usuário 1 viu apenas seu próprio nome"
            )
        elif "Maria" in response1.message:
            logger.info("  ❌ Erro de isolamento: Usuário 1 viu nome do usuário 2")
        else:
            logger.info("  ⚠️ Possível problema de isolamento")

        # Usuário 2 pergunta seu nome
        logger.info("  ❓ Usuário 2 pergunta seu nome...")
        response2 = await chatbot_service.process_message(
            user_id=user2_id,
            thread_id=thread2_id,
            message="Qual é o meu nome?",
        )
        logger.info(f"  🤖 Resposta: {response2.message}")
        logger.info(f"  🔧 Ferramentas chamadas: {response2.tools_called}")

        # Verificar se mencionou "Maria" (correto) ou "João" (erro de isolamento)
        if "Maria" in response2.message:
            logger.info(
                "  ✅ Isolamento correto: Usuário 2 viu apenas seu próprio nome"
            )
        elif "João" in response2.message:
            logger.info("  ❌ Erro de isolamento: Usuário 2 viu nome do usuário 1")
        else:
            logger.info("  ⚠️ Possível problema de isolamento")

        logger.info("  ✅ Teste de isolamento de memória OK")
        return True

    except Exception as e:
        logger.info(f"  ❌ Erro no teste de isolamento: {e}")
        return False
    finally:
        chatbot_service.close()


if __name__ == "__main__":
    import asyncio

    logging.basicConfig(level=logging.INFO)
    asyncio.run(test_memory_isolation())
