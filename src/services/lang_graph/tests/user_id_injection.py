import uuid
from src.services.lang_graph.service import LangGraphChatbotService
from src.utils.log import logger


async def test_user_id_injection():
    """Testa se o user_id está sendo injetado corretamente nas ferramentas."""
    logger.info("🔍 Testando injeção de user_id...")

    try:
        # Inicializar serviço
        chatbot_service = LangGraphChatbotService()

        # Usar user_id específico para teste
        user_id = f"test_user_{uuid.uuid4()}"
        thread_id = str(uuid.uuid4())

        logger.info(f"  👤 User ID: {user_id}")
        logger.info(f"  🧵 Thread ID: {thread_id}")

        # Teste 1: Salvar informação
        logger.info("  📝 Teste 1: Salvando informação...")
        response1 = await chatbot_service.process_message(
            user_id=user_id,
            thread_id=thread_id,
            message="Use a ferramenta save_memory_tool para salvar: Meu nome é João Silva.",
        )
        logger.info(f"    🤖 Resposta 1: {response1.message[:100]}...")
        logger.info(f"    🔧 Ferramentas usadas: {response1.tools_called}")

        # Teste 2: Buscar informações
        logger.info("  📝 Teste 2: Buscando informações...")
        response2 = await chatbot_service.process_message(
            user_id=user_id,
            thread_id=thread_id,
            message="Use a ferramenta get_memory_tool para buscar minhas informações.",
        )
        logger.info(f"    🤖 Resposta 2: {response2.message[:100]}...")
        logger.info(f"    🔧 Ferramentas usadas: {response2.tools_called}")

        # Verificar se as respostas foram geradas
        responses = [response1, response2]
        all_responses_valid = all(len(r.message.strip()) > 0 for r in responses)

        # Verificar se as ferramentas foram usadas
        all_tools_used = set()
        for r in responses:
            all_tools_used.update(r.tools_called)

        expected_tools = {"save_memory_tool", "get_memory_tool"}
        tools_coverage = len(all_tools_used.intersection(expected_tools)) >= 1

        logger.info(f"    📊 Respostas válidas: {all_responses_valid}")
        logger.info(f"    📊 Ferramentas usadas: {sorted(all_tools_used)}")
        logger.info(f"    📊 Ferramentas esperadas: {sorted(expected_tools)}")
        logger.info(f"    📊 Cobertura de ferramentas: {tools_coverage}")

        # Resultado final
        if all_responses_valid and tools_coverage:
            logger.info("  ✅ User ID está sendo injetado corretamente!")
            return True
        else:
            logger.info("  ❌ User ID não está sendo injetado corretamente")
            return False

    except Exception as e:
        logger.info(f"  ❌ Erro no teste: {e}")
        return False
    finally:
        chatbot_service.close()


if __name__ == "__main__":
    import asyncio

    asyncio.run(test_user_id_injection())
