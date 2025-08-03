import uuid
import logging
from src.services.lang_graph.service import LangGraphChatbotService

logger = logging.getLogger(__name__)


def test_short_term_memory():
    """Testa se a memória de curto prazo (thread-level persistence) está funcionando."""
    print("🧠 Testando memória de curto prazo (thread-level persistence)...")
    
    try:
        # Inicializar serviço
        chatbot_service = LangGraphChatbotService()
        
        # Criar IDs únicos
        user_id = str(uuid.uuid4())
        thread_id = str(uuid.uuid4())
        
        print(f"  👤 User ID: {user_id}")
        print(f"  🧵 Thread ID: {thread_id}")
        
        # Teste 1: Primeira mensagem
        print("  📝 Teste 1: Enviando primeira mensagem...")
        response1 = chatbot_service.process_message(
            user_id=user_id,
            thread_id=thread_id,
            message="Meu nome é Alice e eu gosto de programar em Python."
        )
        print(f"    🤖 Resposta 1: {response1.message[:100]}...")
        
        # Teste 2: Segunda mensagem - perguntando sobre informações da primeira
        print("  📝 Teste 2: Perguntando sobre informações da primeira mensagem...")
        response2 = chatbot_service.process_message(
            user_id=user_id,
            thread_id=thread_id,
            message="Qual é o meu nome e o que eu gosto de fazer?"
        )
        print(f"    🤖 Resposta 2: {response2.message[:100]}...")
        
        # Verificar se a segunda resposta menciona informações da primeira
        response2_lower = response2.message.lower()
        has_name = "alice" in response2_lower
        has_programming = any(word in response2_lower for word in ["python", "programar", "programação"])
        
        print(f"    ✅ Menciona nome (Alice): {has_name}")
        print(f"    ✅ Menciona programação: {has_programming}")
        
        # Teste 3: Terceira mensagem - perguntando sobre contexto anterior
        print("  📝 Teste 3: Perguntando sobre contexto anterior...")
        response3 = chatbot_service.process_message(
            user_id=user_id,
            thread_id=thread_id,
            message="Você se lembra do que eu disse sobre mim?"
        )
        print(f"    🤖 Resposta 3: {response3.message[:100]}...")
        
        # Teste 4: Nova thread - verificar isolamento
        print("  📝 Teste 4: Testando isolamento com nova thread...")
        new_thread_id = str(uuid.uuid4())
        response4 = chatbot_service.process_message(
            user_id=user_id,
            thread_id=new_thread_id,
            message="Qual é o meu nome?"
        )
        print(f"    🤖 Resposta 4 (nova thread): {response4.message[:100]}...")
        
        # Verificar se a nova thread não tem acesso às informações da thread anterior
        response4_lower = response4.message.lower()
        mentions_alice = "alice" in response4_lower
        
        print(f"    🔒 Nova thread não menciona Alice: {not mentions_alice}")
        
        # Resultado final
        if has_name and has_programming and not mentions_alice:
            print("  ✅ Memória de curto prazo funcionando corretamente!")
            return True
        else:
            print("  ❌ Memória de curto prazo não está funcionando como esperado")
            return False
            
    except Exception as e:
        print(f"  ❌ Erro no teste: {e}")
        return False
    finally:
        chatbot_service.close()


if __name__ == "__main__":
    test_short_term_memory() 