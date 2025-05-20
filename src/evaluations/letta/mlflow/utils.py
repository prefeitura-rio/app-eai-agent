import pandas as pd


def explode_dataframe(dataframe: pd.DataFrame, explode_col: str) -> pd.DataFrame:
    s = dataframe[explode_col].explode()
    tmp = dataframe.drop(columns=explode_col)
    out = (
        pd.concat(
            [
                tmp,
                pd.json_normalize(s, sep="_")
                .set_axis(s.index)
                .dropna()
                .combine_first(tmp),
            ]
        )
        .drop_duplicates()
        .sort_index(kind="stable")
    )
    return out[out["judge"].notnull()]


def load_dataframe(final_results: list) -> pd.DataFrame:
    dataframe = pd.DataFrame(final_results)
    dataframe = explode_dataframe(dataframe=dataframe, explode_col="judges")
