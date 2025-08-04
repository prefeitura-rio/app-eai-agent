"""
Testes de conexão com banco de dados.
"""

import logging
from src.services.lang_graph.database import db_manager

logger = logging.getLogger(__name__)


async def test_database_connection():
    """Testa a conexão com o banco de dados."""
    print("📋 Executando: Conexão com Banco de Dados")
    print("----------------------------------------")

    try:
        print("🔍 Testando conexão com banco de dados...")

        # Testar inicialização do engine
        db_manager.initialize_engine()
        print("✅ Engine SQLAlchemy inicializado")

        # Testar criação de tabelas
        db_manager.create_tables()
        print("✅ Tabelas criadas/verificadas")

        # Testar sessão
        session = db_manager.get_session()
        if session:
            session.close()
            print("✅ Sessão criada e fechada com sucesso")

        print("✅ Conexão com banco de dados OK")
        return True

    except Exception as e:
        print(f"❌ Erro na conexão com banco de dados: {e}")
        return False
    finally:
        db_manager.close()


if __name__ == "__main__":
    import asyncio

    logging.basicConfig(level=logging.INFO)
    asyncio.run(test_database_connection())
