import sys
from loguru import logger

# 1. REMOVA O HANDLER PADRÃO PARA TER CONTROLE TOTAL
logger.remove(0)

# 2. DEFINA O FORMATO PARA OS LOGS PADRÃO (SEM CONTEXTO)
default_format = (
    "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
    "<level>{level: <8}</level> | "
    "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
)

# 3. DEFINA O FORMATO PARA OS LOGS CONTEXTUALIZADOS
#    --- ÚNICA MUDANÇA AQUI ---
context_format = (
    "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
    "<level>{level: <8}</level> | "
    "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
    "<magenta>{extra[task_id]:}</magenta> | "
    # Aumentando o padding para manter o alinhamento
    "<yellow>{extra[turn_type]:}</yellow> | "
    "<level>- {message}</level>"
)

# 4. ADICIONE O HANDLER PARA LOGS CONTEXTUALIZADOS
logger.add(
    sys.stderr,
    level="DEBUG",
    format=context_format,
    filter=lambda record: "task_id" in record["extra"]
    and "turn_type" in record["extra"],
)

# 5. ADICIONE O HANDLER PARA LOGS PADRÃO
logger.add(
    sys.stderr,
    level="DEBUG",
    format=default_format,
    filter=lambda record: "task_id" not in record["extra"],
)
