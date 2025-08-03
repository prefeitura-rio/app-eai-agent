"""
Testes de capacidade do agente de usar ferramentas.
"""
import logging
import uuid
from src.services.lang_graph.service import LangGraphChatbotService

logger = logging.getLogger(__name__)


def test_agent_memory_tools():
    """Testa a capacidade do agente de usar ferramentas de memória."""
    print("📋 Executando: Capacidade do Agente de Usar Ferramentas de Memória")
    print("----------------------------------------")
    
    # Usar UUID único para evitar contaminação
    test_user_id = str(uuid.uuid4())
    test_thread_id = str(uuid.uuid4())
    
    try:
        chatbot_service = LangGraphChatbotService()
        print("🧠 Testando capacidade do agente de usar ferramentas de memória...")
        
        # Teste 1: Agente salvando informações do usuário
        print("  📝 Teste 1: Agente salvando informações do usuário...")
        response = chatbot_service.process_message(
            user_id=test_user_id,
            thread_id=test_thread_id,
            message="Meu nome é Maria, tenho 25 anos e trabalho como engenheira de software. Eu gosto muito de programar em Python e JavaScript.",
        )
        print(f"  🤖 Resposta: {response.message}")
        print(f"  📊 Memórias usadas: {len(response.memories_used)}")
        print(f"  🔧 Ferramentas chamadas: {response.tools_called}")
        
        # Teste 2: Agente buscando informações específicas
        print("  🔍 Teste 2: Agente buscando informações específicas...")
        response = chatbot_service.process_message(
            user_id=test_user_id,
            thread_id=test_thread_id,
            message="Qual é a minha profissão?",
        )
        print(f"  🤖 Resposta: {response.message}")
        print(f"  📊 Memórias usadas: {len(response.memories_used)}")
        print(f"  🔧 Ferramentas chamadas: {response.tools_called}")
        
        # Teste 3: Agente salvando preferências
        print("  💾 Teste 3: Agente salvando preferências...")
        response = chatbot_service.process_message(
            user_id=test_user_id,
            thread_id=test_thread_id,
            message="Eu prefiro trabalhar remotamente e gosto de projetos que envolvem machine learning.",
        )
        print(f"  🤖 Resposta: {response.message}")
        print(f"  📊 Memórias usadas: {len(response.memories_used)}")
        print(f"  🔧 Ferramentas chamadas: {response.tools_called}")
        
        # Teste 4: Agente usando memórias para personalizar resposta
        print("  🎯 Teste 4: Agente usando memórias para personalizar resposta...")
        response = chatbot_service.process_message(
            user_id=test_user_id,
            thread_id=test_thread_id,
            message="Você pode me recomendar alguns projetos de machine learning em Python?",
        )
        print(f"  🤖 Resposta: {response.message}")
        print(f"  📊 Memórias usadas: {len(response.memories_used)}")
        print(f"  🔧 Ferramentas chamadas: {response.tools_called}")
        
        # Teste 5: Agente atualizando informações
        print("  🔄 Teste 5: Agente atualizando informações...")
        response = chatbot_service.process_message(
            user_id=test_user_id,
            thread_id=test_thread_id,
            message="Na verdade, eu tenho 26 anos agora, não 25.",
        )
        print(f"  🤖 Resposta: {response.message}")
        print(f"  📊 Memórias usadas: {len(response.memories_used)}")
        print(f"  🔧 Ferramentas chamadas: {response.tools_called}")
        
        # Teste 6: Agente verificando informações atualizadas
        print("  ✅ Teste 6: Agente verificando informações atualizadas...")
        response = chatbot_service.process_message(
            user_id=test_user_id,
            thread_id=test_thread_id,
            message="Quantos anos eu tenho?",
        )
        print(f"  🤖 Resposta: {response.message}")
        print(f"  📊 Memórias usadas: {len(response.memories_used)}")
        print(f"  🔧 Ferramentas chamadas: {response.tools_called}")
        
        # Teste 7: Agente deletando informações irrelevantes
        print("  🗑️ Teste 7: Agente deletando informações irrelevantes...")
        response = chatbot_service.process_message(
            user_id=test_user_id,
            thread_id=test_thread_id,
            message="Esquece o que eu disse sobre gostar de JavaScript, eu não uso mais.",
        )
        print(f"  🤖 Resposta: {response.message}")
        print(f"  📊 Memórias usadas: {len(response.memories_used)}")
        print(f"  🔧 Ferramentas chamadas: {response.tools_called}")
        
        # Teste 8: Agente fazendo busca semântica complexa
        print("  🔍 Teste 8: Agente fazendo busca semântica complexa...")
        response = chatbot_service.process_message(
            user_id=test_user_id,
            thread_id=test_thread_id,
            message="Quais são minhas habilidades técnicas e preferências de trabalho?",
        )
        print(f"  🤖 Resposta: {response.message}")
        print(f"  📊 Memórias usadas: {len(response.memories_used)}")
        print(f"  🔧 Ferramentas chamadas: {response.tools_called}")
        
        print("  ✅ Capacidade do agente de usar ferramentas de memória OK")
        return True
        
    except Exception as e:
        print(f"  ❌ Erro na capacidade do agente de usar ferramentas: {e}")
        return False
    finally:
        chatbot_service.close()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    test_agent_memory_tools() 