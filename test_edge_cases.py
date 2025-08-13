#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.utils.letta_format_messages import to_letta
from datetime import datetime, timezone

# Edge case: Mensagem no final de uma janela e resposta na próxima janela
edge_case_messages = [
    # Mensagem 1: 16:59:30 (quase fim da janela 16:00-17:00)
    [{
        "kwargs": {
            "type": "human",
            "id": "msg1",
            "content": "Pergunta no final da janela",
            "additional_kwargs": {
                "timestamp": "2025-08-13T16:59:30.000000+00:00"
            }
        }
    }],
    # Mensagem 2: 17:00:15 (início da próxima janela, mas resposta rápida)
    [{
        "kwargs": {
            "type": "ai",
            "id": "msg2",
            "content": "Resposta na próxima janela",
            "additional_kwargs": {
                "timestamp": "2025-08-13T17:00:15.000000+00:00"
            },
            "response_metadata": {
                "model_name": "gemini-2.5-flash",
                "finish_reason": "STOP",
                "usage_metadata": {
                    "prompt_token_count": 100,
                    "candidates_token_count": 50,
                    "total_token_count": 150
                }
            }
        }
    }],
    # Mensagem 3: 17:01:00 (continuação da conversa)
    [{
        "kwargs": {
            "type": "human",
            "id": "msg3",
            "content": "Continuação da conversa",
            "additional_kwargs": {
                "timestamp": "2025-08-13T17:01:00.000000+00:00"
            }
        }
    }],
    # Mensagem 4: 18:05:00 (muito depois - nova sessão)
    [{
        "kwargs": {
            "type": "human",
            "id": "msg4",
            "content": "Mensagem muito depois",
            "additional_kwargs": {
                "timestamp": "2025-08-13T18:05:00.000000+00:00"
            }
        }
    }]
]

print("=== Teste Edge Case: Transição de Janela ===")
print("Timeout: 1 hora (3600s)")
print("Janelas: 16:00-17:00, 17:00-18:00, 18:00-19:00\n")

for i, msg_list in enumerate(edge_case_messages):
    result = to_letta(msg_list, "test_thread_id", session_timeout_seconds=3600)
    for msg in result["data"]["messages"]:
        if msg.get("message_type") != "usage_statistics":
            print(f"Msg {i+1} ({msg.get('date')})")
            print(f"  Conteúdo: {msg.get('content')}")
            print(f"  Session ID: {msg.get('session_id')}")
            print()

print("=== Análise ===")
print("✅ Msg 1 (16:59:30): Janela 16:00-17:00")
print("✅ Msg 2 (17:00:15): Deveria estar na MESMA sessão (resposta rápida)")
print("✅ Msg 3 (17:01:00): Deveria estar na MESMA sessão (continuação)")
print("❌ Msg 4 (18:05:00): Nova sessão (tempo > timeout)")

print("\n=== Teste com Timeout Menor (30 min) ===")

for i, msg_list in enumerate(edge_case_messages):
    result = to_letta(msg_list, "test_thread_id", session_timeout_seconds=1800)  # 30 min
    for msg in result["data"]["messages"]:
        if msg.get("message_type") != "usage_statistics":
            print(f"Msg {i+1}: {msg.get('session_id')} - {msg.get('date')}")

print("\n=== Teste Extreme Edge Case ===")
extreme_case = [
    # Mensagem exatamente no limite da janela
    [{
        "kwargs": {
            "type": "human",
            "id": "extreme1",
            "content": "Mensagem exata no limite",
            "additional_kwargs": {
                "timestamp": "2025-08-13T16:59:59.999999+00:00"
            }
        }
    }],
    # Resposta 1 segundo depois
    [{
        "kwargs": {
            "type": "ai",
            "id": "extreme2",
            "content": "Resposta 1 segundo depois",
            "additional_kwargs": {
                "timestamp": "2025-08-13T17:00:00.000001+00:00"
            },
            "response_metadata": {
                "model_name": "gemini-2.5-flash",
                "finish_reason": "STOP",
                "usage_metadata": {}
            }
        }
    }]
]

print("Extreme case (diferença de 1 segundo):")
for i, msg_list in enumerate(extreme_case):
    result = to_letta(msg_list, "test_thread_id", session_timeout_seconds=3600)
    for msg in result["data"]["messages"]:
        if msg.get("message_type") != "usage_statistics":
            print(f"Extreme {i+1}: {msg.get('session_id')} - {msg.get('date')}")