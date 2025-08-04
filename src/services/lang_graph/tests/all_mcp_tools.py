import uuid
from src.services.lang_graph.service import LangGraphChatbotService
from src.utils.log import logger


async def test_all_mcp_tools():
    """Testa se o agente consegue usar todas as ferramentas MCP disponíveis."""
    logger.info("🔧 Testando uso de todas as ferramentas MCP...")

    try:
        # Inicializar serviço
        chatbot_service = LangGraphChatbotService()

        # Usar user_id único para garantir isolamento
        user_id = f"test_all_mcp_tools_user_{uuid.uuid4()}"

        logger.info(f"  👤 User ID: {user_id}")

        # Teste 1: Calculadora - Expressão matemática complexa
        logger.info("  📝 Teste 1: Calculadora - Expressão matemática complexa...")
        thread_id_1 = str(uuid.uuid4())
        response1 = await chatbot_service.process_message(
            user_id=user_id,
            thread_id=thread_id_1,
            message="Calcule a seguinte expressão matemática complexa: (15 + 7) * 3 - 8 / 2 + 5^2. Mostre cada passo do cálculo.",
        )
        logger.info(f"    🤖 Resposta 1: {response1.message[:200]}...")
        logger.info(f"    🔧 Ferramentas usadas: {response1.tools_called}")

        # Teste 2: Time Current - Verificar hora atual
        logger.info("  📝 Teste 2: Time Current - Verificar hora atual...")
        thread_id_2 = str(uuid.uuid4())
        response2 = await chatbot_service.process_message(
            user_id=user_id,
            thread_id=thread_id_2,
            message="Que horas são agora no Rio de Janeiro?",
        )
        logger.info(f"    🤖 Resposta 2: {response2.message[:200]}...")
        logger.info(f"    🔧 Ferramentas usadas: {response2.tools_called}")

        # Teste 3: Google Search - Pesquisar presidente de Tuvalu
        logger.info("  📝 Teste 3: Google Search - Pesquisar presidente de Tuvalu...")
        thread_id_3 = str(uuid.uuid4())
        response3 = await chatbot_service.process_message(
            user_id=user_id,
            thread_id=thread_id_3,
            message="Quem é o atual primeiro ministro de Tuvalu?",
        )
        logger.info(f"    🤖 Resposta 3: {response3.message[:200]}...")
        logger.info(f"    🔧 Ferramentas usadas: {response3.tools_called}")

        # Teste 4: Equipments Instructions - Atendimento médico
        logger.info("  📝 Teste 4: Equipments Instructions - Atendimento médico...")
        thread_id_4 = str(uuid.uuid4())
        response4 = await chatbot_service.process_message(
            user_id=user_id,
            thread_id=thread_id_4,
            message="Preciso de atendimento médico urgente, quebrei a perna. Onde posso ir?",
        )
        logger.info(f"    🤖 Resposta 4: {response4.message[:200]}...")
        logger.info(f"    🔧 Ferramentas usadas: {response4.tools_called}")

        # Verificar se todas as respostas foram geradas
        responses = [response1, response2, response3, response4]
        all_responses_valid = all(len(r.message.strip()) > 0 for r in responses)

        # Verificar se as ferramentas MCP foram usadas
        all_tools_used = set()
        for r in responses:
            all_tools_used.update(r.tools_called)

        # Ferramentas MCP esperadas
        expected_mcp_tools = {
            "calculator_add",
            "calculator_subtract",
            "calculator_multiply",
            "calculator_divide",
            "calculator_power",
            "time_current",
            "google_search",
            "equipments_instructions",
        }

        # Verificar uso específico de cada categoria de ferramenta
        calculator_tools_used = any(
            tool.startswith("calculator_") for tool in all_tools_used
        )
        time_tool_used = "time_current" in all_tools_used
        search_tool_used = "google_search" in all_tools_used
        equipments_tool_used = "equipments_instructions" in all_tools_used

        # Verificar se a resposta sobre Tuvalu contém "Feleti Teo"
        tuvalu_response_contains_feleti = "Feleti Teo" in response3.message

        # Verificar se o resultado da calculadora contém o valor esperado (87)
        calculator_result_contains_87 = "87" in response1.message

        logger.info(f"    📊 Respostas válidas: {all_responses_valid}")
        logger.info(f"    📊 Ferramentas usadas: {sorted(all_tools_used)}")
        logger.info(f"    📊 Ferramentas MCP esperadas: {sorted(expected_mcp_tools)}")
        logger.info(f"    📊 Calculadora usada: {calculator_tools_used}")
        logger.info(f"    📊 Time tool usada: {time_tool_used}")
        logger.info(f"    📊 Search tool usada: {search_tool_used}")
        logger.info(f"    📊 Equipments tool usada: {equipments_tool_used}")
        logger.info(
            f"    📊 Resposta Tuvalu contém 'Feleti Teo': {tuvalu_response_contains_feleti}"
        )
        logger.info(
            f"    📊 Resultado calculadora contém '87': {calculator_result_contains_87}"
        )

        # Resultado final - verificar se o agente usou as ferramentas MCP corretamente
        mcp_tools_working = (
            calculator_tools_used
            and time_tool_used
            and search_tool_used
            and equipments_tool_used
        )

        if all_responses_valid and mcp_tools_working:
            logger.info("  ✅ Agente usa as ferramentas MCP corretamente!")
            if tuvalu_response_contains_feleti:
                logger.info("  ✅ Resposta sobre Tuvalu contém informação correta!")
            else:
                logger.info(
                    "  ⚠️ Resposta sobre Tuvalu pode não conter informação esperada"
                )
            if calculator_result_contains_87:
                logger.info("  ✅ Resultado da calculadora está correto!")
            else:
                logger.info("  ⚠️ Resultado da calculadora pode estar incorreto")
            return True
        else:
            logger.info("  ❌ Agente não usa as ferramentas MCP corretamente")
            return False

    except Exception as e:
        logger.info(f"  ❌ Erro no teste: {e}")
        return False
    finally:
        chatbot_service.close()


if __name__ == "__main__":
    import asyncio

    asyncio.run(test_all_mcp_tools())
