import json
import csv
import asyncio
from pathlib import Path
from typing import List, Dict, Any
from src.utils.md_to_wpp import markdown_to_whatsapp
from src.evaluations.core.eval.log import logger


def parse_reasoning_messages(messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Transforma a lista de mensagens brutas da API em uma estrutura limpa e padronizada.
    """
    if not messages:
        return []

    parsed_list = []
    for msg in messages:
        message_type = msg.get("message_type")
        content = None

        if message_type == "assistant_message":
            content = msg.get("content")
            # content = markdown_to_whatsapp(content)
        elif message_type == "reasoning_message":
            content = msg.get("reasoning")
        elif message_type == "tool_return_message":
            tool_return = msg.get("tool_return", "{}")

            try:
                parsed_tool_return = json.loads(tool_return)
            except (json.JSONDecodeError, TypeError):
                parsed_tool_return = tool_return
            content = {"name": msg.get("name"), "tool_return": parsed_tool_return}

        elif message_type == "tool_call_message":
            tool_call = msg.get("tool_call", {})
            # Tenta fazer o parse dos argumentos, com fallback para string
            arguments = tool_call.get("arguments", "{}")
            try:
                parsed_args = json.loads(arguments)
            except (json.JSONDecodeError, TypeError):
                parsed_args = arguments
            content = {
                "name": tool_call.get("name"),
                "arguments": parsed_args,
            }
        elif message_type == "hidden_reasoning_message":
            content = msg.get("hidden_reasoning")
        elif message_type in ["system_message", "user_message"]:
            content = msg.get("content")
        elif message_type == "usage_statistics":
            content = {
                # "agent_name": msg.get("agent_name"),
                # "agent_id": msg.get("agent_id"),
                "user_number": msg.get("user_number"),
                "message_id": msg.get("message_id"),
                "processed_at": msg.get("processed_at"),
                "total_tokens": msg.get("total_tokens"),
                "prompt_tokens": msg.get("prompt_tokens"),
                "completion_tokens": msg.get("completion_tokens"),
                "step_count": msg.get("step_count"),
                "steps_messages": msg.get("steps_messages"),
                "run_ids": msg.get("run_ids"),
            }

        # Tenta fazer o parse do conteúdo se for uma string JSON, com fallback
        if isinstance(content, str):
            try:
                # Evita que strings simples como "Paris." sejam convertidas para JSON
                if content.strip().startswith(("{", "[")):
                    content = json.loads(content)
            except (json.JSONDecodeError, TypeError):
                pass  # Mantém como string se o parse falhar

        if message_type:
            parsed_list.append({"message_type": message_type, "content": content})

    return parsed_list


async def process_csv_with_criteria_generation(
    csv_input_path: str,
    csv_output_path: str,
    prompt_template: str = "",
    model_name: str = "gemini-2.5-flash-exp",
) -> None:
    """
    Lê um CSV com as colunas: mensagem_whatsapp_simulada, golden_answer_criteria, golden_answer.
    Para cada linha onde golden_answer_criteria está vazio, chama o LLM para gerar o conteúdo.
    Salva o CSV atualizado no caminho especificado.

    Args:
        csv_input_path: Caminho do arquivo CSV de entrada
        csv_output_path: Caminho onde o CSV atualizado será salvo
        prompt_template: Template do prompt a ser enviado ao LLM. Pode conter {mensagem_whatsapp_simulada} e {golden_answer}
        model_name: Nome do modelo Gemini a ser usado
    """
    from src.evaluations.core.eval.llm_clients import GeminiAIClient

    logger.info(f"Iniciando processamento do CSV: {csv_input_path}")

    # Validar que o arquivo existe
    input_path = Path(csv_input_path)
    if not input_path.exists():
        raise FileNotFoundError(f"Arquivo CSV não encontrado: {csv_input_path}")

    # Ler o CSV
    rows = []
    with open(csv_input_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        required_columns = {
            "mensagem_whatsapp_simulada",
            "golden_answer_criteria",
            "golden_answer",
        }

        # Validar que as colunas necessárias existem
        if not required_columns.issubset(set(reader.fieldnames or [])):
            raise ValueError(
                f"CSV deve conter as colunas: {required_columns}. Encontradas: {reader.fieldnames}"
            )

        for row in reader:
            rows.append(row)

    logger.info(f"Total de linhas lidas: {len(rows)}")

    # Inicializar o cliente Gemini
    gemini_client = GeminiAIClient(model_name=model_name)

    # Processar cada linha
    rows_to_process = [
        (idx, row)
        for idx, row in enumerate(rows)
        if not row.get("golden_answer_criteria", "").strip()
    ]

    logger.info(
        f"Linhas que precisam ser processadas (golden_answer_criteria vazio): {len(rows_to_process)}"
    )

    for idx, row in rows_to_process:
        mensagem = row.get("mensagem_whatsapp_simulada", "")
        golden_answer = row.get("golden_answer", "")

        logger.info(f"Processando linha {idx + 1}/{len(rows)}...")

        # Montar o prompt
        if prompt_template:
            prompt = prompt_template.format(
                mensagem_whatsapp_simulada=mensagem, golden_answer=golden_answer
            )
        else:
            # Prompt padrão caso nenhum seja fornecido
            prompt = f"Mensagem: {mensagem}\nResposta: {golden_answer}"

        try:
            # Chamar o LLM
            criteria = await gemini_client.execute(prompt)
            row["golden_answer_criteria"] = criteria.strip()
            logger.info(f"Critério gerado para linha {idx + 1}")

        except Exception as e:
            logger.error(
                f"Erro ao processar linha {idx + 1}: {e}", exc_info=True
            )
            row["golden_answer_criteria"] = f"ERRO: {str(e)}"

    # Salvar o CSV atualizado
    output_path = Path(csv_output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(csv_output_path, "w", encoding="utf-8", newline="") as f:
        if rows:
            writer = csv.DictWriter(f, fieldnames=rows[0].keys())
            writer.writeheader()
            writer.writerows(rows)

    logger.info(f"CSV atualizado salvo em: {csv_output_path}")

