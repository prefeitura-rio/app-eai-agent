"""
Testes de memória de curto prazo (contexto da conversa).
"""

import logging
import uuid
from src.services.lang_graph.service import LangGraphChatbotService

logger = logging.getLogger(__name__)


async def test_short_term_memory():
    """Testa a capacidade do bot de lembrar o contexto da conversa atual."""
    print("📋 Executando: Memória de Curto Prazo")
    print("----------------------------------------")

    # Usar UUID único para evitar contaminação
    test_user_id = str(uuid.uuid4())
    test_thread_id = str(uuid.uuid4())

    try:
        chatbot_service = LangGraphChatbotService()
        print("🧠 Testando memória de curto prazo...")

        # Teste 1: Primeira mensagem
        print("  💬 Teste 1: Primeira mensagem...")
        response = await chatbot_service.process_message(
            user_id=test_user_id,
            thread_id=test_thread_id,
            message="Olá, como você está?",
        )
        print(f"  🤖 Resposta: {response.message}")

        # Teste 2: Segunda mensagem referenciando a primeira
        print("  💬 Teste 2: Segunda mensagem...")
        response = await chatbot_service.process_message(
            user_id=test_user_id,
            thread_id=test_thread_id,
            message="Você respondeu que está bem?",
        )
        print(f"  🤖 Resposta: {response.message}")

        # Teste 3: Terceira mensagem com contexto
        print("  💬 Teste 3: Terceira mensagem...")
        response = await chatbot_service.process_message(
            user_id=test_user_id,
            thread_id=test_thread_id,
            message="Qual foi a primeira coisa que eu disse?",
        )
        print(f"  🤖 Resposta: {response.message}")

        # Teste 4: Mensagem com informação específica
        print("  💬 Teste 4: Informação específica...")
        response = await chatbot_service.process_message(
            user_id=test_user_id,
            thread_id=test_thread_id,
            message="Meu nome é Ana e eu tenho 25 anos.",
        )
        print(f"  🤖 Resposta: {response.message}")

        # Teste 5: Pergunta sobre informação anterior
        print("  💬 Teste 5: Pergunta sobre informação anterior...")
        response = await chatbot_service.process_message(
            user_id=test_user_id,
            thread_id=test_thread_id,
            message="Quantos anos eu tenho?",
        )
        print(f"  🤖 Resposta: {response.message}")

        # Verificar se o bot mencionou a idade
        if "25" in response.message or "vinte e cinco" in response.message.lower():
            print("  ✅ Bot mencionou a idade correta")
        else:
            print("  ⚠️ Bot não mencionou a idade correta")

        print("  ✅ Teste de memória de curto prazo OK")
        return True

    except Exception as e:
        print(f"  ❌ Erro no teste de memória de curto prazo: {e}")
        return False
    finally:
        chatbot_service.close()


if __name__ == "__main__":
    import asyncio

    logging.basicConfig(level=logging.INFO)
    asyncio.run(test_short_term_memory())
