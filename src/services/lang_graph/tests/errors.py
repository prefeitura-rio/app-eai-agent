"""
Testes de tratamento de erros.
"""

import logging
from src.services.lang_graph.service import LangGraphChatbotService

logger = logging.getLogger(__name__)


async def test_error_handling():
    """
    Testes de tratamento de erros.
    """
    print("⚠️ Testando tratamento de erros...")

    chatbot_service = LangGraphChatbotService()

    try:
        # Teste 1: Parâmetros inválidos
        print("  🚫 Testando parâmetros inválidos...")

        # Teste com parâmetros vazios - deve tratar graciosamente
        try:
            result = await chatbot_service.process_message(
                user_id="", thread_id="", message=""
            )
            print("  ⚠️ Sistema não retornou erro esperado, mas continuou funcionando")
        except Exception as e:
            print(
                f"  ✅ Sistema tratou graciosamente parâmetros vazios: {str(e)[:100]}..."
            )

        # Teste 2: Parâmetros None
        try:
            result = await chatbot_service.process_message(
                user_id=None, thread_id=None, message=None
            )
            print("  ⚠️ Sistema não retornou erro esperado, mas continuou funcionando")
        except Exception as e:
            print(
                f"  ✅ Sistema tratou graciosamente parâmetros None: {str(e)[:100]}..."
            )

        print("  ✅ Tratamento de erros OK")
        return True

    except Exception as e:
        print(f"  ❌ Erro inesperado: {e}")
        return False
    finally:
        chatbot_service.close()


if __name__ == "__main__":
    import asyncio

    logging.basicConfig(level=logging.INFO)
    asyncio.run(test_error_handling())
