import uuid
import logging
from src.services.lang_graph.service import LangGraphChatbotService

logger = logging.getLogger(__name__)


async def test_user_id_injection():
    """Testa se o user_id está sendo injetado corretamente nas ferramentas."""
    print("🔍 Testando injeção de user_id...")

    try:
        # Inicializar serviço
        chatbot_service = LangGraphChatbotService()

        # Usar user_id específico para teste
        user_id = f"test_user_{uuid.uuid4()}"
        thread_id = str(uuid.uuid4())

        print(f"  👤 User ID: {user_id}")
        print(f"  🧵 Thread ID: {thread_id}")

        # Teste 1: Salvar informação
        print("  📝 Teste 1: Salvando informação...")
        response1 = await chatbot_service.process_message(
            user_id=user_id,
            thread_id=thread_id,
            message="Use a ferramenta save_memory_tool para salvar: Meu nome é João Silva.",
        )
        print(f"    🤖 Resposta 1: {response1.message[:100]}...")
        print(f"    🔧 Ferramentas usadas: {response1.tools_called}")

        # Teste 2: Buscar informações
        print("  📝 Teste 2: Buscando informações...")
        response2 = await chatbot_service.process_message(
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
            print("  ✅ User ID está sendo injetado corretamente!")
            return True
        else:
            print("  ❌ User ID não está sendo injetado corretamente")
            return False

    except Exception as e:
        print(f"  ❌ Erro no teste: {e}")
        return False
    finally:
        chatbot_service.close()


if __name__ == "__main__":
    import asyncio

    asyncio.run(test_user_id_injection())
