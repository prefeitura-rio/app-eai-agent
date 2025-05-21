import pandas as pd
import mlflow

mlflow.gemini.autolog()


def get_metrics(eval_results: dict) -> tuple[pd.DataFrame, dict]:
    all_records = []
    for eval_result in eval_results:
        query = eval_result["query"]
        response = eval_result["letta_response"]
        letta_stats = eval_result["letta_usage_statistics"][0]

        for judge_result in eval_result["judges"]:
            record = {
                "query": query,
                "response": response,
                "judge": judge_result["judge"],
                "label": judge_result["response"].get("label"),
                "value": judge_result["response"].get("value"),
                "completion_tokens": letta_stats["completion_tokens"],
                "prompt_tokens": letta_stats["prompt_tokens"],
                "total_tokens": letta_stats["total_tokens"],
                "step_count": letta_stats["step_count"],
            }
            all_records.append(record)

    df_long = pd.DataFrame.from_records(all_records)
    df_long["label"] = df_long["label"].fillna("None")
    final_df = df_long.pivot_table(
        index=[
            "query",
            "response",
            "completion_tokens",
            "prompt_tokens",
            "total_tokens",
            "step_count",
        ],
        columns="judge",
        values=["label", "value"],
        aggfunc="first",
    )

    final_df = final_df.reset_index()

    final_df.columns = [f"{col[1]}_{col[0]}" for col in final_df.columns]
    final_df = final_df.reset_index()
    final_df.columns = [col.lstrip("_") for col in final_df.columns]
    all_judges = sorted(df_long["judge"].unique())
    clean_cols = [
        col.replace("_label", "").replace("_value", "")
        for col in final_df.columns.tolist()
    ]
    fixed_cols = [col for col in clean_cols if col not in all_judges + ["index"]]

    ordered_judge_columns = []
    for judge in all_judges:
        label_col = f"{judge}_label"
        value_col = f"{judge}_value"

        if label_col in final_df.columns:
            ordered_judge_columns.append(label_col)

        if value_col in final_df.columns:
            ordered_judge_columns.append(value_col)

    final_column_order = fixed_cols + ordered_judge_columns
    final_df = final_df[final_column_order]
    final_df.columns.name = None

    metrics = [
        col.replace("_value", "")
        for col in final_df.columns.tolist()
        if "_value" in col
    ]
    parameters = {}
    for metric in metrics:
        parameters[metric] = final_df[f"{metric}_value"].mean()
    tokens_metrics = [
        "completion_tokens",
        "prompt_tokens",
        "total_tokens",
        "step_count",
    ]
    for token_metric in tokens_metrics:
        parameters[token_metric] = final_df[token_metric].mean()

    return final_df, parameters
