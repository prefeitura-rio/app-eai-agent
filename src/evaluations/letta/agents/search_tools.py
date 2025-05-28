SEARCH_RESULT_COVERAGE_LLM_JUDGE_PROMPT = """
In this task, you will be presented with an original 'user_query' and a list of 'search_results'. Each search result is a dictionary containing a 'title' and a 'summary' of a document retrieved by a search tool. Your objective is to evaluate if the combined information from the titles and summaries of these search results indicates that the underlying documents likely contain the necessary content to correctly and comprehensively answer the 'user_query'. You are not evaluating a generated answer from these results, but rather the potential of the search snippets themselves to lead to an answer.

The 'label' field in your JSON output should be a single word: either "covers" or "uncovers."
- "covers" indicates that, based on the titles and summaries, the search results collectively seem to contain sufficient information, suggesting the full documents would likely allow for a complete answer to the user's query.
- "uncovers" indicates that the titles and summaries suggest the search results are insufficient, largely irrelevant, or miss key aspects needed to answer the user's query, making it unlikely the full documents would provide a complete answer.

Consider if the results address the main entities and the core intent of the user's query. It's about the potential of the retrieved documents, not a perfect answer within the snippets themselves.

After analyzing, you must write a detailed explanation. Your 'explanation' should:
1. Briefly state the core information need or question presented in the 'user_query'.
2. For each search result (or a selection of the most relevant/problematic ones if there are many), briefly comment on its apparent relevance based on its 'title' and 'summary', and what key information it hints at regarding the 'user_query'.
3. Conclude whether the collection of search results, as indicated by their titles and summaries, likely 'covers' the information needed for the query or 'uncovers' it (i.e., fails to cover it adequately).
4. If 'uncovers', explain why the results seem insufficient (e.g., off-topic, too general, missing specific details requested, only tangential relevance).

[BEGIN DATA]
User Query: {query}
Search Results: {search_results}
[END DATA]
Please analyze the data carefully and provide your explanation and label in the specified JSON format.

explanation: First, identify the core information sought by the user_query. Then, review the title and summary of each search result to assess its potential relevance. Finally, judge if the collective search_results likely indicate that the full documents would cover the query's needs.
label: "covers":1 or "uncovers":0

OUTPUT FORMAT

```
{
    'explanation':str,
    'label':str,
    'value':int
}
```
"""
