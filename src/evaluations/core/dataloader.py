import pandas as pd
import re
from typing import Generator, Dict, Any, Union, List, Optional
from urllib.parse import urlparse, parse_qs


class DataLoader:
    """
    Carrega dados de diversas fontes (DataFrame, CSV, Google Sheets)
    e os prepara como tarefas para avaliação.
    """

    def __init__(
        self,
        source: Union[str, pd.DataFrame],
        id_col: str,
        metadata_cols: Optional[List[str]] = None,
    ):
        """
        Inicializa o DataLoader.

        Args:
            source (Union[str, pd.DataFrame]): A fonte dos dados. Pode ser:
                - um caminho para um arquivo CSV.
                - uma URL para uma planilha pública do Google Sheets.
                - um pandas.DataFrame já carregado.
            id_col (str): O nome da coluna que contém um identificador único para a linha.
            metadata_cols (List[str], optional): Uma lista de nomes de colunas a serem
                                                 incluídas como metadados em cada tarefa.
                                                 Defaults to None.
        """
        self.id_col = id_col
        self.metadata_cols = metadata_cols if metadata_cols else []

        if isinstance(source, pd.DataFrame):
            self.df = source
        elif isinstance(source, str):
            if "docs.google.com/spreadsheets" in source:
                self.df = self._load_from_gsheet(source)
            else:
                self.df = self._load_from_file(source)
        else:
            raise TypeError(
                "A fonte deve ser um caminho de arquivo, URL do Google Sheets ou um pandas.DataFrame."
            )

        self._validate_columns()

    def _load_from_file(self, file_path: str) -> pd.DataFrame:
        try:
            return pd.read_csv(file_path)
        except FileNotFoundError:
            raise FileNotFoundError(f"Arquivo não encontrado em: {file_path}")
        except Exception as e:
            raise Exception(f"Erro ao ler o arquivo CSV: {e}")

    def _load_from_gsheet(self, url: str) -> pd.DataFrame:
        try:
            match = re.search(r"/spreadsheets/d/([a-zA-Z0-9-_]+)", url)
            if not match:
                raise ValueError("URL do Google Sheets inválida ou mal formatada.")
            sheet_id = match.group(1)

            parsed_url = urlparse(url)
            query_params = parse_qs(parsed_url.query)
            fragment_params = parse_qs(parsed_url.fragment)
            gid = (
                query_params.get("gid", [None])[0] or fragment_params.get("gid", [0])[0]
            )

            csv_export_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={gid}"
            return pd.read_csv(csv_export_url)
        except Exception as e:
            raise Exception(f"Erro ao carregar dados do Google Sheets: {e}")

    def _validate_columns(self):
        """Verifica se as colunas mapeadas existem no DataFrame."""
        required_cols = {self.id_col, *self.metadata_cols}
        missing_cols = required_cols - set(self.df.columns)
        if missing_cols:
            raise ValueError(
                f"Colunas necessárias não encontradas na fonte de dados: {', '.join(missing_cols)}"
            )

    def get_tasks(self) -> Generator[Dict[str, Any], None, None]:
        """
        Retorna um gerador que produz cada linha como uma tarefa padronizada.

        Yields:
            Generator[Dict[str, Any], None, None]: Um gerador de tarefas.
        """
        for _, row in self.df.iterrows():
            task = {"id": row[self.id_col]}
            for col in self.metadata_cols:
                task[col] = row[col]
            yield task


if __name__ == "__main__":
    # Exemplo de como usar o DataLoader refatorado

    print("\n--- Teste: Carregando do Google Sheets com a nova estrutura ---")
    gsheet_url = "https://docs.google.com/spreadsheets/d/1VPnJSf9puDgZ-Ed9MRkpe3Jy38nKxGLp7O9-ydAdm98/edit?gid=370781785"
    try:
        loader = DataLoader(
            source=gsheet_url,
            id_col="id",
            metadata_cols=[
                "mensagem_whatsapp_simulada",
                "golden_answer",
                "golden_links_list",
            ],
        )
        print("Tarefas carregadas do Google Sheets com sucesso!")

        tasks_generator = loader.get_tasks()
        # Imprime as 3 primeiras tarefas para verificação
        for i, task in enumerate(tasks_generator):
            if i >= 3:
                break
            import json

            print(json.dumps(task, ensure_ascii=False, indent=2))

    except Exception as e:
        print(f"Não foi possível carregar a planilha de exemplo: {e}")
