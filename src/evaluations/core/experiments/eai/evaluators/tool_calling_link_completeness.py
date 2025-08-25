# -*- coding: utf-8 -*-
from urllib.parse import urlparse
from src.evaluations.core.eval import (
    AgentResponse,
    BaseOneTurnEvaluator,
    EvaluationResult,
    EvaluationTask,
)


class ToolCallingLinkCompletenessEvaluator(BaseOneTurnEvaluator):
    """
    Avalia se os links nas fontes do tool calling são completos (têm domínio e subdomínio/caminho).
    Links genéricos como "https://1746.rio/" são considerados incompletos.
    Links específicos como "https://www.1746.rio/hc/pt-br/articles/..." são considerados completos.
    """

    name = "tool_calling_link_completeness"

    def _is_link_complete(self, url: str) -> bool:
        """
        Verifica se um link é completo baseado na presença de:
        1. Domínio principal
        2. Subdomínio ou caminho específico
        
        Args:
            url (str): O URL a ser verificado
            
        Returns:
            bool: True se o link for completo, False caso contrário
        """
        try:
            parsed = urlparse(url)
            
            # Verifica se tem esquema e domínio
            if not parsed.scheme or not parsed.netloc:
                return False
            
            # Verifica se tem apenas o domínio principal (considerado incompleto)
            # Por exemplo: "https://1746.rio/" ou "https://1746.rio"
            domain_parts = parsed.netloc.lower().split('.')
            path = parsed.path.strip('/')
            
            # Se não tem caminho específico e é apenas um domínio simples, é incompleto
            if not path or path == '':
                # Verifica se tem subdomínio (mais de 2 partes no domínio)
                # Exemplo: www.1746.rio tem 3 partes, então tem subdomínio
                if len(domain_parts) <= 2:
                    return False
                # Se tem subdomínio mas não tem caminho, ainda consideramos incompleto
                # a menos que seja um caso específico conhecido
                return False
            
            # Se tem caminho específico, consideramos completo
            return True
            
        except Exception:
            return False

    def _extract_links_from_trace(self, agent_response: AgentResponse) -> list[str]:
        """
        Extrai links das fontes do tool calling no reasoning trace.
        """
        links = []
        tools = ["google_search"]

        if not agent_response or not agent_response.reasoning_trace:
            return links
        
        for step in agent_response.reasoning_trace:
            if step.message_type != "tool_return_message":
                continue
            
            if step.content.get("name") not in tools:
                continue

            tool_call = step.content.get("tool_return", {})
            sources = tool_call.get("sources", [])

            for source in sources:
                url = source.get("url")
                if url:
                    links.append(url) 
        
        return links

    async def evaluate(
        self, 
        agent_response: AgentResponse, 
        task: EvaluationTask
    ) -> EvaluationResult:
        try:
            tool_calling_links = self._extract_links_from_trace(agent_response)
            
            if not tool_calling_links:
                return EvaluationResult(
                    score=0,  # Se não há links nas fontes, score é 0
                    annotations="No links found in tool calling sources.",
                    has_error=False,
                    error_message=None,
                )

            link_analysis = []
            complete_links = 0
            
            for link in tool_calling_links:
                is_complete = self._is_link_complete(link)
                link_analysis.append({
                    "url": link,
                    "is_complete": is_complete,
                })
                if is_complete:
                    complete_links += 1

            # Score binário: 1 se mais de 50% dos links são completos, 0 caso contrário
            completeness_ratio = complete_links / len(tool_calling_links) if tool_calling_links else 0
            score = 1 if completeness_ratio > 0.5 else 0

            annotations = {
                "total_links": len(tool_calling_links),
                "complete_links": complete_links,
                "incomplete_links": len(tool_calling_links) - complete_links,
                "link_analysis": link_analysis,
                "completeness_ratio": completeness_ratio,
                "binary_score_threshold": 0.5
            }

            return EvaluationResult(
                score=score,
                annotations=annotations,
                has_error=False,
                error_message=None,
            )

        except Exception as e:
            return EvaluationResult(
                score=None,
                annotations=None,
                has_error=True,
                error_message=str(e),
            )
