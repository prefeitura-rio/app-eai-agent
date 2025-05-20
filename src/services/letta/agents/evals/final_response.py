CLARITY_LLM_JUDGE_PROMPT = """
In this task, you will be presented with a query and an answer. Your objective is to evaluate the clarity 
of the answer in addressing the query. A clear response is one that is precise, coherent, and directly 
addresses the query without introducing unnecessary complexity or ambiguity. An unclear response is one 
that is vague, disorganized, or difficult to understand, even if it may be factually correct.

Your response should be a single word: either "clear" or "unclear," and it should not include any other 
text or characters. "clear" indicates that the answer is well-structured, easy to understand, and 
appropriately addresses the query. "unclear" indicates that some part of the response could be better 
structured or worded.
Please carefully consider the query and answer before determining your response.

After analyzing the query and the answer, you must write a detailed explanation of your reasoning to 
justify why you chose either "clear" or "unclear." Avoid stating the final label at the beginning of your 
explanation. Your reasoning should include specific points about how the answer does or does not meet the 
criteria for clarity.

[BEGIN DATA]
Query: {query}
Answer: {response}
[END DATA]
Please analyze the data carefully and provide an explanation followed by your response.

EXPLANATION: Provide your reasoning step by step, evaluating the clarity of the answer based on the query.
LABEL: "clear" or "unclear"
"""

GOLD_STANDART_SIMILARITY_LLM_JUDGE_PROMPT = """
In this task, you will be presented with a query, a model's response to that query, and an ideal response (e.g., from an official entity or a gold standard). Your objective is to evaluate how well the model's response captures the core topics and essential concepts present in the ideal response. The evaluation is not about stylistic similarity or exact phrasing, but about the substantial overlap of key information.

You will categorize the model's response into one of three labels:
- "equivalent": The model's response comprehensively covers all the core topics and essential concepts present in the ideal response. It doesn't need to be a word-for-word match, but the key information and themes must be fully represented.
- "similar": The model's response addresses some, but not all, of the core topics and essential concepts from the ideal response. There's a partial overlap in the key information.
- "different": The model's response covers very few or none of the core topics and essential concepts from the ideal response. The main message or substance diverges significantly.

Your response should be a single word: "different", "similar", or "equivalent", and it should not include any other text or characters.

Please carefully consider the query (for context), the model's response, and the ideal response before determining your evaluation. Focus on identifying the core topics in the ideal response and then checking their presence and completeness in the model's response.

After analyzing all three pieces of information, you must write a detailed explanation of your reasoning to justify your chosen label. Avoid stating the final label at the beginning of your explanation. Your reasoning should include specific points identifying which core topics/concepts from the ideal response are present, partially present, or absent in the model's response. Compare the substance and key takeaways.

[BEGIN DATA]
Query: {query}
Model Response: {model_response}
Ideal Response: {ideal_response}
[END DATA]
Please analyze the data carefully and provide an explanation followed by your response.

EXPLANATION: Provide your reasoning step by step, evaluating the model's response against the ideal response based on core topic coverage. Identify key topics in the ideal response and assess their presence in the model's response.
LABEL: "different", "similar", or "equivalent"
"""

GROUNDEDNESS_LLM_JUDGE_PROMPT = """
In this task, you will be presented with a query, a model's response, the model's "core memory" (a dictionary of key information), and "search tool results" (a list of dictionaries representing retrieved information). Your objective is to evaluate if the model's response is strictly based *only* on the information contained within the provided core memory and search tool results. The model should not introduce external knowledge, facts, or details not present in these provided sources.

You will categorize the model's response using one of two labels:
- "based": Every factual assertion, detail, and piece of information in the model's response can be directly traced back to, or is a direct and reasonable inference solely from, the content of the core memory and/or the search tool results.
- "unfounded": The model's response contains information, claims, or details that are not present in, and cannot be reasonably inferred *solely* from, the provided core memory or search tool results. This indicates the model may have introduced external knowledge or hallucinated information.

Your response should be a single word: either "based" or "unfounded," and it should not include any other text or characters.

Please carefully scrutinize the model's response. For each piece of information it presents, attempt to locate its origin within the provided core memory or search tool results. A response can be "based" even if it rephrases or summarizes the provided information, as long as the core substance is derived from the inputs.

After analyzing all provided data, you must write a detailed explanation of your reasoning to justify why you chose either "based" or "unfounded." Avoid stating the final label at the beginning of your explanation. Your reasoning should meticulously cross-reference claims made in the model's response with the contents of the core memory and search tool results. If you label the response "unfounded," clearly identify the specific statements or pieces of information that lack grounding in the provided context.

[BEGIN DATA]
Query: {query}
Core Memory: {core_memory}
Search Tool Results: {search_tool_results}
Model Response: {model_response}
[END DATA]
Please analyze the data carefully and provide an explanation followed by your response.

EXPLANATION: Provide your reasoning step by step, evaluating if each part of the model's response is directly supported by the core memory or search tool results. Note any information present in the response that cannot be found in the provided context.
LABEL: "based" or "unfounded"
"""