from fastapi import APIRouter, Depends, Query, HTTPException
from loguru import logger

from src.services.llm.openai_service import OpenAIService
from src.core.security.dependencies import validar_token
from src.services.letta.agents.tools.typesense_search import typesense_search
from src.services.llm.gemini_service import GeminiService
from src.config import env
from src.services.deep_research.graph import graph, log_graph_event
from src.services.deep_research.configuration import Configuration
from langchain_core.messages import HumanMessage

router = APIRouter(
    prefix="/letta/tools",
    tags=["Letta Tools"],
    dependencies=[Depends(validar_token)],
)


@router.get("/google_search", name="Google Search")
async def google_search_tool(
    query: str = Query(..., description="Texto da consulta"),
):
    try:
        gemini_service = GeminiService()
        response = await gemini_service.google_search(
            query=query,
            model="gemini-2.5-flash-lite-preview-06-17",
            temperature=0.0,
        )

        if not response or response.get("text") is None:
            raise HTTPException(
                status_code=500, detail="Falha ao gerar resposta do Gemini"
            )

        return response
    except Exception as e:
        logger.error(f"Erro ao gerar resposta do Gemini: {e}")
        raise HTTPException(
            status_code=500, detail=f"Erro ao processar a requisição: {str(e)}"
        )


@router.get("/gpt_search", name="Busca com GPT")
async def gpt_search_tool(
    query: str = Query(..., description="Texto da consulta"),
):
    try:
        openai_service = OpenAIService()

        prompt = (
            f"Pesquise e forneça informações atualizadas sobre: {query}. "
            f"Cite as fontes e forneça uma resposta completa e informativa."
        )

        response = await openai_service.generate_content(
            text=prompt,
            model=env.GPT_SEARCH_MODEL,
            use_web_search=True,
        )

        if not response:
            raise HTTPException(
                status_code=500, detail="Nenhuma resposta recebida do serviço"
            )

        resposta_texto = response.get("resposta", "").strip()
        links = response.get("links", [])

        if not resposta_texto and links:
            response["resposta"] = (
                f"Encontrei {len(links)} fontes relevantes sobre '{query}'. Consulte os links para informações detalhadas."
            )

        elif not resposta_texto and not links:
            raise HTTPException(
                status_code=500,
                detail="Não foi possível obter informações sobre a consulta",
            )

        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro no gpt_search_tool: {e}")
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")


@router.get("/public_services_grounded_search", name="Busca Serviços Públicos")
async def public_services_grounded_search_tool(
    query: str = Query(..., description="Texto da consulta"),
):
    try:
        collections = "1746,carioca-digital"
        limit = 10
        raw_response = await typesense_search(query, collections, limit)

        # Converte resposta em lista simples de links
        resultado_lista = []

        if isinstance(raw_response, dict):
            if "hits" in raw_response:
                for h in raw_response.get("hits", []):
                    doc = h.get("document", {}) if isinstance(h, dict) else {}
                    url = doc.get("url") or doc.get("link")
                    title = doc.get("title") or doc.get("headline")
                    if url:
                        resultado_lista.append({"uri": url, "title": title})
            elif "result" in raw_response:
                for item in raw_response.get("result", []):
                    url = item.get("url") or item.get("link_acesso")
                    title = item.get("titulo") or item.get("title")
                    if url:
                        resultado_lista.append({"uri": url, "title": title})

        return {"links": resultado_lista[:limit]}
    except Exception as e:
        logger.error(f"Erro: {e}")
        raise HTTPException(
            status_code=500, detail=f"Erro ao processar a requisição: {str(e)}"
        )


@router.get("/google_deep_research", name="Google Deep Research")
async def google_deep_research(question: str) -> str:
    """
    Performs deep research on a given question using a multi-step agent.
    """
    logger.info(f"🚀 Starting research: {question}")

    # Define a configuration for the tool
    config = Configuration(
        query_generator_model="gemini-2.0-flash",
        reflection_model="gemini-2.5-flash-preview-04-17",
        answer_model="gemini-2.5-flash-preview-04-17",
        number_of_initial_queries=3,
        max_research_loops=2,
    )

    # Define the initial state with the research question
    initial_state = {"messages": [HumanMessage(content=question)]}

    # Stream the graph execution and find the final answer
    final_answer = "Could not find an answer."

    try:
        async for event in graph.astream(
            initial_state, config={"configurable": config.model_dump()}
        ):
            # Log each event
            for event_name, event_data in event.items():
                log_graph_event(event_name, event_data)

                # Check for final answer
                if event_name == "finalize_answer":
                    if "messages" in event_data and event_data["messages"]:
                        message = event_data["messages"][-1]
                        final_answer = message.content
                        logger.info("✅ Research completed")
                        break

            # Break if we found the final answer
            if "finalize_answer" in event:
                break

    except Exception as e:
        logger.error(f"❌ Research failed: {str(e)}")
        final_answer = f"Error occurred during research: {str(e)}"

    return final_answer
