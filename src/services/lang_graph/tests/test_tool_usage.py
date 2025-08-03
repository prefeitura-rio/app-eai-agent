import uuid
import logging
from src.services.lang_graph.service import LangGraphChatbotService

logger = logging.getLogger(__name__)


def test_tool_usage():
    """Testa se o agente está usando as ferramentas corretamente com as novas instruções."""
    print("🔧 Testando uso correto das ferramentas...")

    try:
        # Inicializar serviço
        chatbot_service = LangGraphChatbotService()

        # Usar user_id específico para teste
        user_id = f"test_tool_usage_{uuid.uuid4()}"
        thread_id = str(uuid.uuid4())

        print(f"  👤 User ID: {user_id}")
        print(f"  🧵 Thread ID: {thread_id}")

        # Teste 1: Usuário fornece informação pessoal (deve usar save_memory_tool)
        print("  📝 Teste 1: Usuário fornece informação pessoal...")
        response1 = chatbot_service.process_message(
            user_id=user_id,
            thread_id=thread_id,
            message="Meu nome é Maria Silva e tenho 25 anos.",
        )
        print(f"    🤖 Resposta 1: {response1.message[:100]}...")
        print(f"    🔧 Ferramentas usadas: {response1.tools_called}")

        # Teste 2: Usuário pergunta sobre si mesmo (deve usar get_memory_tool)
        print("  📝 Teste 2: Usuário pergunta sobre si mesmo...")
        response2 = chatbot_service.process_message(
            user_id=user_id,
            thread_id=thread_id,
            message="Qual é o meu nome?",
        )
        print(f"    🤖 Resposta 2: {response2.message[:100]}...")
        print(f"    🔧 Ferramentas usadas: {response2.tools_called}")

        # Teste 3: Usuário fornece preferência (deve usar save_memory_tool)
        print("  📝 Teste 3: Usuário fornece preferência...")
        response3 = chatbot_service.process_message(
            user_id=user_id,
            thread_id=thread_id,
            message="Eu gosto de programar em Python e tenho alergia a frutos do mar.",
        )
        print(f"    🤖 Resposta 3: {response3.message[:100]}...")
        print(f"    🔧 Ferramentas usadas: {response3.tools_called}")

        # Teste 4: Usuário pergunta sobre preferências (deve usar get_memory_tool)
        print("  📝 Teste 4: Usuário pergunta sobre preferências...")
        response4 = chatbot_service.process_message(
            user_id=user_id,
            thread_id=thread_id,
            message="Quais são as minhas preferências?",
        )
        print(f"    🤖 Resposta 4: {response4.message[:100]}...")
        print(f"    🔧 Ferramentas usadas: {response4.tools_called}")

        # Verificar se as respostas foram geradas
        responses = [response1, response2, response3, response4]
        all_responses_valid = all(len(r.message.strip()) > 0 for r in responses)

        # Verificar se as ferramentas foram usadas corretamente
        all_tools_used = set()
        for r in responses:
            all_tools_used.update(r.tools_called)

        # Verificar se save_memory_tool foi usada (obrigatório para informações pessoais)
        save_tool_used = "save_memory_tool" in all_tools_used
        
        # Verificar se get_memory_tool foi usada (obrigatório para perguntas sobre dados)
        get_tool_used = "get_memory_tool" in all_tools_used

        print(f"    📊 Respostas válidas: {all_responses_valid}")
        print(f"    📊 Ferramentas usadas: {sorted(all_tools_used)}")
        print(f"    📊 Save tool usada: {save_tool_used}")
        print(f"    📊 Get tool usada: {get_tool_used}")

        # Resultado final
        if all_responses_valid and save_tool_used and get_tool_used:
            print("  ✅ Agente está usando as ferramentas corretamente!")
            return True
        else:
            print("  ❌ Agente não está usando as ferramentas corretamente")
            return False

    except Exception as e:
        print(f"  ❌ Erro no teste: {e}")
        return False
    finally:
        chatbot_service.close()


if __name__ == "__main__":
    test_tool_usage() 