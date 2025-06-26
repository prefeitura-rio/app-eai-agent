#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste Web Search - IPTU Rio de Janeiro
Testa o web search nativo da OpenAI com uma pergunta específica sobre IPTU no RJ
"""

import asyncio
import sys
import os
import json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.services.llm.openai_service import openai_service


async def teste_iptu_rio():
    """Teste específico sobre IPTU no Rio de Janeiro."""
    print("🏠 Teste Web Search - IPTU Rio de Janeiro")
    print("=" * 50)
    
    try:
        resultado = await openai_service.generate_content(
            text="Como pagar o IPTU na cidade do Rio de Janeiro? Quais são as formas de pagamento e prazos?",
            use_web_search=True,
            model="gpt-4o"
        )
        
        print("✅ Sucesso!")
        print(f"📊 Modelo usado: {resultado['model_used']}")
        print(f"🔍 Web search usado: {resultado['web_search_used']}")
        print(f"🔗 Links encontrados: {len(resultado['links'])}")
        print()
        
        print("📝 RESPOSTA:")
        print("-" * 30)
        print(resultado['resposta'])
        print()
        
        if resultado['links']:
            print("🔗 LINKS COM METADADOS:")
            print("-" * 30)
            for i, link in enumerate(resultado['links'], 1):
                print(f"{i}. {link.get('title', 'Sem título')}")
                print(f"   URL: {link['uri']}")
                if 'start_index' in link and 'end_index' in link:
                    print(f"   Citação: posição {link['start_index']}-{link['end_index']}")
                if 'web_search_id' in link:
                    print(f"   Search ID: {link['web_search_id']}")
                print()
        else:
            print("⚠️ Nenhum link encontrado nos metadados")
            
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()


async def teste_comparativo():
    """Teste comparativo: com e sem web search."""
    print("\n" + "="*50)
    print("🔍 TESTE COMPARATIVO")
    print("="*50)
    
    pergunta = "Qual é o prazo para pagamento do IPTU no Rio de Janeiro em 2025?"
    
    try:
        # Teste SEM web search
        print("\n1️⃣ SEM Web Search:")
        print("-" * 20)
        resultado_sem = await openai_service.generate_content(
            text=pergunta,
            use_web_search=False,
            model="gpt-4o"
        )
        print(f"Resposta: {resultado_sem['resposta'][:200]}...")
        print(f"Links: {len(resultado_sem['links'])}")
        
        # Teste COM web search
        print("\n2️⃣ COM Web Search:")
        print("-" * 20)
        resultado_com = await openai_service.generate_content(
            text=pergunta,
            use_web_search=True,
            model="gpt-4o"
        )
        print(f"Resposta: {resultado_com['resposta'][:200]}...")
        print(f"Links: {len(resultado_com['links'])}")
        
        print("\n📊 DIFERENÇAS:")
        print("-" * 15)
        print(f"• Tamanho da resposta SEM: {len(resultado_sem['resposta'])} chars")
        print(f"• Tamanho da resposta COM: {len(resultado_com['resposta'])} chars")
        print(f"• Links SEM: {len(resultado_sem['links'])}")
        print(f"• Links COM: {len(resultado_com['links'])}")
        
    except Exception as e:
        print(f"❌ Erro no teste comparativo: {e}")


async def main():
    """Executa todos os testes."""
    print("🚀 Iniciando testes de Web Search")
    print("=" * 50)
    
    await teste_iptu_rio()
    # await teste_comparativo()
    
    print("\n✅ Testes concluídos!")


if __name__ == "__main__":
    asyncio.run(main()) 