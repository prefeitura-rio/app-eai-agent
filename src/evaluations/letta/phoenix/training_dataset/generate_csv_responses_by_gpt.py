import pandas as pd
import re
from urllib.parse import urlparse, urlunparse

def limpar_url(url: str) -> str:
    try:
        parsed = urlparse(url)
        if parsed.scheme not in {"http", "https"} or '.' not in parsed.netloc:
            raise ValueError("URL inválida")
        return urlunparse(parsed._replace(query=""))
    except Exception:
        return url

def processar_resposta(resposta):
    if not isinstance(resposta, str):
        return "", []

    # 1. Extrair referências tipo: [1]: https://...
    referencias = dict(re.findall(r"\[(\d+)\]:\s*(\S+)", resposta))

    # 2. Substituir ([site.com][1]) por URL limpa
    def substituir_referencia(match):
        _, ref = match.groups()
        url = referencias.get(ref, "")
        return limpar_url(url) if url else match.group(0)

    # 3. Separar corpo do texto (antes das referências)
    corpo = re.split(r"\n\[\d+\]:", resposta)[0]  # pega tudo antes de rodapés

    # 4. Substituir marcadores ([site][1]) por URLs limpas
    corpo = re.sub(r"\(\[([^\]]+)\]\[(\d+)\]\)", substituir_referencia, corpo)

    # 5. Substituir URLs com utm_* por URLs limpas
    def limpar_urls_embutidas(match):
        return limpar_url(match.group(0))

    corpo = re.sub(r"https?://[^\s\]\)\"\'<>]+", limpar_urls_embutidas, corpo)

    # 6. Coletar todas as URLs finais limpas
    urls_texto = set(re.findall(r"https?://[^\s)]+", corpo))
    urls_referencias = {limpar_url(u) for u in referencias.values()}
    todas = sorted(urls_texto.union(urls_referencias))

    return corpo.strip(), list(todas)

def processar_dataframe(df):
    df['resposta_gpt'] = df['resposta_gpt'].fillna("")
    resultados = df['resposta_gpt'].apply(processar_resposta)
    df['resposta_gpt_formatada'], df['fontes'] = zip(*resultados)
    return df[['pergunta', 'resposta_gpt_formatada', 'fontes']].rename(
        columns={"resposta_gpt_formatada": "resposta_gpt"}
    )

df = pd.read_csv("Golden Dataset - Eai Agent - ChatGPT Browser.csv")
df_formatado = processar_dataframe(df)
df_formatado.to_csv("respostas_formatadas.csv", index=False)