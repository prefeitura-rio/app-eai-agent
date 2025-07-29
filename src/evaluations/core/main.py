import asyncio
import json
import os
from dotenv import load_dotenv

# Carrega as variáveis de ambiente do arquivo .env
# Certifique-se de ter um .env na raiz do projeto com OPENAI_API_KEY e GEMINI_API_KEY
load_dotenv()

from .dataloader import DataLoader
from .llm_clients import OpenAIClient, GeminiClient
from .evals import LLMJudgeEvaluation, KeywordMatchEvaluation, RegexMatchEvaluation
from .runner import AsyncExperimentRunner

async def run_evaluation_experiment():
    """
    Configura e executa um experimento de avaliação de ponta a ponta.
    """
    print("--- Configurando o Experimento de Avaliação ---")

    # --- 1. Configuração do DataLoader ---
    # Usaremos a planilha do Google Sheets como nossa fonte de dados.
    # As tarefas devem ter as colunas 'id', 'prompt', e 'golden_response'.
    gsheet_url = "https://docs.google.com/spreadsheets/d/1VPnJSf9puDgZ-Ed9MRkpe3Jy38nKxGLp7O9-ydAdm98/edit?gid=370781785"
    try:
        loader = DataLoader(
            source=gsheet_url,
            id_col="id",
            # 'prompt' será usado pelo gerador, 'golden_response' pelos avaliadores.
            metadata_cols=["prompt", "golden_response"]
        )
        print(f"✅ DataLoader configurado com a fonte: {gsheet_url}")
    except Exception as e:
        print(f"❌ Erro ao configurar o DataLoader: {e}")
        return

    # --- 2. Configuração do Modelo a ser Testado (Gerador) ---
    # Vamos testar o 'gpt-4o' da OpenAI como nosso modelo principal.
    generator = OpenAIClient(model_name="gpt-4o")
    print(f"✅ Modelo a ser avaliado (Gerador): {generator.model_name}")

    # --- 3. Configuração das Avaliações ---
    # Definimos uma lista de avaliações que serão executadas em paralelo para cada resposta gerada.
    
    # Avaliação 1: Juiz LLM (Gemini) para verificar a similaridade semântica.
    semantic_judge_prompt = """
    Avalie a similaridade semântica entre a Resposta Gerada e a Resposta de Referência (Golden).
    Retorne um JSON com as chaves 'score' (um float de 0.0 a 1.0) e 'reasoning' (uma breve explicação).

    Golden Response: "{task[golden_response]}"
    Generated Answer: "{generated_answer}"

    JSON de avaliação:
    """
    gemini_judge = GeminiClient(model_name="gemini-1.5-flash-latest")
    semantic_evaluation = LLMJudgeEvaluation(
        name="similaridade_semantica_gemini",
        judge_client=gemini_judge,
        prompt_template=semantic_judge_prompt
    )

    # Avaliação 2: Verificação de palavra-chave.
    # Vamos verificar se a resposta contém o CEP esperado para uma das perguntas.
    keyword_evaluation = KeywordMatchEvaluation(name="contem_cep_correto", keywords=["01310-100"])

    # Avaliação 3: Verificação de formato com Regex.
    # Verifica se a resposta contém um número no formato de CEP.
    regex_evaluation = RegexMatchEvaluation(name="formato_cep_valido", regex_pattern=r"\d{5}-\d{3}")

    evaluations = [
        semantic_evaluation,
        keyword_evaluation,
        regex_evaluation
    ]
    print(f"✅ {len(evaluations)} avaliações configuradas: {[e.name for e in evaluations]}")

    # --- 4. Configuração e Execução do Runner ---
    runner = AsyncExperimentRunner(generator=generator, evaluations=evaluations)
    print("\n--- Iniciando a Execução do Experimento ---")
    
    results = await runner.run(loader)

    # --- 5. Salvando e Exibindo os Resultados ---
    output_dir = "evaluation_results"
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, f"results_{generator.model_name}.json")

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=4, ensure_ascii=False)

    print(f"\n--- Experimento Concluído ---")
    print(f"✅ Resultados salvos em: {output_path}")

    # Imprime o resultado da primeira tarefa como exemplo
    if results:
        print("\nExemplo de resultado para a primeira tarefa:")
        print(json.dumps(results[0], indent=4, ensure_ascii=False))


if __name__ == "__main__":
    try:
        asyncio.run(run_evaluation_experiment())
    except Exception as e:
        print(f"Ocorreu um erro fatal durante a execução do experimento: {e}")
