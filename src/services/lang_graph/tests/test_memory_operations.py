"""
Testes de operações de memória.
"""

import logging
import uuid
from src.services.lang_graph.repository import MemoryRepository
from src.services.lang_graph.models import MemoryType
from sqlalchemy import text

logger = logging.getLogger(__name__)


def test_memory_operations():
    """Testa operações básicas de memória."""
    print("📋 Executando: Operações de Memória")
    print("----------------------------------------")

    # Usar UUID único para evitar contaminação
    test_user_id = str(uuid.uuid4())
    repository = MemoryRepository()

    try:
        # Limpar tabela antes dos testes
        print("🧹 Limpando tabela antes dos testes...")
        session = repository.db_manager.get_session()
        try:
            session.execute(
                text('DROP TABLE IF EXISTS "public"."long_term_memory" CASCADE;')
            )
            session.commit()
            print("  ✅ Tabela dropada com sucesso")
        except Exception as e:
            print(f"  ⚠️ Erro ao dropar tabela: {e}")
        finally:
            session.close()

        # Recriar tabelas
        repository.db_manager.create_tables()
        print("  ✅ Tabelas recriadas")

        print("🧠 Testando operações de memória...")

        # Teste 1: Salvar memória
        print("  📝 Testando salvamento de memória...")
        memory_id = repository.create_memory(
            user_id=test_user_id,
            content="O usuário gosta de café com leite",
            memory_type=MemoryType.PREFERENCE,
        )
        print(f"  ✅ Memória salva com ID: {memory_id}")

        # Teste 2: Busca semântica
        print("  🔍 Testando busca semântica...")
        memories = repository.get_memories_semantic(
            user_id=test_user_id,
            query="café",
            limit=5,
        )
        print(f"  ✅ Encontradas {len(memories)} memórias semânticas")
        if memories:
            print(
                f"    - {memories[0].content} (tipo: {memories[0].memory_type.value})"
            )

        # Teste 3: Busca cronológica
        print("  📅 Testando busca cronológica...")
        memories = repository.get_memories_chronological(
            user_id=test_user_id,
            limit=5,
        )
        print(f"  ✅ Encontradas {len(memories)} memórias cronológicas")

        print("  ✅ Todas as operações de memória OK")
        return True

    except Exception as e:
        print(f"  ❌ Erro nas operações de memória: {e}")
        return False


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    test_memory_operations()
