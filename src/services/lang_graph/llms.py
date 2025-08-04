from typing import Optional
import google.generativeai as genai
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from src.config import env


class LLMConfig:
    """Configuração para modelos de linguagem e embeddings."""

    def __init__(self):
        # Configurar API key
        genai.configure(api_key=env.GEMINI_API_KEY)

        # Modelos
        self.chat_model_name = "gemini-2.5-flash-lite"
        self.embedding_model_name = "models/text-embedding-004"

        # Parâmetros do chat model
        self.temperature = 0.7
        self.max_tokens = 100_000
        self.top_p = 0.9
        self.top_k = 40

        # Parâmetros do embedding
        self.embedding_dimension = 768

    def get_chat_model(
        self, model_name: Optional[str] = None, temperature: Optional[float] = None
    ) -> ChatGoogleGenerativeAI:
        """Retorna o modelo de chat configurado."""
        model = model_name or self.chat_model_name
        temp = temperature if temperature is not None else self.temperature

        return ChatGoogleGenerativeAI(
            model=model,
            temperature=temp,
            max_output_tokens=self.max_tokens,
            top_p=self.top_p,
            top_k=self.top_k,
            google_api_key=env.GEMINI_API_KEY,
            # Configuração de retry mais robusta
            max_retries=3,
            retry_delay=2,
            timeout=30,
        )

    def get_embedding_model(
        self, model_name: Optional[str] = None
    ) -> GoogleGenerativeAIEmbeddings:
        """Retorna o modelo de embedding configurado."""
        model = model_name or self.embedding_model_name

        return GoogleGenerativeAIEmbeddings(
            model=model,
            google_api_key=env.GEMINI_API_KEY,
            task_type="retrieval_document",
            title="Memory Embedding",
        )

    def generate_embedding(self, text: str) -> list:
        """Gera embedding para um texto."""
        embedding_model = self.get_embedding_model()
        return embedding_model.embed_query(text)

    def generate_embeddings(self, texts: list) -> list:
        """Gera embeddings para uma lista de textos."""
        embedding_model = self.get_embedding_model()
        return embedding_model.embed_documents(texts)


# Instância global para uso em todo o módulo
llm_config = LLMConfig()
