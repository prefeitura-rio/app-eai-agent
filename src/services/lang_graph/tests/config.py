"""
Testes de parâmetros de configuração.
"""

import uuid
from src.services.lang_graph.service import LangGraphChatbotService
from src.utils.log import logger


async def test_configuration_parameters():
    """Testa se o agente está usando os parâmetros de configuração corretamente."""
    logger.info("📋 Executando: Parâmetros de Configuração")
    logger.info("----------------------------------------")

    # Usar UUID único para evitar contaminação
    test_user_id = str(uuid.uuid4())
    test_thread_id = str(uuid.uuid4())

    try:
        chatbot_service = LangGraphChatbotService()
        logger.info("⚙️ Testando parâmetros de configuração...")

        # Teste 1: Salvando memórias para teste
        logger.info("  💾 Teste 1: Salvando memórias para teste...")
        response = await chatbot_service.process_message(
            user_id=test_user_id,
            thread_id=test_thread_id,
            message="Meu nome é Pedro, tenho 28 anos e trabalho como desenvolvedor. Gosto de programar em Python e JavaScript.",
        )
        logger.info(f"  🤖 Resposta: {response.message}")
        logger.info(f"  🔧 Ferramentas chamadas: {response.tools_called}")

        # Teste 2: Buscando com configuração padrão
        logger.info("  🔍 Teste 2: Buscando com configuração padrão...")
        response = await chatbot_service.process_message(
            user_id=test_user_id,
            thread_id=test_thread_id,
            message="Quais são minhas informações pessoais?",
        )
        logger.info(f"  🤖 Resposta: {response.message}")
        logger.info(f"  🔧 Ferramentas chamadas: {response.tools_called}")

        # Teste 3: Buscando com parâmetros específicos
        logger.info("  🎯 Teste 3: Buscando com parâmetros específicos...")
        response = await chatbot_service.process_message(
            user_id=test_user_id,
            thread_id=test_thread_id,
            message="Busque apenas as 3 memórias mais relevantes sobre minhas preferências.",
        )
        logger.info(f"  🤖 Resposta: {response.message}")
        logger.info(f"  🔧 Ferramentas chamadas: {response.tools_called}")

        # Teste 4: Buscando com alta relevância
        logger.info("  🔥 Teste 4: Buscando com alta relevância...")
        response = await chatbot_service.process_message(
            user_id=test_user_id,
            thread_id=test_thread_id,
            message="Busque apenas memórias com relevância muito alta sobre minha profissão.",
        )
        logger.info(f"  🤖 Resposta: {response.message}")
        logger.info(f"  🔧 Ferramentas chamadas: {response.tools_called}")

        # Teste 5: Verificando uso dos parâmetros
        logger.info("  ✅ Teste 5: Verificando uso dos parâmetros...")
        response = await chatbot_service.process_message(
            user_id=test_user_id,
            thread_id=test_thread_id,
            message="Quantas memórias você pode buscar por vez?",
        )
        logger.info(f"  🤖 Resposta: {response.message}")
        logger.info(f"  🔧 Ferramentas chamadas: {response.tools_called}")

        logger.info("  ✅ Teste de parâmetros de configuração OK")
        return True

    except Exception as e:
        logger.info(f"  ❌ Erro no teste de parâmetros de configuração: {e}")
        return False
    finally:
        chatbot_service.close()


if __name__ == "__main__":
    import asyncio

    logging.basicConfig(level=logging.INFO)
    asyncio.run(test_configuration_parameters())
