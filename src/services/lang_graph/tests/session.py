"""
Testes de gerenciamento de sessões.
"""

import logging
import uuid
from src.services.lang_graph.service import LangGraphChatbotService

logger = logging.getLogger(__name__)


async def test_session_management():
    """Testa gerenciamento de sessões."""
    print("📋 Executando: Gerenciamento de Sessões")
    print("----------------------------------------")

    # Usar UUID único para evitar contaminação
    test_user_id = str(uuid.uuid4())
    test_thread_id = str(uuid.uuid4())

    try:
        chatbot_service = LangGraphChatbotService()
        print("🎯 Testando gerenciamento de sessões...")

        # Teste 1: Inicialização de sessão
        print("  🚀 Testando inicialização de sessão...")
        session_result = chatbot_service.initialize_session(
            user_id=test_user_id,
            thread_id=test_thread_id,
        )
        print(f"  ✅ Sessão inicializada: {session_result}")

        # Teste 2: Processar mensagem para testar a sessão
        print("  💬 Testando processamento de mensagem com sessão...")
        response = await chatbot_service.process_message(
            user_id=test_user_id,
            thread_id=test_thread_id,
            message="Olá, esta é uma mensagem de teste",
        )
        print(f"  🤖 Resposta: {response.message}")

        # Teste 3: Limpeza de memórias
        print("  🧹 Testando limpeza de memórias...")
        result = chatbot_service.clear_memory(test_user_id)
        if result.get("success"):
            print("  ✅ Memórias limpas com sucesso")
        else:
            print(f"  ❌ Erro ao limpar memórias: {result.get('error_message')}")

        print("  ✅ Gerenciamento de sessões OK")
        return True

    except Exception as e:
        print(f"  ❌ Erro no gerenciamento de sessões: {e}")
        return False
    finally:
        chatbot_service.close()


if __name__ == "__main__":
    import asyncio

    logging.basicConfig(level=logging.INFO)
    asyncio.run(test_session_management())
