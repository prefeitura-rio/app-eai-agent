from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_core.language_models.chat_models import BaseChatModel
from typing import Literal, Optional

# --- Embedding Service ---


class EmbeddingService:
    """
    Serviço para gerar embeddings. Atualmente usa o Google GenAI.
    """

    def __init__(self, model_name: str = "models/embedding-001"):
        self.client = GoogleGenerativeAIEmbeddings(model=model_name)

    def get_embedding(self, text: str) -> list[float]:
        """
        Gera o embedding para um determinado texto.
        """
        return self.client.embed_query(text)

    def get_embeddings(self, texts: list[str]) -> list[list[float]]:
        """
        Gera embeddings para uma lista de textos de forma otimizada.
        """
        return self.client.embed_documents(texts)


# --- Chat Model Service ---

Provider = Literal["google"]


class ChatModelFactory:
    """
    Factory para criar instâncias de modelos de chat de diferentes provedores.
    """

    @staticmethod
    def create(
        provider: Provider,
        model_name: Optional[str] = None,
        temperature: Optional[float] = 0.7,
    ) -> BaseChatModel:
        """
        Cria e retorna uma instância de um modelo de chat com base no provedor.

        Args:
            provider: O provedor do modelo (ex: "google").
            model_name: O nome específico do modelo.
            temperature: A temperatura para a geração do modelo.

        Returns:
            Uma instância de um modelo de chat que herda de BaseChatModel.

        Raises:
            ValueError: Se o provedor não for suportado.
        """
        if provider == "google":
            if not model_name:
                model_name = "gemini-2.5-flash-lite"
            if not temperature:
                temperature = 0.7
            return ChatGoogleGenerativeAI(model=model_name, temperature=temperature)
        # Futuramente, outros provedores podem ser adicionados aqui.
        # elif provider == "openai":
        #     return ChatOpenAI(model=model_name, temperature=temperature)
        else:
            raise ValueError(f"Provedor '{provider}' não é suportado.")


# Exemplo de como instanciar o modelo que será usado no service.py
# Isso centraliza a configuração do modelo.
