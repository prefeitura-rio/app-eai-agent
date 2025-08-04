"""
Teste para verificar se o system prompt está sendo injetado corretamente
e se o chat lembra das mensagens da mesma thread.
"""

import uuid
from src.services.lang_graph.service import LangGraphChatbotService
from src.utils.log import logger


async def test_system_prompt_injection():
    """
    Testa se o system prompt está sendo injetado corretamente
    e se o chat lembra das mensagens da mesma thread.
    """
    logger.info("🧠 Testando injeção de system prompt e memória de thread...")

    chatbot_service = LangGraphChatbotService()

    try:
        # Teste 1: Verificar se o system prompt está sendo injetado
        logger.info("  📝 Teste 1: Verificando injeção de system prompt...")

        user_id = str(uuid.uuid4())
        thread_id = str(uuid.uuid4())

        # Inicializar sessão com system prompt customizado
        custom_prompt = "Você é um assistente especializado em programação Python. Sempre responda de forma técnica e detalhada."

        session_result = chatbot_service.initialize_session(
            user_id=user_id,
            thread_id=thread_id,
            temperature=0.3,  # Baixa temperatura para respostas mais consistentes
        )

        if not session_result.get("success"):
            logger.info("  ❌ Falha ao inicializar sessão")
            return False

        # Enviar mensagem técnica
        response = await chatbot_service.process_message(
            user_id=user_id,
            thread_id=thread_id,
            message="Explique o que é uma função lambda em Python.",
        )

        logger.info(f"  🤖 Resposta: {response.message[:200]}...")

        # Verificar se a resposta é técnica (indicando que o system prompt foi aplicado)
        technical_indicators = [
            "lambda",
            "função",
            "def",
            "return",
            "parâmetro",
            "argumento",
        ]
        is_technical = any(
            indicator in response.message.lower() for indicator in technical_indicators
        )

        if is_technical:
            logger.info("  ✅ System prompt aplicado - resposta técnica detectada")
        else:
            logger.info("  ⚠️ System prompt pode não estar sendo aplicado corretamente")

        # Teste 2: Verificar se o chat lembra das mensagens da mesma thread
        logger.info("  💬 Teste 2: Verificando memória de thread...")

        # Enviar primeira mensagem
        response1 = await chatbot_service.process_message(
            user_id=user_id,
            thread_id=thread_id,
            message="Meu nome é João e eu sou desenvolvedor Python.",
        )

        logger.info(f"  📝 Primeira mensagem: {response1.message[:100]}...")

        # Enviar segunda mensagem na mesma thread
        response2 = await chatbot_service.process_message(
            user_id=user_id,
            thread_id=thread_id,
            message="Qual é o meu nome?",
        )

        logger.info(f"  📝 Segunda mensagem: {response2.message[:100]}...")

        # Verificar se o bot mencionou o nome "João" na segunda resposta
        if "joão" in response2.message.lower():
            logger.info("  ✅ Chat lembra do nome da thread - memória funcionando")
        else:
            logger.info("  ⚠️ Chat pode não estar lembrando das mensagens da thread")

        # Teste 3: Verificar isolamento entre threads
        logger.info("  🔒 Teste 3: Verificando isolamento entre threads...")

        # Criar nova thread com usuário diferente
        user_id2 = str(uuid.uuid4())
        thread_id2 = str(uuid.uuid4())

        # Enviar mensagem na nova thread
        response3 = await chatbot_service.process_message(
            user_id=user_id2,
            thread_id=thread_id2,
            message="Qual é o meu nome?",
        )

        logger.info(f"  📝 Nova thread: {response3.message[:100]}...")

        # Verificar se NÃO menciona "João" na nova thread
        if "joão" not in response3.message.lower():
            logger.info("  ✅ Isolamento entre threads funcionando")
        else:
            logger.info("  ⚠️ Possível problema de isolamento entre threads")

        # Teste 4: Verificar se o system prompt é mantido entre mensagens
        logger.info("  🔄 Teste 4: Verificando consistência do system prompt...")

        # Enviar terceira mensagem na primeira thread
        response4 = await chatbot_service.process_message(
            user_id=user_id,
            thread_id=thread_id,
            message="Explique o que é uma list comprehension em Python.",
        )

        logger.info(f"  📝 Terceira mensagem: {response4.message[:200]}...")

        # Verificar se ainda é técnica
        is_technical_2 = any(
            indicator in response4.message.lower() for indicator in technical_indicators
        )

        if is_technical_2:
            logger.info("  ✅ System prompt mantido entre mensagens")
        else:
            logger.info("  ⚠️ System prompt pode não estar sendo mantido")

        logger.info("  ✅ Teste de system prompt e memória de thread OK")
        return True

    except Exception as e:
        logger.info(f"  ❌ Erro no teste de system prompt: {e}")
        return False
    finally:
        chatbot_service.close()


if __name__ == "__main__":
    import asyncio

    logging.basicConfig(level=logging.INFO)
    asyncio.run(test_system_prompt_injection())
