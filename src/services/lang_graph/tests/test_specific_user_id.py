import logging
from src.services.lang_graph.service import LangGraphChatbotService

logger = logging.getLogger(__name__)


def test_specific_user_id():
    """Testa com o user_id específico da conversa do usuário."""
    print("🔍 Testando user_id específico...")

    try:
        # Inicializar serviço
        chatbot_service = LangGraphChatbotService()

        # Usar o user_id da conversa do usuário
        user_id = "16ed4535-0327-4774-88ba-dce483bb4229"
        thread_id = "test_thread_specific"

        print(f"  👤 User ID: {user_id}")
        print(f"  🧵 Thread ID: {thread_id}")

        # Teste 1: Salvar informação
        print("  📝 Teste 1: Salvando informação...")
        response1 = chatbot_service.process_message(
            user_id=user_id,
            thread_id=thread_id,
            message="Use a ferramenta save_memory_tool para salvar: Informação crítica - Tenho um agendamento no Sisrag na semana que vem.",
        )
        print(f"    🤖 Resposta 1: {response1.message[:100]}...")
        print(f"    🔧 Ferramentas usadas: {response1.tools_called}")

        # Teste 2: Buscar informações
        print("  📝 Teste 2: Buscando informações...")
        response2 = chatbot_service.process_message(
            user_id=user_id,
            thread_id=thread_id,
            message="Use a ferramenta get_memory_tool para buscar minhas informações.",
        )
        print(f"    🤖 Resposta 2: {response2.message[:100]}...")
        print(f"    🔧 Ferramentas usadas: {response2.tools_called}")

        # Verificar se as respostas foram geradas
        responses = [response1, response2]
        all_responses_valid = all(len(r.message.strip()) > 0 for r in responses)

        # Verificar se as ferramentas foram usadas
        all_tools_used = set()
        for r in responses:
            all_tools_used.update(r.tools_called)

        expected_tools = {"save_memory_tool", "get_memory_tool"}
        tools_coverage = len(all_tools_used.intersection(expected_tools)) >= 1

        print(f"    📊 Respostas válidas: {all_responses_valid}")
        print(f"    📊 Ferramentas usadas: {sorted(all_tools_used)}")
        print(f"    📊 Ferramentas esperadas: {sorted(expected_tools)}")
        print(f"    📊 Cobertura de ferramentas: {tools_coverage}")

        # Resultado final
        if all_responses_valid and tools_coverage:
            print("  ✅ User ID específico está sendo injetado corretamente!")
            return True
        else:
            print("  ❌ User ID específico não está sendo injetado corretamente")
            return False

    except Exception as e:
        print(f"  ❌ Erro no teste: {e}")
        return False
    finally:
        chatbot_service.close()


if __name__ == "__main__":
    test_specific_user_id()
