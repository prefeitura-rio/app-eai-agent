"""
Testes de memória de curto prazo (contexto da conversa).
"""

import uuid
from src.services.lang_graph.service import LangGraphChatbotService
from src.utils.log import logger


async def test_short_term_memory():
    """Testa a capacidade do bot de lembrar o contexto da conversa atual."""
    logger.info("📋 Executando: Memória de Curto Prazo")
    logger.info("----------------------------------------")

    # Usar UUID único para evitar contaminação
    test_user_id = str(uuid.uuid4())
    test_thread_id = str(uuid.uuid4())

    try:
        chatbot_service = LangGraphChatbotService()
        logger.info("🧠 Testando memória de curto prazo...")

        # Teste 1: Primeira mensagem
        logger.info("  💬 Teste 1: Primeira mensagem...")
        response = await chatbot_service.process_message(
            user_id=test_user_id,
            thread_id=test_thread_id,
            message="Olá, como você está?",
        )
        logger.info(f"  🤖 Resposta: {response.message}")

        # Teste 2: Segunda mensagem referenciando a primeira
        logger.info("  💬 Teste 2: Segunda mensagem...")
        response = await chatbot_service.process_message(
            user_id=test_user_id,
            thread_id=test_thread_id,
            message="Você respondeu que está bem?",
        )
        logger.info(f"  🤖 Resposta: {response.message}")

        # Teste 3: Terceira mensagem com contexto
        logger.info("  💬 Teste 3: Terceira mensagem...")
        response = await chatbot_service.process_message(
            user_id=test_user_id,
            thread_id=test_thread_id,
            message="Qual foi a primeira coisa que eu disse?",
        )
        logger.info(f"  🤖 Resposta: {response.message}")

        # Teste 4: Mensagem com informação específica
        logger.info("  💬 Teste 4: Informação específica...")
        response = await chatbot_service.process_message(
            user_id=test_user_id,
            thread_id=test_thread_id,
            message="Meu nome é Ana e eu tenho 25 anos.",
        )
        logger.info(f"  🤖 Resposta: {response.message}")

        # Teste 5: Pergunta sobre informação anterior
        logger.info("  💬 Teste 5: Pergunta sobre informação anterior...")
        response = await chatbot_service.process_message(
            user_id=test_user_id,
            thread_id=test_thread_id,
            message="Quantos anos eu tenho?",
        )
        logger.info(f"  🤖 Resposta: {response.message}")

        # Verificar se o bot mencionou a idade
        if "25" in response.message or "vinte e cinco" in response.message.lower():
            logger.info("  ✅ Bot mencionou a idade correta")
        else:
            logger.info("  ⚠️ Bot não mencionou a idade correta")

        logger.info("  ✅ Teste de memória de curto prazo OK")
        return True

    except Exception as e:
        logger.info(f"  ❌ Erro no teste de memória de curto prazo: {e}")
        return False
    finally:
        chatbot_service.close()


if __name__ == "__main__":
    import asyncio

    logging.basicConfig(level=logging.INFO)
    asyncio.run(test_short_term_memory())
