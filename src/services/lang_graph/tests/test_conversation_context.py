import uuid
import logging
from src.services.lang_graph.service import LangGraphChatbotService

logger = logging.getLogger(__name__)


def test_conversation_context():
    """Testa se o chatbot está usando o contexto da conversa corretamente."""
    print("💬 Testando contexto da conversa...")
    
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
            message="Oi, eu sou o Batman!"
        )
        print(f"    🤖 Resposta 1: {response1.message[:100]}...")
        
        # Teste 2: Segunda mensagem - perguntando sobre a primeira
        print("  📝 Teste 2: Perguntando sobre a primeira mensagem...")
        response2 = chatbot_service.process_message(
            user_id=user_id,
            thread_id=thread_id,
            message="Quem eu disse que eu era?"
        )
        print(f"    🤖 Resposta 2: {response2.message[:100]}...")
        
        # Verificar se a segunda resposta menciona "Batman"
        response2_lower = response2.message.lower()
        mentions_batman = "batman" in response2_lower
        
        print(f"    ✅ Menciona Batman: {mentions_batman}")
        
        # Teste 3: Terceira mensagem - perguntando sobre contexto
        print("  📝 Teste 3: Perguntando sobre contexto da conversa...")
        response3 = chatbot_service.process_message(
            user_id=user_id,
            thread_id=thread_id,
            message="Qual foi minha primeira mensagem nesta conversa?"
        )
        print(f"    🤖 Resposta 3: {response3.message[:100]}...")
        
        # Verificar se menciona a primeira mensagem
        response3_lower = response3.message.lower()
        mentions_first_message = any(word in response3_lower for word in ["oi", "eu sou", "batman"])
        
        print(f"    ✅ Menciona primeira mensagem: {mentions_first_message}")
        
        # Teste 4: Nova thread - verificar isolamento
        print("  📝 Teste 4: Testando isolamento com nova thread...")
        new_thread_id = str(uuid.uuid4())
        response4 = chatbot_service.process_message(
            user_id=user_id,
            thread_id=new_thread_id,
            message="Quem eu disse que eu era?"
        )
        print(f"    🤖 Resposta 4 (nova thread): {response4.message[:100]}...")
        
        # Verificar se a nova thread não tem acesso ao contexto anterior
        response4_lower = response4.message.lower()
        mentions_batman_in_new_thread = "batman" in response4_lower
        
        print(f"    🔒 Nova thread não menciona Batman: {not mentions_batman_in_new_thread}")
        
        # Resultado final
        if mentions_batman and mentions_first_message and not mentions_batman_in_new_thread:
            print("  ✅ Contexto da conversa funcionando corretamente!")
            return True
        else:
            print("  ❌ Contexto da conversa não está funcionando como esperado")
            return False
            
    except Exception as e:
        print(f"  ❌ Erro no teste: {e}")
        return False
    finally:
        chatbot_service.close()


if __name__ == "__main__":
    test_conversation_context() 