"""
Testes de conversação do chatbot.
"""

import uuid
from src.services.lang_graph.service import LangGraphChatbotService

from src.utils.log import logger


async def test_chatbot_conversation():
    """Testa conversação básica do chatbot."""
    logger.info("📋 Executando: Conversação do Chatbot")
    logger.info("----------------------------------------")

    # Usar UUID único para evitar contaminação
    test_user_id = str(uuid.uuid4())
    test_thread_id = str(uuid.uuid4())

    try:
        chatbot_service = LangGraphChatbotService()
        logger.info("💬 Testando conversação do chatbot...")

        # Teste 1: Mensagem simples
        logger.info("  💭 Testando mensagem simples...")
        response = await chatbot_service.process_message(
            user_id=test_user_id,
            thread_id=test_thread_id,
            message="Olá, como você está?",
        )
        logger.info(f"  🤖 Resposta: {response.message}")
        logger.info(f"  📊 Memórias usadas: {len(response.memories_used)}")
        logger.info(f"  🔧 Ferramentas chamadas: {response.tools_called}")

        # Teste 2: Mensagem com informação para salvar
        logger.info("  💾 Testando mensagem com informação para salvar...")
        response = await chatbot_service.process_message(
            user_id=test_user_id,
            thread_id=test_thread_id,
            message="Meu nome é João e eu moro em São Paulo",
        )
        logger.info(f"  🤖 Resposta: {response.message}")
        logger.info(f"  📊 Memórias usadas: {len(response.memories_used)}")
        logger.info(f"  🔧 Ferramentas chamadas: {response.tools_called}")

        # Teste 3: Uso de memória
        logger.info("  🧠 Testando uso de memória...")
        response = await chatbot_service.process_message(
            user_id=test_user_id,
            thread_id=test_thread_id,
            message="Qual é o meu nome?",
        )
        logger.info(f"  🤖 Resposta: {response.message}")
        logger.info(f"  📊 Memórias usadas: {len(response.memories_used)}")
        logger.info(f"  🔧 Ferramentas chamadas: {response.tools_called}")

        logger.info("  ✅ Conversação do chatbot OK")
        return True

    except Exception as e:
        logger.info(f"  ❌ Erro na conversação do chatbot: {e}")
        return False
    finally:
        chatbot_service.close()


if __name__ == "__main__":
    import asyncio

    logging.basicConfig(level=logging.INFO)
    asyncio.run(test_chatbot_conversation())
