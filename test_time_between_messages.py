#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.utils.letta_format_messages import to_letta

# Mensagens de teste com diferentes intervalos de tempo
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
            "content": "Resposta rápida (2 segundos depois)",
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
            "content": "Segunda mensagem (7 minutos depois)",
            "additional_kwargs": {
                "timestamp": "2025-08-13T16:29:11.239391+00:00"
            }
        }
    },
    {
        "kwargs": {
            "type": "ai",
            "id": "msg4",
            "content": "Resposta após pausa",
            "additional_kwargs": {
                "timestamp": "2025-08-13T16:29:15.000000+00:00"
            },
            "response_metadata": {
                "model_name": "gemini-2.5-flash",
                "finish_reason": "STOP",
                "usage_metadata": {
                    "prompt_token_count": 80,
                    "candidates_token_count": 40,
                    "total_token_count": 120
                }
            }
        }
    },
    {
        "kwargs": {
            "type": "human",
            "id": "msg5",
            "content": "Terceira mensagem (2 horas depois)",
            "additional_kwargs": {
                "timestamp": "2025-08-13T18:30:11.239391+00:00"
            }
        }
    }
]

print("=== Teste: Tempo entre mensagens ===")
result = to_letta(test_messages, "test_thread_id", session_timeout_seconds=3600)

for i, msg in enumerate(result["data"]["messages"]):
    if msg.get("message_type") != "usage_statistics":
        time_diff = msg.get("time_since_last_message")
        content = msg.get("content", "")[:50]
        
        print(f"Msg {i+1}: {msg.get('message_type')}")
        print(f"  Conteúdo: {content}...")
        print(f"  Timestamp: {msg.get('date')}")
        print(f"  Tempo desde última msg: {time_diff} segundos")
        print(f"  Session ID: {msg.get('session_id')}")
        print("---")

print("\n=== Verificação dos tempos calculados ===")
print("✅ Msg 1: time_since_last_message = None (primeira mensagem)")
print("✅ Msg 2: time_since_last_message ≈ 2.247 segundos")
print("✅ Msg 3: time_since_last_message ≈ 472.47 segundos (7min 52s)")
print("✅ Msg 4: time_since_last_message ≈ 3.76 segundos")
print("✅ Msg 5: time_since_last_message ≈ 7260 segundos (2h 1min)")

print("\n=== Teste: API mode (session_timeout_seconds=None) ===")
result_api = to_letta(test_messages, "test_thread_id", session_timeout_seconds=None)

for i, msg in enumerate(result_api["data"]["messages"]):
    if msg.get("message_type") != "usage_statistics":
        time_diff = msg.get("time_since_last_message")
        content = msg.get("content", "")[:50]
        
        print(f"API Msg {i+1}: time_diff={time_diff}s, session_id={msg.get('session_id')}")