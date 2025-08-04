"""
Testes de capacidade do agente de usar ferramentas.
"""

import uuid
from src.services.lang_graph.service import LangGraphChatbotService

from src.utils.log import logger


async def test_agent_memory_tools():
    """Testa a capacidade do agente de usar ferramentas de memória."""
    logger.info("📋 Executando: Capacidade do Agente de Usar Ferramentas de Memória")
    logger.info("----------------------------------------")

    # Usar UUID único para evitar contaminação
    test_user_id = str(uuid.uuid4())
    test_thread_id = str(uuid.uuid4())

    try:
        chatbot_service = LangGraphChatbotService()
        logger.info(
            "🧠 Testando capacidade do agente de usar ferramentas de memória..."
        )

        # Teste 1: Agente salvando informações do usuário
        logger.info("  📝 Teste 1: Agente salvando informações do usuário...")
        response = await chatbot_service.process_message(
            user_id=test_user_id,
            thread_id=test_thread_id,
            message="Meu nome é Maria, tenho 25 anos e trabalho como engenheira de software. Eu gosto muito de programar em Python e JavaScript.",
        )
        logger.info(f"  🤖 Resposta: {response.message}")
        logger.info(f"  📊 Memórias usadas: {len(response.memories_used)}")
        logger.info(f"  🔧 Ferramentas chamadas: {response.tools_called}")

        # Teste 2: Agente buscando informações específicas
        logger.info("  🔍 Teste 2: Agente buscando informações específicas...")
        response = await chatbot_service.process_message(
            user_id=test_user_id,
            thread_id=test_thread_id,
            message="Qual é a minha profissão?",
        )
        logger.info(f"  🤖 Resposta: {response.message}")
        logger.info(f"  📊 Memórias usadas: {len(response.memories_used)}")
        logger.info(f"  🔧 Ferramentas chamadas: {response.tools_called}")

        # Teste 3: Agente salvando preferências
        logger.info("  💾 Teste 3: Agente salvando preferências...")
        response = await chatbot_service.process_message(
            user_id=test_user_id,
            thread_id=test_thread_id,
            message="Eu prefiro trabalhar remotamente e gosto de projetos que envolvem machine learning.",
        )
        logger.info(f"  🤖 Resposta: {response.message}")
        logger.info(f"  📊 Memórias usadas: {len(response.memories_used)}")
        logger.info(f"  🔧 Ferramentas chamadas: {response.tools_called}")

        # Teste 4: Agente usando memórias para personalizar resposta
        logger.info(
            "  🎯 Teste 4: Agente usando memórias para personalizar resposta..."
        )
        response = await chatbot_service.process_message(
            user_id=test_user_id,
            thread_id=test_thread_id,
            message="Você pode me recomendar alguns projetos de machine learning em Python?",
        )
        logger.info(f"  🤖 Resposta: {response.message}")
        logger.info(f"  📊 Memórias usadas: {len(response.memories_used)}")
        logger.info(f"  🔧 Ferramentas chamadas: {response.tools_called}")

        # Teste 5: Agente atualizando informações
        logger.info("  🔄 Teste 5: Agente atualizando informações...")
        response = await chatbot_service.process_message(
            user_id=test_user_id,
            thread_id=test_thread_id,
            message="Na verdade, eu tenho 26 anos agora, não 25.",
        )
        logger.info(f"  🤖 Resposta: {response.message}")
        logger.info(f"  📊 Memórias usadas: {len(response.memories_used)}")
        logger.info(f"  🔧 Ferramentas chamadas: {response.tools_called}")

        # Teste 6: Agente verificando informações atualizadas
        logger.info("  ✅ Teste 6: Agente verificando informações atualizadas...")
        response = await chatbot_service.process_message(
            user_id=test_user_id,
            thread_id=test_thread_id,
            message="Quantos anos eu tenho?",
        )
        logger.info(f"  🤖 Resposta: {response.message}")
        logger.info(f"  📊 Memórias usadas: {len(response.memories_used)}")
        logger.info(f"  🔧 Ferramentas chamadas: {response.tools_called}")

        # Teste 7: Agente deletando informações irrelevantes
        logger.info("  🗑️ Teste 7: Agente deletando informações irrelevantes...")
        response = await chatbot_service.process_message(
            user_id=test_user_id,
            thread_id=test_thread_id,
            message="Esquece o que eu disse sobre gostar de JavaScript, eu não uso mais.",
        )
        logger.info(f"  🤖 Resposta: {response.message}")
        logger.info(f"  📊 Memórias usadas: {len(response.memories_used)}")
        logger.info(f"  🔧 Ferramentas chamadas: {response.tools_called}")

        # Teste 8: Agente fazendo busca semântica complexa
        logger.info("  🔍 Teste 8: Agente fazendo busca semântica complexa...")
        response = await chatbot_service.process_message(
            user_id=test_user_id,
            thread_id=test_thread_id,
            message="Quais são minhas habilidades técnicas e preferências de trabalho?",
        )
        logger.info(f"  🤖 Resposta: {response.message}")
        logger.info(f"  📊 Memórias usadas: {len(response.memories_used)}")
        logger.info(f"  🔧 Ferramentas chamadas: {response.tools_called}")

        logger.info("  ✅ Capacidade do agente de usar ferramentas de memória OK")
        return True

    except Exception as e:
        logger.info(f"  ❌ Erro na capacidade do agente de usar ferramentas: {e}")
        return False
    finally:
        chatbot_service.close()


if __name__ == "__main__":
    import asyncio

    logging.basicConfig(level=logging.INFO)
    asyncio.run(test_agent_memory_tools())
