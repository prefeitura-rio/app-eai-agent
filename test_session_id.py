#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.utils.letta_format_messages import to_letta
from datetime import datetime, timezone

# Teste: mensagens individuais (simulando chamadas da API)
single_messages = [
    # Mensagem 1 - 16:21:16 (janela 1)
    [{
        "kwargs": {
            "type": "human",
            "id": "msg1",
            "content": "Primeira mensagem",
            "additional_kwargs": {
                "timestamp": "2025-08-13T16:21:16.518978+00:00"
            }
        }
    }],
    # Mensagem 2 - 16:21:18 (mesma janela 1) 
    [{
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
    }],
    # Mensagem 3 - 16:29:11 (mesma janela 1)
    [{
        "kwargs": {
            "type": "human",
            "id": "msg3",
            "content": "Segunda mensagem (depois de 7 minutos)",
            "additional_kwargs": {
                "timestamp": "2025-08-13T16:29:11.239391+00:00"
            }
        }
    }],
    # Mensagem 4 - 18:30:11 (janela 2 - 2 horas depois)
    [{
        "kwargs": {
            "type": "human",
            "id": "msg4",
            "content": "Terceira mensagem (depois de 2 horas)",
            "additional_kwargs": {
                "timestamp": "2025-08-13T18:30:11.239391+00:00"
            }
        }
    }]
]

# Todas as mensagens juntas (para comparar)
all_messages = []
for msg_list in single_messages:
    all_messages.extend(msg_list)

print("=== Teste: Mensagens individuais (simulando API) ===")
print("Processando cada mensagem separadamente (como na API):\n")

for i, msg_list in enumerate(single_messages):
    result = to_letta(msg_list, "test_thread_id", session_timeout_seconds=3600)
    for msg in result["data"]["messages"]:
        if msg.get("message_type") != "usage_statistics":
            print(f"Mensagem {i+1}: {msg.get('content')[:40]}...")
            print(f"Session ID: {msg.get('session_id')}")
            print(f"Timestamp: {msg.get('date')}")
            print("---")

print("\n=== Teste: Todas as mensagens juntas ===")
result_all = to_letta(all_messages, "test_thread_id", session_timeout_seconds=3600)

for i, msg in enumerate(result_all["data"]["messages"]):
    if msg.get("message_type") != "usage_statistics":
        print(f"Mensagem {i+1}: {msg.get('content')[:40]}...")
        print(f"Session ID: {msg.get('session_id')}")
        print(f"Timestamp: {msg.get('date')}")
        print("---")

print("\n=== Teste: Determinismo ===")
print("Executando as mesmas mensagens individuais novamente:")

for i, msg_list in enumerate(single_messages):
    result1 = to_letta(msg_list, "test_thread_id", session_timeout_seconds=3600)
    result2 = to_letta(msg_list, "test_thread_id", session_timeout_seconds=3600)
    
    for msg1, msg2 in zip(result1["data"]["messages"], result2["data"]["messages"]):
        if msg1.get("message_type") != "usage_statistics":
            id1 = msg1.get('session_id')
            id2 = msg2.get('session_id')
            match = "✅ IGUAL" if id1 == id2 else "❌ DIFERENTE"
            print(f"Msg {i+1}: {id1} vs {id2} - {match}")
            break

print("\n=== Teste: Timeout de 30 minutos ===")
print("Com timeout menor, mais janelas:")

for i, msg_list in enumerate(single_messages):
    result = to_letta(msg_list, "test_thread_id", session_timeout_seconds=1800)  # 30 min
    for msg in result["data"]["messages"]:
        if msg.get("message_type") != "usage_statistics":
            print(f"Msg {i+1}: {msg.get('session_id')} - {msg.get('date')}")
            break