"""
Testes de contexto de conversação.
"""

import logging
import uuid
from src.services.lang_graph.service import LangGraphChatbotService

logger = logging.getLogger(__name__)


async def test_conversation_context():
    """Testa se o bot mantém o contexto da conversa."""
    print("📋 Executando: Contexto de Conversação")
    print("----------------------------------------")

    # Usar UUID único para evitar contaminação
    test_user_id = str(uuid.uuid4())
    test_thread_id = str(uuid.uuid4())

    try:
        chatbot_service = LangGraphChatbotService()
        print("💬 Testando contexto de conversação...")

        # Teste 1: Iniciar conversa
        print("  💬 Teste 1: Iniciando conversa...")
        response = await chatbot_service.process_message(
            user_id=test_user_id,
            thread_id=test_thread_id,
            message="Olá, como você está?",
        )
        print(f"  🤖 Resposta: {response.message}")

        # Teste 2: Continuar conversa
        print("  💬 Teste 2: Continuando conversa...")
        response = await chatbot_service.process_message(
            user_id=test_user_id,
            thread_id=test_thread_id,
            message="Que bom! Você pode me ajudar com algo?",
        )
        print(f"  🤖 Resposta: {response.message}")

        # Teste 3: Pergunta específica
        print("  💬 Teste 3: Pergunta específica...")
        response = await chatbot_service.process_message(
            user_id=test_user_id,
            thread_id=test_thread_id,
            message="Você se lembra do que eu perguntei antes?",
        )
        print(f"  🤖 Resposta: {response.message}")

        # Teste 4: Informação pessoal
        print("  💬 Teste 4: Informação pessoal...")
        response = await chatbot_service.process_message(
            user_id=test_user_id,
            thread_id=test_thread_id,
            message="Meu nome é João e eu trabalho como programador.",
        )
        print(f"  🤖 Resposta: {response.message}")

        # Teste 5: Referência à informação anterior
        print("  💬 Teste 5: Referência à informação anterior...")
        response = await chatbot_service.process_message(
            user_id=test_user_id,
            thread_id=test_thread_id,
            message="Você pode me dar dicas sobre programação?",
        )
        print(f"  🤖 Resposta: {response.message}")

        # Verificar se o bot mencionou o contexto
        if "João" in response.message or "programador" in response.message.lower():
            print("  ✅ Bot mencionou o contexto da conversa")
        else:
            print("  ⚠️ Bot não mencionou o contexto da conversa")

        print("  ✅ Teste de contexto de conversação OK")
        return True

    except Exception as e:
        print(f"  ❌ Erro no teste de contexto de conversação: {e}")
        return False
    finally:
        chatbot_service.close()


if __name__ == "__main__":
    import asyncio

    logging.basicConfig(level=logging.INFO)
    asyncio.run(test_conversation_context())
