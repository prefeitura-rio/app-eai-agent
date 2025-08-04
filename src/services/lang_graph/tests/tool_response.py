import uuid
import logging
from src.services.lang_graph.service import LangGraphChatbotService

logger = logging.getLogger(__name__)


async def test_tool_response():
    """Testa se o agente responde após executar ferramentas."""
    print("🔧 Testando resposta após execução de ferramentas...")

    try:
        # Inicializar serviço
        chatbot_service = LangGraphChatbotService()

        # Criar IDs únicos
        user_id = str(uuid.uuid4())
        thread_id = str(uuid.uuid4())

        print(f"  👤 User ID: {user_id}")
        print(f"  🧵 Thread ID: {thread_id}")

        # Teste 1: Salvar informações do usuário (save_memory_tool)
        print("  📝 Teste 1: Salvando informações do usuário...")
        response1 = await chatbot_service.process_message(
            user_id=user_id,
            thread_id=thread_id,
            message="Meu nome é João Silva, tenho 28 anos e sou engenheiro de software. Eu gosto de programar em Python e JavaScript, e tenho alergia a amendoim.",
        )
        print(f"    🤖 Resposta 1: {response1.message[:100]}...")
        print(f"    🔧 Ferramentas usadas: {response1.tools_called}")

        # Teste 2: Buscar informações específicas (get_memory_tool)
        print("  📝 Teste 2: Buscando informações do usuário...")
        response2 = await chatbot_service.process_message(
            user_id=user_id,
            thread_id=thread_id,
            message="Qual é o meu nome e idade?",
        )
        print(f"    🤖 Resposta 2: {response2.message[:100]}...")
        print(f"    🔧 Ferramentas usadas: {response2.tools_called}")

        # Teste 3: Buscar preferências (get_memory_tool)
        print("  📝 Teste 3: Buscando preferências...")
        response3 = await chatbot_service.process_message(
            user_id=user_id,
            thread_id=thread_id,
            message="Quais são minhas preferências de programação?",
        )
        print(f"    🤖 Resposta 3: {response3.message[:100]}...")
        print(f"    🔧 Ferramentas usadas: {response3.tools_called}")

        # Teste 4: Buscar restrições (get_memory_tool)
        print("  📝 Teste 4: Buscando restrições...")
        response4 = await chatbot_service.process_message(
            user_id=user_id,
            thread_id=thread_id,
            message="Tenho alguma alergia ou restrição?",
        )
        print(f"    🤖 Resposta 4: {response4.message[:100]}...")
        print(f"    🔧 Ferramentas usadas: {response4.tools_called}")

        # Teste 5: Salvar nova informação (save_memory_tool)
        print("  📝 Teste 5: Salvando nova informação...")
        response5 = await chatbot_service.process_message(
            user_id=user_id,
            thread_id=thread_id,
            message="Eu também gosto de programar em Rust e tenho experiência com Docker.",
        )
        print(f"    🤖 Resposta 5: {response5.message[:100]}...")
        print(f"    🔧 Ferramentas usadas: {response5.tools_called}")

        # Teste 6: Buscar todas as informações (get_memory_tool)
        print("  📝 Teste 6: Buscando todas as informações...")
        response6 = await chatbot_service.process_message(
            user_id=user_id,
            thread_id=thread_id,
            message="Quais são todas as minhas informações?",
        )
        print(f"    🤖 Resposta 6: {response6.message[:100]}...")
        print(f"    🔧 Ferramentas usadas: {response6.tools_called}")

        # Teste 7: Buscar informações profissionais (get_memory_tool)
        print("  📝 Teste 7: Buscando informações profissionais...")
        response7 = await chatbot_service.process_message(
            user_id=user_id,
            thread_id=thread_id,
            message="O que você sabe sobre mim como profissional?",
        )
        print(f"    🤖 Resposta 7: {response7.message[:100]}...")
        print(f"    🔧 Ferramentas usadas: {response7.tools_called}")

        # Teste 8: Buscar tecnologias (get_memory_tool)
        print("  📝 Teste 8: Buscando tecnologias...")
        response8 = await chatbot_service.process_message(
            user_id=user_id,
            thread_id=thread_id,
            message="Quais tecnologias eu uso?",
        )
        print(f"    🤖 Resposta 8: {response8.message[:100]}...")
        print(f"    🔧 Ferramentas usadas: {response8.tools_called}")

        # Teste 9: Buscar restrições novamente (get_memory_tool)
        print("  📝 Teste 9: Buscando restrições novamente...")
        response9 = await chatbot_service.process_message(
            user_id=user_id,
            thread_id=thread_id,
            message="Lembre-se da minha alergia.",
        )
        print(f"    🤖 Resposta 9: {response9.message[:100]}...")
        print(f"    🔧 Ferramentas usadas: {response9.tools_called}")

        # Teste 10: Contexto da conversa (sem ferramentas)
        print("  📝 Teste 10: Usando contexto da conversa...")
        response10 = await chatbot_service.process_message(
            user_id=user_id,
            thread_id=thread_id,
            message="Qual foi a primeira coisa que eu disse sobre mim nesta conversa?",
        )
        print(f"    🤖 Resposta 10: {response10.message[:100]}...")
        print(f"    🔧 Ferramentas usadas: {response10.tools_called}")

        # Verificar se todas as respostas foram geradas
        responses = [
            response1,
            response2,
            response3,
            response4,
            response5,
            response6,
            response7,
            response8,
            response9,
            response10,
        ]

        all_responses_valid = all(len(r.message.strip()) > 0 for r in responses)

        # Verificar se pelo menos save_memory_tool foi usada
        all_tools_used = set()
        for r in responses:
            all_tools_used.update(r.tools_called)

        # Verificar se pelo menos save_memory_tool foi usada
        save_tool_used = "save_memory_tool" in all_tools_used

        print(f"    📊 Respostas válidas: {all_responses_valid}")
        print(f"    📊 Ferramentas usadas: {sorted(all_tools_used)}")
        print(f"    📊 Save tool usada: {save_tool_used}")

        # Resultado final
        if all_responses_valid and save_tool_used:
            print(
                "  ✅ Agente responde corretamente e usa ferramentas quando necessário!"
            )
            return True
        else:
            print(
                "  ❌ Agente não está respondendo corretamente ou não usa ferramentas"
            )
            return False

    except Exception as e:
        print(f"  ❌ Erro no teste: {e}")
        return False
    finally:
        chatbot_service.close()


if __name__ == "__main__":
    import asyncio

    asyncio.run(test_tool_response())
