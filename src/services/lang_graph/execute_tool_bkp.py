# def tool_execution(state: CustomMessagesState) -> CustomMessagesState:
#     """Nó para execução de ferramentas."""
#     try:
#         messages = state.get("messages", [])
#         if not messages:
#             logger.info("Nenhuma mensagem encontrada no estado")
#             return state

#         last_message = messages[-1]
#         if not isinstance(last_message, AIMessage):
#             logger.info("Última mensagem não é do assistente")
#             return state

#         # Verificar se a resposta tem tool calls
#         tool_calls = getattr(last_message, "tool_calls", [])
#         logger.info(f"Tool calls encontrados: {len(tool_calls)}")

#         # Se não há tool calls, retornar estado inalterado
#         if not tool_calls:
#             logger.info("Nenhum tool call encontrado, pulando execução")
#             return state

#         # Obter parâmetros do contexto
#         config = state.get("config")

#         logger.info(f"Executando ferramentas para user_id: {config.user_id}")

#         config = state.get("config")

#         # Criar RunnableConfig com os parâmetros que serão injetados
#         runnable_config = {
#             "configurable": {
#                 "user_id": config.user_id,
#                 "memory_limit": config.memory_limit,
#                 "memory_min_relevance": config.memory_min_relevance,
#             }
#         }

#         # TODO passar informacoes do runnable_config para a chamada da ferramenta

#         # Executar ToolNode - ele cuida de tudo automaticamente!

#         tool_outputs = state.get("tool_outputs", [])

#         for tool_call in tool_calls:
#             try:
#                 tool_name = tool_call.get("name")
#                 tool_args = tool_call.get("args", {})

#                 logger.info(f"Executando ferramenta: {tool_name} com args: {tool_args}")

#                 # Encontrar a ferramenta correspondente
#                 tool_func = None
#                 for tool in TOOLS:
#                     if tool.name == tool_name:
#                         tool_func = tool
#                         break

#                 if tool_func:
#                     # Executar a ferramenta (argumentos já injetados)
#                     result = tool_func.invoke(tool_args, config=runnable_config)
#                     logger.info(
#                         f"Ferramenta {tool_name} executada com sucesso: {result.get('success', False)}"
#                     )

#                     # Criar ToolOutput
#                     tool_output = ToolOutput(
#                         tool_name=tool_name,
#                         success=result.get("success", False),
#                         data=result,
#                     )
#                     tool_outputs.append(tool_output)
#                 else:
#                     logger.error(f"Ferramenta {tool_name} não encontrada")
#                     tool_output = ToolOutput(
#                         tool_name=tool_name,
#                         success=False,
#                         data={"error": f"Ferramenta {tool_name} não encontrada"},
#                     )
#                     tool_outputs.append(tool_output)

#             except Exception as e:
#                 logger.error(f"Erro ao executar ferramenta {tool_name}: {e}")
#                 tool_output = ToolOutput(
#                     tool_name=tool_name,
#                     success=False,
#                     data={"error": f"Erro interno: {str(e)}"},
#                 )
#                 tool_outputs.append(tool_output)

#         # Atualizar estado com tool outputs
#         state["tool_outputs"] = tool_outputs

#         return state

#     except Exception as e:
#         logger.error(f"Erro na execução de ferramentas: {e}")
#         return state
