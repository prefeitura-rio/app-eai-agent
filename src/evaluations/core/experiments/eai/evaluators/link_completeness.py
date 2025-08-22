# -*- coding: utf-8 -*-
from urllib.parse import urlparse
from src.evaluations.core.eval import EvaluationTask, EvaluationResult
from src.evaluations.core.eval.evaluators.base import BaseOneTurnEvaluator
from src.evaluations.core.eval.schemas import AgentResponse
from src.evaluations.core.experiments.eai.evaluators.utils import extract_links_from_text


class LinkCompletenessEvaluator(BaseOneTurnEvaluator):
    """
    Avalia se os links na resposta do agente são completos (têm domínio e subdomínio/caminho).
    Links genéricos como "https://1746.rio/" são considerados incompletos.
    Links específicos como "https://www.1746.rio/hc/pt-br/articles/..." são considerados completos.
    """

    name = "link_completeness"

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

    async def evaluate(
        self, agent_response: AgentResponse, task: EvaluationTask
    ) -> EvaluationResult:
        try:
            answer_links = extract_links_from_text(agent_response.message)
            
            if not answer_links:
                return EvaluationResult(
                    score=1,  # Se não há links, não há links incompletos
                    annotations="No links found in the answer.",
                    has_error=False,
                    error_message=None,
                )

            link_analysis = []
            complete_links = 0
            
            for link in answer_links:
                is_complete = self._is_link_complete(link)
                link_analysis.append({
                    "url": link,
                    "is_complete": is_complete,
                })
                if is_complete:
                    complete_links += 1

            # Score é a proporção de links completos
            score = complete_links / len(answer_links) if answer_links else 1

            annotations = {
                "total_links": len(answer_links),
                "complete_links": complete_links,
                "incomplete_links": len(answer_links) - complete_links,
                "link_analysis": link_analysis,
                "completeness_ratio": score
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
