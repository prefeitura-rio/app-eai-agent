"""
Testes de conexão com banco de dados.
"""

from src.services.lang_graph.database import db_manager

from src.utils.log import logger


async def test_database_connection():
    """Testa a conexão com o banco de dados."""
    logger.info("📋 Executando: Conexão com Banco de Dados")
    logger.info("----------------------------------------")

    try:
        logger.info("🔍 Testando conexão com banco de dados...")

        # Testar inicialização do engine
        db_manager.initialize_engine()
        logger.info("✅ Engine SQLAlchemy inicializado")

        # Testar criação de tabelas
        db_manager.create_tables()
        logger.info("✅ Tabelas criadas/verificadas")

        # Testar sessão
        session = db_manager.get_session()
        if session:
            session.close()
            logger.info("✅ Sessão criada e fechada com sucesso")

        logger.info("✅ Conexão com banco de dados OK")
        return True

    except Exception as e:
        logger.info(f"❌ Erro na conexão com banco de dados: {e}")
        return False
    finally:
        db_manager.close()


if __name__ == "__main__":
    import asyncio

    logging.basicConfig(level=logging.INFO)
    asyncio.run(test_database_connection())
