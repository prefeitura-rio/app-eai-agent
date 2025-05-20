import os
from google import genai
from google.genai import types

import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir.split("src")[0])

client = genai.Client(
    api_key=os.environ.get("GEMINI_API_KEY"),
)


from src.evaluations.letta.agents.final_response import (
    CLARITY_LLM_JUDGE_PROMPT,
    GOLD_STANDART_SIMILARITY_LLM_JUDGE_PROMPT,
    GROUNDEDNESS_LLM_JUDGE_PROMPT,
    LOCATION_POLICY_COMPLIANCE_JUDGE_PROMPT,
    EMERGENCY_HANDLING_COMPLIANCE_JUDGE_PROMPT,
    FEEDBACK_HANDLING_COMPLIANCE_JUDGE_PROMPT,
    SECURITY_PRIVACY_COMPLIANCE_JUDGE_PROMPT,
    WHATSAPP_FORMATTING_COMPLIANCE_JUDGE_PROMPT,
)

import logging

logging.basicConfig(level=logging.INFO)


class Model:
    def generate_content(
        self,
        prompt,
        system_prompt=None,
        temperature=0.1,
        model="gemini-2.5-pro-preview-05-06",
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
            temperature=temperature,
            # response_mime_type= "application/json",
            response_mime_type="text/plain",  # "application/json"
            system_instruction=[
                types.Part.from_text(text=system_prompt),
            ],
        )

        response = client.models.generate_content(
            model=model,
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

    def judge(self, judge_name: str, eval_results: dict):

        possible_judges = [
            "clarify",
            "location",
            "emergency",
            "feedback",
            "security",
            "whatsapp",
            "gold_standart",
            "groundness",
        ]

        if judge_name not in possible_judges:
            raise ValueError(f"Judge must be one of {possible_judges}")

        query = eval_results.get("query")
        letta_response = eval_results.get("letta_response")
        core_memory = eval_results.get("core_memory")
        search_tool_results = eval_results.get("search_tool_results")
        ideal_response = eval_results.get("ideal_response")

        prompt_basic = f"""
            Query: {query}
            Model Response: {letta_response}
        """
        judge_configs = {
            "clarify": {
                "system_prompt": CLARITY_LLM_JUDGE_PROMPT,
                "prompt": prompt_basic,
            },
            "location": {
                "system_prompt": LOCATION_POLICY_COMPLIANCE_JUDGE_PROMPT,
                "prompt": prompt_basic,
            },
            "emergency": {
                "system_prompt": EMERGENCY_HANDLING_COMPLIANCE_JUDGE_PROMPT,
                "prompt": prompt_basic,
            },
            "feedback": {
                "system_prompt": FEEDBACK_HANDLING_COMPLIANCE_JUDGE_PROMPT,
                "prompt": prompt_basic,
            },
            "security": {
                "system_prompt": SECURITY_PRIVACY_COMPLIANCE_JUDGE_PROMPT,
                "prompt": prompt_basic,
            },
            "whatsapp": {
                "system_prompt": WHATSAPP_FORMATTING_COMPLIANCE_JUDGE_PROMPT,
                "prompt": prompt_basic,
            },
            "gold_standart": {
                "system_prompt": GOLD_STANDART_SIMILARITY_LLM_JUDGE_PROMPT,
                "prompt": f"""
                    Query: {query}
                    Model Response: {letta_response}
                    Ideal Response: {ideal_response}
                    """,
            },
            "groundness": {
                "system_prompt": GROUNDEDNESS_LLM_JUDGE_PROMPT,
                "prompt": f"""
                    Query: {query}
                    Model Response: {letta_response}
                    Core Memory: {core_memory}
                    Search Tool Results: {search_tool_results}
                """,
            },
        }

        judge_config = judge_configs[judge_name]

        logging.info(f"Getting response from {judge_name} judge")
        response = self.generate_content(
            prompt=judge_config["prompt"], system_prompt=judge_config["system_prompt"]
        )
        judge_config["response"] = response
        eval_results[judge_name] = judge_config

        return eval_results
