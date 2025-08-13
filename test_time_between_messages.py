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

print("=== Teste: Tempo entre mensagens com Session ID ===")
result = to_letta(test_messages, "test_thread_id", session_timeout_seconds=3600)

for i, msg in enumerate(result["data"]["messages"]):
    if msg.get("message_type") != "usage_statistics":
        time_diff = msg.get("time_since_last_message")
        content = msg.get("content", "")[:40]
        session_id = msg.get("session_id")
        
        print(f"Msg {i+1}: {msg.get('message_type')}")
        print(f"  Conteúdo: {content}...")
        print(f"  Tempo desde última: {time_diff} seg")
        print(f"  Session ID: {session_id}")
        print("---")

print("\n=== Análise das sessões ===")
print("Com timeout de 3600s (1 hora):")
print("- Msgs 1-4: Mesma sessão (intervalos < 1h)")
print("- Msg 5: Nova sessão (2h > 1h)")

print("\n=== Teste: Timeout menor (30 min) ===")
result_30min = to_letta(test_messages, "test_thread_id", session_timeout_seconds=1800)

sessions = {}
for i, msg in enumerate(result_30min["data"]["messages"]):
    if msg.get("message_type") != "usage_statistics":
        session_id = msg.get("session_id")
        time_diff = msg.get("time_since_last_message")
        if session_id not in sessions:
            sessions[session_id] = []
        sessions[session_id].append(f"Msg{i+1}({time_diff}s)")

print(f"Sessões encontradas: {len(sessions)}")
for session_id, msgs in sessions.items():
    print(f"  {session_id}: {msgs}")