"""
Testes de ferramentas com contexto.
"""

import uuid
from src.services.lang_graph.service import LangGraphChatbotService
from src.utils.log import logger


async def test_context_tools():
    """Testa ferramentas com contexto (user_id, limit, min_relevance)."""
    logger.info("📋 Executando: Ferramentas com Contexto")
    logger.info("----------------------------------------")

    # Usar UUID único para evitar contaminação
    test_user_id = str(uuid.uuid4())
    test_thread_id = str(uuid.uuid4())

    try:
        chatbot_service = LangGraphChatbotService()
        logger.info("🔧 Testando ferramentas com contexto...")

        # Teste 1: Salvando informações com contexto
        logger.info("  💾 Teste 1: Salvando informações com contexto...")
        response = await chatbot_service.process_message(
            user_id=test_user_id,
            thread_id=test_thread_id,
            message="Eu sou Ana, tenho 30 anos e trabalho como designer. Gosto de arte e fotografia.",
        )
        logger.info(f"  🤖 Resposta: {response.message}")
        logger.info(f"  📊 Memórias usadas: {len(response.memories_used)}")
        logger.info(f"  🔧 Ferramentas chamadas: {response.tools_called}")

        # Teste 2: Buscando com parâmetros específicos
        logger.info("  🔍 Teste 2: Buscando com parâmetros específicos...")
        response = await chatbot_service.process_message(
            user_id=test_user_id,
            thread_id=test_thread_id,
            message="Quais são minhas informações pessoais? Busque apenas as mais relevantes.",
        )
        logger.info(f"  🤖 Resposta: {response.message}")
        logger.info(f"  📊 Memórias usadas: {len(response.memories_used)}")
        logger.info(f"  🔧 Ferramentas chamadas: {response.tools_called}")

        # Teste 3: Buscando com filtro de tipo
        logger.info("  🎯 Teste 3: Buscando com filtro de tipo...")
        response = await chatbot_service.process_message(
            user_id=test_user_id,
            thread_id=test_thread_id,
            message="Quais são minhas preferências?",
        )
        logger.info(f"  🤖 Resposta: {response.message}")
        logger.info(f"  📊 Memórias usadas: {len(response.memories_used)}")
        logger.info(f"  🔧 Ferramentas chamadas: {response.tools_called}")

        # Teste 4: Atualizando informação
        logger.info("  🔄 Teste 4: Atualizando informação...")
        response = await chatbot_service.process_message(
            user_id=test_user_id,
            thread_id=test_thread_id,
            message="Na verdade, eu tenho 31 anos agora.",
        )
        logger.info(f"  🤖 Resposta: {response.message}")
        logger.info(f"  📊 Memórias usadas: {len(response.memories_used)}")
        logger.info(f"  🔧 Ferramentas chamadas: {response.tools_called}")

        # Teste 5: Verificando atualização
        logger.info("  ✅ Teste 5: Verificando atualização...")
        response = await chatbot_service.process_message(
            user_id=test_user_id,
            thread_id=test_thread_id,
            message="Quantos anos eu tenho?",
        )
        logger.info(f"  🤖 Resposta: {response.message}")
        logger.info(f"  📊 Memórias usadas: {len(response.memories_used)}")
        logger.info(f"  🔧 Ferramentas chamadas: {response.tools_called}")

        logger.info("  ✅ Teste de ferramentas com contexto OK")
        return True

    except Exception as e:
        logger.info(f"  ❌ Erro no teste de ferramentas com contexto: {e}")
        return False
    finally:
        chatbot_service.close()


if __name__ == "__main__":
    import asyncio

    logging.basicConfig(level=logging.INFO)
    asyncio.run(test_context_tools())
