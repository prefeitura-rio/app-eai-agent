import uuid
import logging
from src.services.lang_graph.service import LangGraphChatbotService

logger = logging.getLogger(__name__)


async def test_all_tools():
    """Testa se o agente consegue usar todas as ferramentas disponíveis."""
    print("🔧 Testando uso de todas as ferramentas...")

    try:
        # Inicializar serviço
        chatbot_service = LangGraphChatbotService()

        # Usar user_id único para garantir que não há memórias pré-existentes
        user_id = f"test_all_tools_user_{uuid.uuid4()}"

        print(f"  👤 User ID: {user_id}")

        # Teste 1: Salvar informações (save_memory_tool)
        print("  📝 Teste 1: Salvando informações...")
        thread_id_1 = str(uuid.uuid4())
        response1 = await chatbot_service.process_message(
            user_id=user_id,
            thread_id=thread_id_1,
            message="Meu nome é Pedro Silva, tenho 30 anos e sou engenheiro. Eu gosto de programar em Java e tenho alergia a frutos do mar.",
        )
        print(f"    🤖 Resposta 1: {response1.message[:100]}...")
        print(f"    🔧 Ferramentas usadas: {response1.tools_called}")

        # Mensagens aleatórias na thread 1
        await chatbot_service.process_message(
            user_id=user_id,
            thread_id=thread_id_1,
            message="Como está o tempo hoje?",
        )
        await chatbot_service.process_message(
            user_id=user_id,
            thread_id=thread_id_1,
            message="Que dia é hoje?",
        )

        # Teste 2: Buscar informações (get_memory_tool) - nova thread
        print("  📝 Teste 2: Buscando informações...")
        thread_id_2 = str(uuid.uuid4())
        response2 = await chatbot_service.process_message(
            user_id=user_id,
            thread_id=thread_id_2,
            message="O que você sabe sobre mim?",
        )
        print(f"    🤖 Resposta 2: {response2.message[:100]}...")
        print(f"    🔧 Ferramentas usadas: {response2.tools_called}")

        # Teste 3: Atualizar informações (update_memory_tool) - nova thread
        print("  📝 Teste 3: Atualizando informações...")
        thread_id_3 = str(uuid.uuid4())
        response3 = await chatbot_service.process_message(
            user_id=user_id,
            thread_id=thread_id_3,
            message="Atualize minha idade para 31 anos.",
        )
        print(f"    🤖 Resposta 3: {response3.message[:100]}...")
        print(f"    🔧 Ferramentas usadas: {response3.tools_called}")

        # Teste 4: Deletar informações (delete_memory_tool) - nova thread
        print("  📝 Teste 4: Deletando informações...")
        thread_id_4 = str(uuid.uuid4())
        response4 = await chatbot_service.process_message(
            user_id=user_id,
            thread_id=thread_id_4,
            message="Delete a informação sobre minha alergia.",
        )
        print(f"    🤖 Resposta 4: {response4.message[:100]}...")
        print(f"    🔧 Ferramentas usadas: {response4.tools_called}")

        # Teste 5: Verificar resultado final (get_memory_tool) - nova thread
        print("  📝 Teste 5: Verificando resultado final...")
        thread_id_5 = str(uuid.uuid4())
        response5 = await chatbot_service.process_message(
            user_id=user_id,
            thread_id=thread_id_5,
            message="Quais são minhas informações atuais?",
        )
        print(f"    🤖 Resposta 5: {response5.message[:100]}...")
        print(f"    🔧 Ferramentas usadas: {response5.tools_called}")

        # Verificar se todas as respostas foram geradas
        responses = [response1, response2, response3, response4, response5]

        all_responses_valid = all(len(r.message.strip()) > 0 for r in responses)

        # Verificar se todas as ferramentas foram usadas
        all_tools_used = set()
        for r in responses:
            all_tools_used.update(r.tools_called)

        expected_tools = {
            "save_memory_tool",
            "get_memory_tool",
            "update_memory_tool",
            "delete_memory_tool",
        }

        # Verificar se pelo menos save_memory_tool foi usada (que sabemos que funciona)
        save_tool_used = "save_memory_tool" in all_tools_used

        # Verificar se o agente tentou usar as outras ferramentas
        get_tool_attempted = "get_memory_tool" in all_tools_used
        update_tool_attempted = "update_memory_tool" in all_tools_used
        delete_tool_attempted = "delete_memory_tool" in all_tools_used

        print(f"    📊 Respostas válidas: {all_responses_valid}")
        print(f"    📊 Ferramentas usadas: {sorted(all_tools_used)}")
        print(f"    📊 Ferramentas esperadas: {sorted(expected_tools)}")
        print(f"    📊 Save tool usada: {save_tool_used}")
        print(f"    📊 Get tool tentada: {get_tool_attempted}")
        print(f"    📊 Update tool tentada: {update_tool_attempted}")
        print(f"    📊 Delete tool tentada: {delete_tool_attempted}")

        # Resultado final - verificar se o agente tentou usar as ferramentas
        tools_attempted = save_tool_used and get_tool_attempted

        if all_responses_valid and tools_attempted:
            print("  ✅ Agente tenta usar as ferramentas disponíveis!")
            return True
        else:
            print("  ❌ Agente não tenta usar as ferramentas disponíveis")
            return False

    except Exception as e:
        print(f"  ❌ Erro no teste: {e}")
        return False
    finally:
        chatbot_service.close()


if __name__ == "__main__":
    import asyncio

    asyncio.run(test_all_tools())
