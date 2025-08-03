#!/usr/bin/env python3
"""
Teste principal do serviço LangGraph.
Permite executar testes específicos ou todos os testes.
"""
import logging
import sys
from typing import List, Dict, Callable

# Importar todos os testes
from src.services.lang_graph.tests.test_database import test_database_connection
from src.services.lang_graph.tests.test_memory_operations import test_memory_operations
from src.services.lang_graph.tests.test_chatbot_conversation import (
    test_chatbot_conversation,
)
from src.services.lang_graph.tests.test_session_management import (
    test_session_management,
)
from src.services.lang_graph.tests.test_error_handling import test_error_handling
from src.services.lang_graph.tests.test_agent_tools import test_agent_memory_tools
from src.services.lang_graph.tests.test_memory_persistence import (
    test_memory_persistence_conversation,
)
from src.services.lang_graph.tests.test_context_tools import test_context_tools
from src.services.lang_graph.tests.test_isolation import test_memory_isolation
from src.services.lang_graph.tests.test_configuration import (
    test_configuration_parameters,
)

logger = logging.getLogger(__name__)

# Mapeamento de testes disponíveis
AVAILABLE_TESTS = {
    "database": test_database_connection,
    "memory": test_memory_operations,
    "conversation": test_chatbot_conversation,
    "session": test_session_management,
    "errors": test_error_handling,
    "tools": test_agent_memory_tools,
    "persistence": test_memory_persistence_conversation,
    "context": test_context_tools,
    "isolation": test_memory_isolation,
    "config": test_configuration_parameters,
}

# Testes por categoria
TEST_CATEGORIES = {
    "core": ["database", "memory", "conversation", "session"],
    "features": ["tools", "persistence", "context", "isolation"],
    "all": list(AVAILABLE_TESTS.keys()),
}


def print_available_tests():
    """Imprime os testes disponíveis."""
    print("🚀 Testes disponíveis:")
    print("=======================")

    print("\n📋 Testes individuais:")
    for test_name in AVAILABLE_TESTS.keys():
        print(f"  • {test_name}")

    print("\n📂 Categorias:")
    for category, tests in TEST_CATEGORIES.items():
        if category != "all":
            print(f"  • {category}: {', '.join(tests)}")

    print("\n💡 Uso:")
    print("  • Teste específico: python test_service.py database")
    print("  • Categoria: python test_service.py core")
    print("  • Todos: python test_service.py all")
    print("  • Listar: python test_service.py --list")


def run_specific_test(test_name: str) -> bool:
    """Executa um teste específico."""
    if test_name not in AVAILABLE_TESTS:
        print(f"❌ Teste '{test_name}' não encontrado!")
        print_available_tests()
        return False

    print(f"🎯 Executando teste: {test_name}")
    print("=" * 50)

    try:
        result = AVAILABLE_TESTS[test_name]()
        if result:
            print(f"✅ Teste '{test_name}' PASS")
        else:
            print(f"❌ Teste '{test_name}' FAIL")
        return result
    except Exception as e:
        print(f"❌ Erro no teste '{test_name}': {e}")
        return False


def run_category_tests(category: str) -> Dict[str, bool]:
    """Executa todos os testes de uma categoria."""
    if category not in TEST_CATEGORIES:
        print(f"❌ Categoria '{category}' não encontrada!")
        print_available_tests()
        return {}

    test_names = TEST_CATEGORIES[category]
    results = {}

    print(f"📂 Executando categoria: {category}")
    print("=" * 50)

    for test_name in test_names:
        results[test_name] = run_specific_test(test_name)
        print()  # Linha em branco entre testes

    return results


def run_all_tests() -> Dict[str, bool]:
    """Executa todos os testes."""
    print("🚀 Iniciando testes do chatbot com memória de longo prazo...")
    print("=" * 60)

    results = {}

    for test_name in AVAILABLE_TESTS.keys():
        results[test_name] = run_specific_test(test_name)
        print()  # Linha em branco entre testes

    return results


def print_results(results: Dict[str, bool]):
    """Imprime os resultados dos testes."""
    print("📊 Resultado dos Testes:")
    print("=" * 60)

    passed = sum(1 for result in results.values() if result)
    total = len(results)

    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name}: {status}")

    print(f"\n📈 Resumo: {passed}/{total} PASS")

    if passed == total:
        print("🎉 Todos os testes passaram! O chatbot está funcionando corretamente.")
        print("\n🎯 Implementação concluída com sucesso!")
        print("📝 Próximos passos:")
        print("   1. Integrar com a API principal")
        print("   2. Implementar busca semântica real")
        print("   3. Adicionar mais testes de integração")
        print("   4. Otimizar performance")
    else:
        print(f"⚠️ {total - passed} teste(s) falharam. Verifique os erros acima.")


def main():
    """Função principal."""
    logging.basicConfig(level=logging.INFO)

    if len(sys.argv) < 2:
        print("❌ Uso: python test_service.py <test_name|category>")
        print_available_tests()
        return

    test_arg = sys.argv[1].lower()

    if test_arg == "--list" or test_arg == "-l":
        print_available_tests()
        return

    if test_arg == "all":
        results = run_all_tests()
        print_results(results)
    elif test_arg in TEST_CATEGORIES:
        results = run_category_tests(test_arg)
        print_results(results)
    elif test_arg in AVAILABLE_TESTS:
        result = run_specific_test(test_arg)
        print(f"\n📊 Resultado: {'✅ PASS' if result else '❌ FAIL'}")
    else:
        print(f"❌ Argumento '{test_arg}' não reconhecido!")
        print_available_tests()


if __name__ == "__main__":
    main()
