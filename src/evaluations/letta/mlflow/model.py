import json
import os
import sys
import textwrap

current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir.split("src")[0])


from google import genai
from google.genai import types

from src.evaluations.letta.agents.final_response import (
    CLARITY_LLM_JUDGE_PROMPT,
    GOLD_STANDART_SIMILARITY_LLM_JUDGE_PROMPT,
    GROUNDEDNESS_LLM_JUDGE_PROMPT,
    LOCATION_POLICY_COMPLIANCE_JUDGE_PROMPT,
    EMERGENCY_HANDLING_COMPLIANCE_JUDGE_PROMPT,
    FEEDBACK_HANDLING_COMPLIANCE_JUDGE_PROMPT,
    SECURITY_PRIVACY_COMPLIANCE_JUDGE_PROMPT,
    WHATSAPP_FORMATTING_COMPLIANCE_JUDGE_PROMPT,
    ANSWER_COMPLETENESS_LLM_JUDGE_PROMPT,
    ENTITY_PRESENCE_LLM_JUDGE_PROMPT,
)


from src.evaluations.letta.agents.router import (
    TOOL_CALLING_LLM_JUDGE_PROMPT,
    SEARCH_QUERY_EFFECTIVENESS_LLM_JUDGE_PROMPT,
)

from src.evaluations.letta.agents.search_tools import (
    SEARCH_RESULT_COVERAGE_LLM_JUDGE_PROMPT,
)


import logging

logging.basicConfig(level=logging.INFO)

client = genai.Client(
    api_key=os.environ.get("GEMINI_API_KEY"),
)


