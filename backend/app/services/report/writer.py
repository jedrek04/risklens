import json

from google import genai
from google.genai import types

from backend.app.config import GEMINI_LOCATION, GEMINI_MODEL, PROJECT_ID
from backend.app.services.report.prompt import SYSTEM_PROMPT, ReportDraft, build_prompt


class WriterError(Exception):
    pass


class GeminiWriter:
    def __init__(self, client=None, model: str = GEMINI_MODEL):
        self._client = client
        self.model = model

    @property
    def client(self):
        if self._client is None:
            self._client = genai.Client(vertexai=True, project=PROJECT_ID, location=GEMINI_LOCATION)
        return self._client

    def write(self, facts: dict, problems: list[str] | None = None) -> ReportDraft:
        response = self.client.models.generate_content(
            model=self.model,
            contents=build_prompt(facts, problems),
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT,
                temperature=0.2,
                max_output_tokens=4096,
                response_mime_type="application/json",
                response_schema=ReportDraft,
                thinking_config=types.ThinkingConfig(thinking_level="low"),
            ),
        )

        try:
            return ReportDraft.model_validate(json.loads(response.text))
        except Exception as e:
            raise WriterError(f"model returned an unusable answer: {e}")
