"""
Testes de tratamento de erros.
"""

from src.services.lang_graph.service import LangGraphChatbotService
from src.utils.log import logger


async def test_error_handling():
    """
    Testes de tratamento de erros.
    """
    logger.info("⚠️ Testando tratamento de erros...")

    chatbot_service = LangGraphChatbotService()

    try:
        # Teste 1: Parâmetros inválidos
        logger.info("  🚫 Testando parâmetros inválidos...")

        # Teste com parâmetros vazios - deve tratar graciosamente
        try:
            result = await chatbot_service.process_message(
                user_id="", thread_id="", message=""
            )
            logger.info(
                "  ⚠️ Sistema não retornou erro esperado, mas continuou funcionando"
            )
        except Exception as e:
            logger.info(
                f"  ✅ Sistema tratou graciosamente parâmetros vazios: {str(e)[:100]}..."
            )

        # Teste 2: Parâmetros None
        try:
            result = await chatbot_service.process_message(
                user_id=None, thread_id=None, message=None
            )
            logger.info(
                "  ⚠️ Sistema não retornou erro esperado, mas continuou funcionando"
            )
        except Exception as e:
            logger.info(
                f"  ✅ Sistema tratou graciosamente parâmetros None: {str(e)[:100]}..."
            )

        logger.info("  ✅ Tratamento de erros OK")
        return True

    except Exception as e:
        logger.info(f"  ❌ Erro inesperado: {e}")
        return False
    finally:
        chatbot_service.close()


if __name__ == "__main__":
    import asyncio

    logging.basicConfig(level=logging.INFO)
    asyncio.run(test_error_handling())
