# Configuração do Gunicorn para operações longas
bind = "0.0.0.0:80"
workers = 1
threads = 4
worker_class = "uvicorn.workers.UvicornWorker"
worker_connections = 1000

# Timeouts críticos para resolver o problema
timeout = 120  # Timeout do worker em segundos (era 30 por padrão)
keepalive = 5  # Keep-alive connections
graceful_timeout = 30  # Tempo para shutdown graceful

# Logging
access_log = "-"
error_log = "-"
log_level = "info"

# Para debug em desenvolvimento
reload = False
preload_app = True 