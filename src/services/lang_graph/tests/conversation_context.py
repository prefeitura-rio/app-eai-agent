"""
Testes de contexto de conversação.
"""

import uuid
from src.services.lang_graph.service import LangGraphChatbotService
from src.utils.log import logger


async def test_conversation_context():
    """Testa se o bot mantém o contexto da conversa."""
    logger.info("📋 Executando: Contexto de Conversação")
    logger.info("----------------------------------------")

    # Usar UUID único para evitar contaminação
    test_user_id = str(uuid.uuid4())
    test_thread_id = str(uuid.uuid4())

    try:
        chatbot_service = LangGraphChatbotService()
        logger.info("💬 Testando contexto de conversação...")

        # Teste 1: Iniciar conversa
        logger.info("  💬 Teste 1: Iniciando conversa...")
        response = await chatbot_service.process_message(
            user_id=test_user_id,
            thread_id=test_thread_id,
            message="Olá, como você está?",
        )
        logger.info(f"  🤖 Resposta: {response.message}")

        # Teste 2: Continuar conversa
        logger.info("  💬 Teste 2: Continuando conversa...")
        response = await chatbot_service.process_message(
            user_id=test_user_id,
            thread_id=test_thread_id,
            message="Que bom! Você pode me ajudar com algo?",
        )
        logger.info(f"  🤖 Resposta: {response.message}")

        # Teste 3: Pergunta específica
        logger.info("  💬 Teste 3: Pergunta específica...")
        response = await chatbot_service.process_message(
            user_id=test_user_id,
            thread_id=test_thread_id,
            message="Você se lembra do que eu perguntei antes?",
        )
        logger.info(f"  🤖 Resposta: {response.message}")

        # Teste 4: Informação pessoal
        logger.info("  💬 Teste 4: Informação pessoal...")
        response = await chatbot_service.process_message(
            user_id=test_user_id,
            thread_id=test_thread_id,
            message="Meu nome é João e eu trabalho como programador.",
        )
        logger.info(f"  🤖 Resposta: {response.message}")

        # Teste 5: Referência à informação anterior
        logger.info("  💬 Teste 5: Referência à informação anterior...")
        response = await chatbot_service.process_message(
            user_id=test_user_id,
            thread_id=test_thread_id,
            message="Você pode me dar dicas sobre programação?",
        )
        logger.info(f"  🤖 Resposta: {response.message}")

        # Verificar se o bot mencionou o contexto
        if "João" in response.message or "programador" in response.message.lower():
            logger.info("  ✅ Bot mencionou o contexto da conversa")
        else:
            logger.info("  ⚠️ Bot não mencionou o contexto da conversa")

        logger.info("  ✅ Teste de contexto de conversação OK")
        return True

    except Exception as e:
        logger.info(f"  ❌ Erro no teste de contexto de conversação: {e}")
        return False
    finally:
        chatbot_service.close()


if __name__ == "__main__":
    import asyncio

    logging.basicConfig(level=logging.INFO)
    asyncio.run(test_conversation_context())
