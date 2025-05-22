import phoenix as px
from phoenix.evals import (
    TOOL_CALLING_PROMPT_TEMPLATE, 
    llm_classify,
)
from phoenix.trace import SpanEvaluations
from phoenix.trace.dsl import SpanQuery

phoenix_client = px.Client(endpoint="http://34.60.92.205:6006")

query = SpanQuery().where(
    # Filter for the `LLM` span kind.
    # The filter condition is a string of valid Python boolean expression.
    "name =='Agent.step'",
).select(
    question="parameter.input_messages",
)

# The Phoenix Client can take this query and return the dataframe.
tool_calls_df = phoenix_client.query_spans(query, 
                                        project_name="default", 
                                        timeout=None)

#tool_calls_df = tool_calls_df.dropna(subset=["tool_call"])

print(tool_calls_df.head())