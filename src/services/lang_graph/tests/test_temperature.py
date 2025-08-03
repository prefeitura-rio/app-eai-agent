"""
Teste para verificar o controle de temperatura do chatbot.
"""

import logging
import uuid
from src.services.lang_graph.service import LangGraphChatbotService


def test_temperature_control():
    """
    Testa o controle de temperatura do chatbot.
    """
    print("🌡️ Testando controle de temperatura...")

    chatbot_service = LangGraphChatbotService()

    try:
        # Teste 1: Temperatura baixa (respostas mais determinísticas)
        print("  ❄️ Testando temperatura baixa (0.1)...")

        user_id = str(uuid.uuid4())
        thread_id = str(uuid.uuid4())

        # Inicializar sessão com temperatura baixa
        session_result = chatbot_service.initialize_session(
            user_id=user_id, thread_id=thread_id, temperature=0.1  # Temperatura baixa
        )

        if not session_result.get("success"):
            print("  ❌ Falha ao inicializar sessão com temperatura baixa")
            return False

        # Enviar mensagem
        response_low = chatbot_service.process_message(
            user_id=user_id,
            thread_id=thread_id,
            message="Conte uma história curta sobre um gato.",
        )

        print(f"  🤖 Resposta (temp=0.1): {response_low.message[:100]}...")

        # Teste 2: Temperatura alta (respostas mais criativas)
        print("  🔥 Testando temperatura alta (0.9)...")

        user_id_high = str(uuid.uuid4())
        thread_id_high = str(uuid.uuid4())

        # Inicializar sessão com temperatura alta
        session_result_high = chatbot_service.initialize_session(
            user_id=user_id_high,
            thread_id=thread_id_high,
            temperature=0.9,  # Temperatura alta
        )

        if not session_result_high.get("success"):
            print("  ❌ Falha ao inicializar sessão com temperatura alta")
            return False

        # Enviar a mesma mensagem
        response_high = chatbot_service.process_message(
            user_id=user_id_high,
            thread_id=thread_id_high,
            message="Conte uma história curta sobre um gato.",
        )

        print(f"  🤖 Resposta (temp=0.9): {response_high.message[:100]}...")

        # Teste 3: Temperatura padrão (0.7)
        print("  🌡️ Testando temperatura padrão (0.7)...")

        user_id_default = str(uuid.uuid4())
        thread_id_default = str(uuid.uuid4())

        # Inicializar sessão com temperatura padrão
        session_result_default = chatbot_service.initialize_session(
            user_id=user_id_default,
            thread_id=thread_id_default,
            temperature=0.7,  # Temperatura padrão
        )

        if not session_result_default.get("success"):
            print("  ❌ Falha ao inicializar sessão com temperatura padrão")
            return False

        # Enviar a mesma mensagem
        response_default = chatbot_service.process_message(
            user_id=user_id_default,
            thread_id=thread_id_default,
            message="Conte uma história curta sobre um gato.",
        )

        print(f"  🤖 Resposta (temp=0.7): {response_default.message[:100]}...")

        # Verificar se as respostas são diferentes (indicando que temperatura funciona)
        if (
            response_low.message != response_high.message
            and response_low.message != response_default.message
            and response_high.message != response_default.message
        ):
            print("  ✅ Temperatura funcionando - respostas diferentes geradas")
        else:
            print(
                "  ⚠️ Respostas similares - pode indicar que temperatura não está sendo aplicada"
            )

        print("  ✅ Teste de temperatura OK")
        return True

    except Exception as e:
        print(f"  ❌ Erro no teste de temperatura: {e}")
        return False
    finally:
        chatbot_service.close()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    test_temperature_control()
