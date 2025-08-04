"""
Testes de gerenciamento de sessões.
"""

import uuid
from src.services.lang_graph.service import LangGraphChatbotService
from src.utils.log import logger


async def test_session_management():
    """Testa gerenciamento de sessões."""
    logger.info("📋 Executando: Gerenciamento de Sessões")
    logger.info("----------------------------------------")

    # Usar UUID único para evitar contaminação
    test_user_id = str(uuid.uuid4())
    test_thread_id = str(uuid.uuid4())

    try:
        chatbot_service = LangGraphChatbotService()
        logger.info("🎯 Testando gerenciamento de sessões...")

        # Teste 1: Inicialização de sessão
        logger.info("  🚀 Testando inicialização de sessão...")
        session_result = chatbot_service.initialize_session(
            user_id=test_user_id,
            thread_id=test_thread_id,
        )
        logger.info(f"  ✅ Sessão inicializada: {session_result}")

        # Teste 2: Processar mensagem para testar a sessão
        logger.info("  💬 Testando processamento de mensagem com sessão...")
        response = await chatbot_service.process_message(
            user_id=test_user_id,
            thread_id=test_thread_id,
            message="Olá, esta é uma mensagem de teste",
        )
        logger.info(f"  🤖 Resposta: {response.message}")

        # Teste 3: Limpeza de memórias
        logger.info("  🧹 Testando limpeza de memórias...")
        result = chatbot_service.clear_memory(test_user_id)
        if result.get("success"):
            logger.info("  ✅ Memórias limpas com sucesso")
        else:
            logger.info(f"  ❌ Erro ao limpar memórias: {result.get('error_message')}")

        logger.info("  ✅ Gerenciamento de sessões OK")
        return True

    except Exception as e:
        logger.info(f"  ❌ Erro no gerenciamento de sessões: {e}")
        return False
    finally:
        chatbot_service.close()


if __name__ == "__main__":
    import asyncio

    logging.basicConfig(level=logging.INFO)
    asyncio.run(test_session_management())
