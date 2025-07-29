import abc
import asyncio
import json
from typing import Dict, Any, List, Union

# Importa os clientes que serão usados como Juízes
from .llm_clients import AzureOpenAIClient, GeminiAIClient

# --- Classe Base para Avaliações ---

class Evaluation(abc.ABC):
    """Classe base para qualquer tipo de avaliação."""
    def __init__(self, name: str):
        self.name = name

    @abc.abstractmethod
    async def run(self, evaluated_result: Dict[str, Any], task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executa a avaliação.

        Args:
            evaluated_result (Dict[str, Any]): O objeto de resultado completo retornado
                                               pelo EvaluatedLLMClient.
            task (Dict[str, Any]): A tarefa original do DataLoader, contendo metadados
                                   como a resposta de referência (golden_response).

        Returns:
            Dict[str, Any]: Um dicionário contendo o resultado da avaliação.
        """
        pass

# --- Avaliações baseadas em LLM (Juízes) ---

class LLMJudgeEvaluation(Evaluation):
    """
    Uma avaliação que usa um cliente LLM (Juiz) para avaliar uma resposta.
    """
    def __init__(
        self,
        name: str,
        judge_client: Union[AzureOpenAIClient, GeminiAIClient],
        prompt_template: str,
    ):
        super().__init__(name)
        self.judge_client = judge_client
        self.prompt_template = prompt_template

    async def run(self, evaluated_result: Dict[str, Any], task: Dict[str, Any]) -> Dict[str, Any]:
        """Formata o prompt e executa o julgamento."""
        try:
            # O template pode acessar a resposta final com {output} e a tarefa com {task[...]}
            prompt = self.prompt_template.format(
                output=evaluated_result.get("output", ""),
                task=task
            )
            
            judgement_response = await self.judge_client.execute(prompt)
            
            # Tenta parsear a resposta como JSON, se não, retorna como texto.
            try:
                result_data = json.loads(judgement_response)
            except (json.JSONDecodeError, TypeError):
                result_data = {"raw_response": judgement_response}

            return {"eval_name": self.name, "result": result_data}
        except KeyError as e:
            return {"eval_name": self.name, "error": f"Chave não encontrada no template: {e}"}
        except Exception as e:
            return {"eval_name": self.name, "error": f"Erro durante a execução do juiz: {e}"}

# --- Avaliações Não-LLM (Baseadas em Regras) ---

class ContentMatchEvaluation(Evaluation):
    """Avalia se a resposta final contém uma ou mais palavras-chave."""
    def __init__(self, name: str, keywords: List[str], case_sensitive: bool = False):
        super().__init__(name)
        self.keywords = keywords
        self.case_sensitive = case_sensitive

    async def run(self, evaluated_result: Dict[str, Any], task: Dict[str, Any]) -> Dict[str, Any]:
        final_answer = evaluated_result.get("output", "")
        answer_to_check = final_answer if self.case_sensitive else final_answer.lower()
        
        found = [kw for kw in self.keywords if (kw if self.case_sensitive else kw.lower()) in answer_to_check]
        
        return {"eval_name": self.name, "score": 1.0 if found else 0.0, "found_keywords": found}

class ToolUsageEvaluation(Evaluation):
    """Verifica se uma ferramenta específica foi usada na cadeia de pensamento."""
    def __init__(self, name: str, tool_name: str):
        super().__init__(name)
        self.tool_name = tool_name

    async def run(self, evaluated_result: Dict[str, Any], task: Dict[str, Any]) -> Dict[str, Any]:
        tool_used = False
        try:
            messages = evaluated_result.get("data", {}).get("messages", [])
            for msg in messages:
                # A lógica exata aqui dependerá de como o uso de ferramentas é logado.
                # Este é um exemplo baseado em um possível formato de 'reasoning'.
                if msg.get("message_type") == "reasoning_message":
                    reasoning = msg.get("reasoning", "")
                    if f"using tool {self.tool_name}" in reasoning.lower():
                        tool_used = True
                        break
            return {"eval_name": self.name, "score": 1.0 if tool_used else 0.0, "tool_checked": self.tool_name}
        except Exception as e:
            return {"eval_name": self.name, "error": f"Erro ao analisar o uso de ferramentas: {e}"}


# --- Bloco de Exemplo ---

async def main():
    """Função de exemplo para demonstrar o uso das classes de avaliação."""
    
    # 1. Juiz LLM para a avaliação
    judge = AzureOpenAIClient(model_name="gpt-4o")

    # 2. Template de prompt para o juiz
    judge_prompt = """
    Avalie a qualidade da resposta da IA. A resposta esperada era '{task[golden_response]}'.
    A resposta gerada foi: '{output}'.
    A resposta está correta e completa? Responda com um JSON contendo 'score' (0.0 a 1.0) e 'reasoning'.
    """

    # 3. Instanciar as avaliações
    llm_eval = LLMJudgeEvaluation(name="correcao_openai", judge_client=judge, prompt_template=judge_prompt)
    content_eval = ContentMatchEvaluation(name="contem_batman", keywords=["Batman"])

    # 4. Dados de exemplo (como viriam do Runner)
    sample_task = {"id": 1, "golden_response": "Eu sou o Batman."}
    sample_result_from_evaluated_client = {
      "status": "completed",
      "output": "Eu sou o Batman."
    }

    # 5. Executar avaliações em paralelo
    results = await asyncio.gather(
        llm_eval.run(sample_result_from_evaluated_client, sample_task),
        content_eval.run(sample_result_from_evaluated_client, sample_task)
    )

    print(json.dumps(results, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    asyncio.run(main())