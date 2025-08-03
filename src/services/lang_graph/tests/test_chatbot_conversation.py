"""
Testes de conversação do chatbot.
"""
import logging
import uuid
from src.services.lang_graph.service import LangGraphChatbotService

logger = logging.getLogger(__name__)


def test_chatbot_conversation():
    """Testa conversação básica do chatbot."""
    print("📋 Executando: Conversação do Chatbot")
    print("----------------------------------------")
    
    # Usar UUID único para evitar contaminação
    test_user_id = str(uuid.uuid4())
    test_thread_id = str(uuid.uuid4())
    
    try:
        chatbot_service = LangGraphChatbotService()
        print("💬 Testando conversação do chatbot...")
        
        # Teste 1: Mensagem simples
        print("  💭 Testando mensagem simples...")
        response = chatbot_service.process_message(
            user_id=test_user_id,
            thread_id=test_thread_id,
            message="Olá, como você está?",
        )
        print(f"  🤖 Resposta: {response.message}")
        print(f"  📊 Memórias usadas: {len(response.memories_used)}")
        print(f"  🔧 Ferramentas chamadas: {response.tools_called}")
        
        # Teste 2: Mensagem com informação para salvar
        print("  💾 Testando mensagem com informação para salvar...")
        response = chatbot_service.process_message(
            user_id=test_user_id,
            thread_id=test_thread_id,
            message="Meu nome é João e eu moro em São Paulo",
        )
        print(f"  🤖 Resposta: {response.message}")
        print(f"  📊 Memórias usadas: {len(response.memories_used)}")
        print(f"  🔧 Ferramentas chamadas: {response.tools_called}")
        
        # Teste 3: Uso de memória
        print("  🧠 Testando uso de memória...")
        response = chatbot_service.process_message(
            user_id=test_user_id,
            thread_id=test_thread_id,
            message="Qual é o meu nome?",
        )
        print(f"  🤖 Resposta: {response.message}")
        print(f"  📊 Memórias usadas: {len(response.memories_used)}")
        print(f"  🔧 Ferramentas chamadas: {response.tools_called}")
        
        print("  ✅ Conversação do chatbot OK")
        return True
        
    except Exception as e:
        print(f"  ❌ Erro na conversação do chatbot: {e}")
        return False
    finally:
        chatbot_service.close()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    test_chatbot_conversation() 