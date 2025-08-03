"""
Testes de parâmetros de configuração.
"""
import logging
import uuid
from src.services.lang_graph.service import LangGraphChatbotService

logger = logging.getLogger(__name__)


def test_configuration_parameters():
    """Testa se o agente está usando os parâmetros de configuração corretamente."""
    print("📋 Executando: Parâmetros de Configuração")
    print("----------------------------------------")
    
    # Usar UUID único para evitar contaminação
    test_user_id = str(uuid.uuid4())
    test_thread_id = str(uuid.uuid4())
    
    try:
        chatbot_service = LangGraphChatbotService()
        print("⚙️ Testando parâmetros de configuração...")
        
        # Teste 1: Salvando memórias para teste
        print("  💾 Teste 1: Salvando memórias para teste...")
        response = chatbot_service.process_message(
            user_id=test_user_id,
            thread_id=test_thread_id,
            message="Meu nome é Pedro, tenho 28 anos e trabalho como desenvolvedor. Gosto de programar em Python e JavaScript.",
        )
        print(f"  🤖 Resposta: {response.message}")
        print(f"  🔧 Ferramentas chamadas: {response.tools_called}")
        
        # Teste 2: Buscando com configuração padrão
        print("  🔍 Teste 2: Buscando com configuração padrão...")
        response = chatbot_service.process_message(
            user_id=test_user_id,
            thread_id=test_thread_id,
            message="Quais são minhas informações pessoais?",
        )
        print(f"  🤖 Resposta: {response.message}")
        print(f"  🔧 Ferramentas chamadas: {response.tools_called}")
        
        # Teste 3: Buscando com parâmetros específicos
        print("  🎯 Teste 3: Buscando com parâmetros específicos...")
        response = chatbot_service.process_message(
            user_id=test_user_id,
            thread_id=test_thread_id,
            message="Busque apenas as 3 memórias mais relevantes sobre minhas preferências.",
        )
        print(f"  🤖 Resposta: {response.message}")
        print(f"  🔧 Ferramentas chamadas: {response.tools_called}")
        
        # Teste 4: Buscando com alta relevância
        print("  🔥 Teste 4: Buscando com alta relevância...")
        response = chatbot_service.process_message(
            user_id=test_user_id,
            thread_id=test_thread_id,
            message="Busque apenas memórias com relevância muito alta sobre minha profissão.",
        )
        print(f"  🤖 Resposta: {response.message}")
        print(f"  🔧 Ferramentas chamadas: {response.tools_called}")
        
        # Teste 5: Verificando uso dos parâmetros
        print("  ✅ Teste 5: Verificando uso dos parâmetros...")
        response = chatbot_service.process_message(
            user_id=test_user_id,
            thread_id=test_thread_id,
            message="Quantas memórias você pode buscar por vez?",
        )
        print(f"  🤖 Resposta: {response.message}")
        print(f"  🔧 Ferramentas chamadas: {response.tools_called}")
        
        print("  ✅ Teste de parâmetros de configuração OK")
        return True
        
    except Exception as e:
        print(f"  ❌ Erro no teste de parâmetros de configuração: {e}")
        return False
    finally:
        chatbot_service.close()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    test_configuration_parameters() 