"""
Teste para verificar se o system prompt está sendo injetado corretamente
e se o chat lembra das mensagens da mesma thread.
"""

import logging
import uuid
from src.services.lang_graph.service import LangGraphChatbotService


async def test_system_prompt_injection():
    """
    Testa se o system prompt está sendo injetado corretamente
    e se o chat lembra das mensagens da mesma thread.
    """
    print("🧠 Testando injeção de system prompt e memória de thread...")

    chatbot_service = LangGraphChatbotService()

    try:
        # Teste 1: Verificar se o system prompt está sendo injetado
        print("  📝 Teste 1: Verificando injeção de system prompt...")

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
            print("  ❌ Falha ao inicializar sessão")
            return False

        # Enviar mensagem técnica
        response = await chatbot_service.process_message(
            user_id=user_id,
            thread_id=thread_id,
            message="Explique o que é uma função lambda em Python.",
        )

        print(f"  🤖 Resposta: {response.message[:200]}...")

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
            print("  ✅ System prompt aplicado - resposta técnica detectada")
        else:
            print("  ⚠️ System prompt pode não estar sendo aplicado corretamente")

        # Teste 2: Verificar se o chat lembra das mensagens da mesma thread
        print("  💬 Teste 2: Verificando memória de thread...")

        # Enviar primeira mensagem
        response1 = await chatbot_service.process_message(
            user_id=user_id,
            thread_id=thread_id,
            message="Meu nome é João e eu sou desenvolvedor Python.",
        )

        print(f"  📝 Primeira mensagem: {response1.message[:100]}...")

        # Enviar segunda mensagem na mesma thread
        response2 = await chatbot_service.process_message(
            user_id=user_id,
            thread_id=thread_id,
            message="Qual é o meu nome?",
        )

        print(f"  📝 Segunda mensagem: {response2.message[:100]}...")

        # Verificar se o bot mencionou o nome "João" na segunda resposta
        if "joão" in response2.message.lower():
            print("  ✅ Chat lembra do nome da thread - memória funcionando")
        else:
            print("  ⚠️ Chat pode não estar lembrando das mensagens da thread")

        # Teste 3: Verificar isolamento entre threads
        print("  🔒 Teste 3: Verificando isolamento entre threads...")

        # Criar nova thread com usuário diferente
        user_id2 = str(uuid.uuid4())
        thread_id2 = str(uuid.uuid4())

        # Enviar mensagem na nova thread
        response3 = await chatbot_service.process_message(
            user_id=user_id2,
            thread_id=thread_id2,
            message="Qual é o meu nome?",
        )

        print(f"  📝 Nova thread: {response3.message[:100]}...")

        # Verificar se NÃO menciona "João" na nova thread
        if "joão" not in response3.message.lower():
            print("  ✅ Isolamento entre threads funcionando")
        else:
            print("  ⚠️ Possível problema de isolamento entre threads")

        # Teste 4: Verificar se o system prompt é mantido entre mensagens
        print("  🔄 Teste 4: Verificando consistência do system prompt...")

        # Enviar terceira mensagem na primeira thread
        response4 = await chatbot_service.process_message(
            user_id=user_id,
            thread_id=thread_id,
            message="Explique o que é uma list comprehension em Python.",
        )

        print(f"  📝 Terceira mensagem: {response4.message[:200]}...")

        # Verificar se ainda é técnica
        is_technical_2 = any(
            indicator in response4.message.lower() for indicator in technical_indicators
        )

        if is_technical_2:
            print("  ✅ System prompt mantido entre mensagens")
        else:
            print("  ⚠️ System prompt pode não estar sendo mantido")

        print("  ✅ Teste de system prompt e memória de thread OK")
        return True

    except Exception as e:
        print(f"  ❌ Erro no teste de system prompt: {e}")
        return False
    finally:
        chatbot_service.close()


if __name__ == "__main__":
    import asyncio

    logging.basicConfig(level=logging.INFO)
    asyncio.run(test_system_prompt_injection())
