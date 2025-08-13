#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.utils.letta_format_messages import to_letta

# Mensagens de teste
test_messages = [
    {
        "kwargs": {
            "type": "human",
            "id": "msg1",
            "content": "Primeira mensagem",
            "additional_kwargs": {
                "timestamp": "2025-08-13T16:21:16.518978+00:00"
            }
        }
    },
    {
        "kwargs": {
            "type": "ai",
            "id": "msg2",
            "content": "Resposta 1",
            "additional_kwargs": {
                "timestamp": "2025-08-13T16:21:18.766862+00:00"
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
    },
    {
        "kwargs": {
            "type": "human",
            "id": "msg3",
            "content": "Segunda mensagem (depois de 7 minutos)",
            "additional_kwargs": {
                "timestamp": "2025-08-13T16:29:11.239391+00:00"
            }
        }
    },
    {
        "kwargs": {
            "type": "human",
            "id": "msg4",
            "content": "Terceira mensagem (depois de 2 horas)",
            "additional_kwargs": {
                "timestamp": "2025-08-13T18:30:11.239391+00:00"
            }
        }
    }
]

print("=== Teste 1: Com timeout (histórico completo) ===")
result_with_timeout = to_letta(test_messages, "test_thread_id", session_timeout_seconds=3600)

for i, msg in enumerate(result_with_timeout["data"]["messages"]):
    if msg.get("message_type") != "usage_statistics":
        print(f"Msg {i+1}: session_id={msg.get('session_id')} - {msg.get('content')[:40]}...")

print("\n=== Teste 2: Sem timeout (API - session_timeout_seconds=None) ===")
result_without_timeout = to_letta(test_messages, "test_thread_id", session_timeout_seconds=None)

for i, msg in enumerate(result_without_timeout["data"]["messages"]):
    if msg.get("message_type") != "usage_statistics":
        print(f"Msg {i+1}: session_id={msg.get('session_id')} - {msg.get('content')[:40]}...")

print("\n=== Teste 3: Determinismo (executando novamente com timeout) ===")
result_deterministic = to_letta(test_messages, "test_thread_id", session_timeout_seconds=3600)

print("Comparando session_ids:")
for i, (msg1, msg2) in enumerate(zip(result_with_timeout["data"]["messages"], result_deterministic["data"]["messages"])):
    if msg1.get("message_type") != "usage_statistics":
        id1 = msg1.get('session_id')
        id2 = msg2.get('session_id')
        match = "✅ IGUAL" if id1 == id2 else "❌ DIFERENTE"
        print(f"Msg {i+1}: {id1} vs {id2} - {match}")

print("\n=== Teste 4: Thread ID diferente ===")
result_diff_thread = to_letta(test_messages, "different_thread_id", session_timeout_seconds=3600)

print("Comparando session_ids com thread_id diferente:")
for i, (msg1, msg2) in enumerate(zip(result_with_timeout["data"]["messages"], result_diff_thread["data"]["messages"])):
    if msg1.get("message_type") != "usage_statistics":
        id1 = msg1.get('session_id')
        id2 = msg2.get('session_id')
        match = "✅ IGUAL" if id1 == id2 else "❌ DIFERENTE (esperado)"
        print(f"Msg {i+1}: {id1} vs {id2} - {match}")

print("\n=== Teste 5: Mensagens individuais (simulando API) ===")
print("Processando cada mensagem separadamente com session_timeout_seconds=None:")

for i, msg in enumerate([test_messages[0], test_messages[1], test_messages[2], test_messages[3]]):
    result = to_letta([msg], "test_thread_id", session_timeout_seconds=None)
    for msg_result in result["data"]["messages"]:
        if msg_result.get("message_type") != "usage_statistics":
            print(f"Msg {i+1}: session_id={msg_result.get('session_id')} - {msg_result.get('content')[:40]}...")
            break