# -*- coding: utf-8 -*-
from src.evaluations.core.eval import (
    EvaluationTask,
    EvaluationResult,
    MultiTurnEvaluationInput,
    BaseMultipleTurnEvaluator,
)
from src.utils.log import logger


def estimate_tokens_from_text(text: str) -> int:
    """
    Estima o número de tokens baseado no comprimento do texto.
    
    Regra aproximada: 
    - Português: ~0.75 tokens por palavra (4 chars/palavra em média)
    - 1 token ≈ 4 caracteres em média
    
    Returns:
        Número estimado de tokens
    """
    if not text:
        return 0
    
    # Remove espaços extras
    text = text.strip()
    
    # Estimativa: 1 token para cada 4 caracteres
    # Isso é uma aproximação conservadora para português
    estimated_tokens = len(text) / 4
    
    return int(estimated_tokens)


class TokenUsageTotalEvaluator(BaseMultipleTurnEvaluator):
    """
    Calcula o total de tokens consumidos na conversa completa (input + output).
    
    Como os valores de usage_statistics podem retornar 0, este avaliador
    faz uma estimativa manual baseada no comprimento do texto em caracteres.
    
    Inclui:
    - Todos os tokens das mensagens do usuário
    - Todos os tokens das respostas do agente
    - Estimativa dos tokens de reasoning
    - Estimativa dos tokens de tool_calls e tool_responses (se presentes)
    
    Objetivo: Comparar economia de tokens entre V1 (memória total) e V2 (memória restrita).
    """

    name = "token_usage_total"

    async def evaluate(
        self, agent_response: MultiTurnEvaluationInput, task: EvaluationTask
    ) -> EvaluationResult:
        """
        Calcula tokens estimados através da contagem de caracteres.
        """
        try:
            transcript = agent_response.transcript
            
            total_tokens_estimated = 0
            user_tokens = 0
            agent_tokens = 0
            reasoning_tokens = 0
            tool_tokens = 0
            
            token_breakdown_by_turn = []
            
            # Itera sobre todos os turnos da conversa
            for turn in transcript:
                turn_total = 0
                turn_user = 0
                turn_agent = 0
                turn_reasoning = 0
                turn_tool = 0
                
                # Tokens da mensagem do usuário
                if turn.user_message:
                    turn_user = estimate_tokens_from_text(turn.user_message)
                    user_tokens += turn_user
                    turn_total += turn_user
                
                # Tokens da resposta do agente
                if turn.agent_message:
                    turn_agent = estimate_tokens_from_text(turn.agent_message)
                    agent_tokens += turn_agent
                    turn_total += turn_agent
                
                # Tokens do reasoning_trace
                if turn.agent_reasoning_trace:
                    for step in turn.agent_reasoning_trace:
                        if step.message_type == "reasoning_message" and step.content:
                            step_tokens = estimate_tokens_from_text(str(step.content))
                            turn_reasoning += step_tokens
                            reasoning_tokens += step_tokens
                        
                        # Tokens de tool_call
                        elif step.message_type == "tool_call_message" and step.content:
                            step_tokens = estimate_tokens_from_text(str(step.content))
                            turn_tool += step_tokens
                            tool_tokens += step_tokens
                        
                        # Tokens de tool_response
                        elif step.message_type == "tool_return_message" and step.content:
                            # Tool responses podem ser grandes
                            step_tokens = estimate_tokens_from_text(str(step.content))
                            turn_tool += step_tokens
                            tool_tokens += step_tokens
                    
                    turn_total += turn_reasoning + turn_tool
                
                if turn_total > 0:
                    token_breakdown_by_turn.append({
                        "turn": turn.turn,
                        "total_tokens": turn_total,
                        "user_tokens": turn_user,
                        "agent_tokens": turn_agent,
                        "reasoning_tokens": turn_reasoning,
                        "tool_tokens": turn_tool,
                    })
                
                total_tokens_estimated += turn_total
            
            # Prepara anotações detalhadas
            annotations = {
                "estimation_method": "character_count",
                "total_tokens_estimated": total_tokens_estimated,
                "user_tokens": user_tokens,
                "agent_tokens": agent_tokens,
                "reasoning_tokens": reasoning_tokens,
                "tool_tokens": tool_tokens,
                "breakdown_by_turn": token_breakdown_by_turn,
                "num_turns": len(transcript),
                "note": "Tokens estimated using 1 token ≈ 4 characters rule"
            }
            
            return EvaluationResult(
                score=total_tokens_estimated,
                annotations=str(annotations),
                has_error=False,
                error_message=None,
            )

        except Exception as e:
            logger.error(
                f"Erro ao avaliar token_usage_total: {e}",
                exc_info=True,
            )
            return EvaluationResult(
                score=None,
                annotations=None,
                has_error=True,
                error_message=str(e),
            )
