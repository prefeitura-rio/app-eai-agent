#!/usr/bin/env python3
"""
Chat interativo com o chatbot LangGraph.
Permite conversar com o bot e testar suas funcionalidades.
"""

import logging
import uuid
import sys
from typing import Optional
from src.services.lang_graph.service import LangGraphChatbotService


class InteractiveChat:
    """Chat interativo com o chatbot."""

    def __init__(self):
        self.chatbot_service = LangGraphChatbotService()
        self.user_id = "87eb2bc7-bc2b-4ca2-875c-a70e9a1c6d99"  # str(uuid.uuid4())
        self.thread_id = str(uuid.uuid4())
        self.temperature = 0.7
        self.system_prompt = (
            "Voce é a EAI, um assistente virtual que é solicito e proativo!"
        )

    def initialize_session(
        self, temperature: Optional[float] = None, system_prompt: Optional[str] = None
    ):
        """Inicializa a sessão do chat."""
        if temperature is not None:
            self.temperature = temperature
        if system_prompt is not None:
            self.system_prompt = system_prompt

        session_result = self.chatbot_service.initialize_session(
            user_id=self.user_id,
            thread_id=self.thread_id,
            temperature=self.temperature,
            system_prompt=self.system_prompt,
        )

        if session_result.get("success"):
            print(
                f"✅ Sessão inicializada (User ID: {self.user_id[:8]}..., Thread ID: {self.thread_id[:8]}...)"
            )
            print(f"🌡️ Temperatura: {self.temperature}")
            print(f"📝 System Prompt: {self.system_prompt[:100]}...")
            return True
        else:
            print(
                f"❌ Erro ao inicializar sessão: {session_result.get('error_message')}"
            )
            return False

    async def send_message(self, message: str) -> str:
        """Envia uma mensagem para o chatbot."""
        try:
            response = await self.chatbot_service.process_message(
                user_id=self.user_id,
                thread_id=self.thread_id,
                message=message,
            )
            return response.message
        except Exception as e:
            return f"❌ Erro: {e}"

    def clear_memory(self):
        """Limpa a memória do usuário."""
        try:
            result = self.chatbot_service.clear_memory(self.user_id)
            if result.get("success"):
                print("🧹 Memória limpa com sucesso!")
            else:
                print(f"❌ Erro ao limpar memória: {result.get('error_message')}")
        except Exception as e:
            print(f"❌ Erro: {e}")

    def show_help(self):
        """Mostra a ajuda do chat."""
        print("\n🤖 Chatbot LangGraph - Ajuda")
        print("=" * 40)
        print("Comandos especiais:")
        print("  /help          - Mostra esta ajuda")
        print("  /clear         - Limpa a memória do usuário")
        print("  /temp <valor>  - Define a temperatura (0.0-1.0)")
        print("  /prompt <texto> - Define o system prompt")
        print("  /restart       - Reinicia a sessão")
        print("  /quit          - Sai do chat")
        print("  /info          - Mostra informações da sessão")
        print("\nExemplos:")
        print("  /temp 0.3      - Define temperatura baixa (mais determinístico)")
        print("  /temp 0.9      - Define temperatura alta (mais criativo)")
        print("  /prompt Você é um especialista em Python")
        print("\nDigite sua mensagem normalmente para conversar!")
        print("=" * 40)

    def show_info(self):
        """Mostra informações da sessão."""
        print(f"\n📊 Informações da Sessão:")
        print(f"  User ID: {self.user_id}")
        print(f"  Thread ID: {self.thread_id}")
        print(f"  Temperatura: {self.temperature}")
        print(f"  System Prompt: {self.system_prompt}")

    def restart_session(self):
        """Reinicia a sessão."""
        print("🔄 Reiniciando sessão...")
        self.thread_id = str(uuid.uuid4())
        self.initialize_session()

    async def run(self):
        """Executa o chat interativo."""
        print("🤖 Chatbot LangGraph - Chat Interativo")
        print("=" * 50)

        # Inicializar sessão
        if not self.initialize_session():
            print("❌ Falha ao inicializar sessão. Saindo...")
            return

        self.show_help()

        print(f"\n💬 Digite sua mensagem (ou /help para ajuda):")
        print("-" * 50)

        while True:
            try:
                # Ler mensagem do usuário
                user_input = input("👤 Você: ").strip()

                if not user_input:
                    continue

                # Processar comandos especiais
                if user_input.startswith("/"):
                    self._handle_command(user_input)
                    continue

                # Enviar mensagem para o chatbot
                print("🤖 Bot: ", end="", flush=True)
                response = await self.send_message(user_input)
                print(response)
                print()

            except KeyboardInterrupt:
                print("\n\n👋 Saindo do chat...")
                break
            except EOFError:
                print("\n\n👋 Saindo do chat...")
                break
            except Exception as e:
                print(f"\n❌ Erro: {e}")

        self.chatbot_service.close()

    def _handle_command(self, command: str):
        """Processa comandos especiais."""
        parts = command.split(" ", 1)
        cmd = parts[0].lower()
        arg = parts[1] if len(parts) > 1 else ""

        if cmd == "/help":
            self.show_help()
        elif cmd == "/clear":
            self.clear_memory()
        elif cmd == "/temp":
            try:
                temp = float(arg)
                if 0.0 <= temp <= 1.0:
                    self.temperature = temp
                    self.restart_session()
                    print(f"✅ Temperatura definida para {temp}")
                else:
                    print("❌ Temperatura deve estar entre 0.0 e 1.0")
            except ValueError:
                print("❌ Temperatura inválida. Use um número entre 0.0 e 1.0")
        elif cmd == "/prompt":
            if arg:
                self.system_prompt = arg
                self.restart_session()
                print(f"✅ System prompt definido: {arg}")
            else:
                print("❌ System prompt não pode estar vazio")
        elif cmd == "/restart":
            self.restart_session()
        elif cmd == "/info":
            self.show_info()
        elif cmd == "/quit":
            print("👋 Saindo do chat...")
            sys.exit(0)
        else:
            print(f"❌ Comando desconhecido: {cmd}")
            print("Digite /help para ver os comandos disponíveis")


async def main():
    """Função principal."""
    logging.basicConfig(level=logging.INFO)

    try:
        chat = InteractiveChat()
        await chat.run()
    except Exception as e:
        print(f"❌ Erro fatal: {e}")
        sys.exit(1)


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