class Model:

    def __init__(
        self,
        model="gemini-2.5-flash-preview-04-17",
        temperature=0.1,
    ) -> None:
        self.model = model
        self.temperature = temperature

    async def generate_content(
        self,
        prompt,
        system_prompt=None,
    ):
        contents = [
            types.Content(
                role="user",
                parts=[
                    types.Part.from_text(text=prompt),
                ],
            ),
        ]
        generate_content_config = types.GenerateContentConfig(
            temperature=self.temperature,
            response_mime_type="application/json",
            system_instruction=[
                types.Part.from_text(text=system_prompt),
            ],
        )

        response = await client.aio.models.generate_content(
            model=self.model,
            contents=contents,
            config=generate_content_config,
        )

        output_text = ""
        if hasattr(response, "candidates") and response.candidates:
            for candidate in response.candidates:
                if (
                    hasattr(candidate, "content")
                    and candidate.content
                    and hasattr(candidate.content, "parts")
                ):
                    for part in candidate.content.parts:
                        if hasattr(part, "text") and part.text:
                            output_text += part.text

        return output_text

    async def judge(self, judge_name: str, eval_results: dict):

        logging.info(f"Evaluating {judge_name} judge")
        possible_judges = [
            "clarify",
            "location_policy_compliance",
            "emergency_handling_compliance",
            "feedback_handling_compliance",
            "security_privacy_compliance",
            "whatsapp_formating",
            "answer_completness",
            "entity_presence",
            "gold_standart",
            "groundness",
            "tool_calling",
            "search_query_effectiveness",
            "search_result_coverage",
        ]

        if judge_name not in possible_judges:
            raise ValueError(f"Judge must be one of {possible_judges}")

        query = eval_results["query"]
        letta_response = eval_results["letta_response"]
        ideal_response = eval_results["ideal_response"]

        search_tool_results = eval_results["search_tool_results"]
        search_tool_query = eval_results["search_tool_query"]
        tool_call = eval_results["tool_call"]

        core_memory = eval_results.get("core_memory")
        tool_definitions = eval_results.get("tool_definitions")

        prompt_basic = textwrap.dedent(
            f"""
                Query: {query}
                Model Response: {letta_response}
            """
        )

        judge_configs = {
            "clarify": {
                "system_prompt": CLARITY_LLM_JUDGE_PROMPT,
                "prompt": prompt_basic,
            },
            "location_policy_compliance": {
                "system_prompt": LOCATION_POLICY_COMPLIANCE_JUDGE_PROMPT,
                "prompt": prompt_basic,
            },
            "emergency_handling_compliance": {
                "system_prompt": EMERGENCY_HANDLING_COMPLIANCE_JUDGE_PROMPT,
                "prompt": prompt_basic,
            },
            "feedback_handling_compliance": {
                "system_prompt": FEEDBACK_HANDLING_COMPLIANCE_JUDGE_PROMPT,
                "prompt": prompt_basic,
            },
            "security_privacy_compliance": {
                "system_prompt": SECURITY_PRIVACY_COMPLIANCE_JUDGE_PROMPT,
                "prompt": prompt_basic,
            },
            "whatsapp_formating": {
                "system_prompt": WHATSAPP_FORMATTING_COMPLIANCE_JUDGE_PROMPT,
                "prompt": prompt_basic,
            },
            "answer_completness": {
                "system_prompt": ANSWER_COMPLETENESS_LLM_JUDGE_PROMPT,
                "prompt": prompt_basic,
            },
            "entity_presence": {
                "system_prompt": ENTITY_PRESENCE_LLM_JUDGE_PROMPT,
                "prompt": prompt_basic,
            },
            "gold_standart": {
                "system_prompt": GOLD_STANDART_SIMILARITY_LLM_JUDGE_PROMPT,
                "prompt": textwrap.dedent(
                    f"""
                        Query: {query}
                        Model Response: {letta_response}
                        Ideal Response: {ideal_response}
                    """
                ),
            },
            "groundness": {
                "system_prompt": GROUNDEDNESS_LLM_JUDGE_PROMPT,
                "prompt": textwrap.dedent(
                    f"""
                        Query: {query}
                        Model Response: {letta_response}
                        Core Memory: {core_memory}
                        Search Tool Results: {search_tool_results}
                    """
                ),
            },
            "tool_calling": {
                "system_prompt": TOOL_CALLING_LLM_JUDGE_PROMPT,
                "prompt": textwrap.dedent(
                    f"""
                    Question: {query}
                    ************
                    Tool Called: {tool_call}
                    ************
                    Tool Definitions: {tool_definitions}
                    """
                ),
            },
            "search_query_effectiveness": {
                "system_prompt": SEARCH_QUERY_EFFECTIVENESS_LLM_JUDGE_PROMPT,
                "prompt": textwrap.dedent(
                    f"""
                    User Query: {query}
                    Search Tool Query: {search_tool_query}
                    """
                ),
            },
            "search_result_coverage": {
                "system_prompt": SEARCH_RESULT_COVERAGE_LLM_JUDGE_PROMPT,
                "prompt": textwrap.dedent(
                    f"""
                        User Query: {query}
                        Search Results: {search_tool_results}
                    """
                ),
            },
        }

        judge_config = judge_configs[judge_name]
        no_info_response = {
            "judge": judge_name,
            "system_prompt": None,
            "prompt": None,
            "response": None,
        }
        if judge_name == "search_result_coverage" and not search_tool_results:
            logging.warning(f"Judge {judge_name} does not have enough information!")
            return no_info_response
        elif judge_name == "search_query_effectiveness" and not search_tool_query:
            logging.warning(f"Judge {judge_name} does not have enough information!")
            return no_info_response
        elif judge_name == "tool_calling" and (not tool_call or not tool_definitions):
            logging.warning(f"Judge {judge_name} does not have enough information!")
            return no_info_response
        elif judge_name == "groundness" and (
            not core_memory or not search_tool_results
        ):
            logging.warning(f"Judge {judge_name} does not have enough information!")
            return no_info_response
        else:
            logging.info(f"Getting response from {judge_name} judge")
            response = await self.generate_content(
                prompt=judge_config["prompt"],
                system_prompt=judge_config["system_prompt"],
            )

            return {
                "judge": judge_name,
                "system_prompt": judge_config["system_prompt"],
                "prompt": judge_config["prompt"],
                "response": json.loads(response),
            }
