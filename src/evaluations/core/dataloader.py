import pandas as pd
import re
from typing import Generator, Dict, Any, Union, List, Optional
from urllib.parse import urlparse, parse_qs
import uuid
import hashlib
from datetime import datetime, timezone


class DataLoader:
    """
    Carrega dados de diversas fontes, gerencia metadados do dataset
    e os prepara como tarefas para avaliação.
    """

    def __init__(
        self,
        source: Union[str, pd.DataFrame],
        id_col: str,
        prompt_col: str,
        dataset_name: str,
        dataset_description: str,
        metadata_cols: Optional[List[str]] = None,
    ):
        """
        Inicializa o DataLoader.

        Args:
            source (Union[str, pd.DataFrame]): A fonte dos dados.
            id_col (str): Nome da coluna de ID único.
            prompt_col (str): Nome da coluna de prompt.
            dataset_name (str): Nome do dataset.
            dataset_description (str): Descrição do dataset.
            metadata_cols (List[str], optional): Colunas de metadados adicionais.
        """
        self.id_col = id_col
        self.prompt_col = prompt_col
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
        self._dataset_config = self._create_dataset_config(
            dataset_name, dataset_description
        )

    def _create_dataset_config(self, name: str, description: str) -> Dict[str, Any]:
        """Cria a configuração e um ID determinístico para o dataset."""
        # Converte o dataframe para uma string JSON estável para o hash
        df_json = self.df.to_json(orient="records", lines=True)
        df_hash = hashlib.sha256(df_json.encode()).hexdigest()

        seed = f"{name}-{df_hash}"
        dataset_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, seed))

        return {
            "dataset_name": name,
            "dataset_description": description,
            "dataset_id": dataset_id,
            "dataset_created_at": datetime.now(timezone.utc).isoformat(),
        }

    def get_dataset_config(self) -> Dict[str, Any]:
        """Retorna os metadados do dataset."""
        return self._dataset_config

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
        required_cols = {self.id_col, self.prompt_col, *self.metadata_cols}
        missing_cols = required_cols - set(self.df.columns)
        if missing_cols:
            raise ValueError(
                f"Colunas necessárias não encontradas na fonte de dados: {', '.join(missing_cols)}"
            )

    def get_tasks(self) -> Generator[Dict[str, Any], None, None]:
        """
        Retorna um gerador que produz cada linha como uma tarefa padronizada.
        A coluna especificada em `prompt_col` é mapeada para a chave 'prompt'.
        """
        for _, row in self.df.iterrows():
            task = {
                "id": row[self.id_col],
                "prompt": row[self.prompt_col],
            }
            for col in self.metadata_cols:
                if col != self.prompt_col:  # Evita duplicar o prompt
                    task[col] = row[col]
            yield task
