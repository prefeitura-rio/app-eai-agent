SEARCH_RESULT_COVERAGE_LLM_JUDGE_PROMPT = """
In this task, you will evaluate whether a list of search results—each with a 'title' and 'summary'—is likely to lead to a complete and correct answer to the 'user_query'.

You are **not** evaluating an actual answer, but the potential usefulness of the documents linked by these search results.

Use one of the following two labels:
- "covers": At least one or two search results clearly and directly suggest that the corresponding documents contain enough relevant information to fully answer the user's query. Minor irrelevance or noise in other results is acceptable.
- "uncovers": None of the search results appear to contain, even potentially, the information needed to correctly answer the query. The key topics or entities are missing or only tangentially referenced.

After analyzing, you must write a detailed explanation. Your 'explanation' should:
1. The core information need of the user_query.
2. A brief analysis of the most relevant or problematic results, based on their 'title' and 'summary'.
3. A conclusion about whether the search results, collectively, **likely include enough relevant content** to answer the query, even if only a few results are highly relevant.
4. If 'uncovers', explain why the results seem insufficient (e.g., off-topic, too general, missing specific details requested, only tangential relevance).

[BEGIN DATA]
User Query: {query}
Search Tool Results: {search_tool_results}
[END DATA]

Please analyze the data carefully and provide your explanation and label.

explanation: Analyze whether any of the results clearly address the user's intent, even partially. Prioritize quality over quantity.
label: "covers" or "uncovers"
"""
