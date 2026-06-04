import json
import re
from django.conf import settings
from .gemini import GeminiClient


class AIService:
    def __init__(self):
        self.client = GeminiClient()

    def generate_mcqs(self, text, count=20):
        prompt = f"""Based on the following study material, generate {count} multiple choice questions.
Return a valid JSON array of objects with keys: question, options, correct, explanation. No other text.

Study material:
{text[:15000]}
"""
        response = self.client.generate(prompt)
        return self._parse_json_array(response)

    def generate_short_questions(self, text, count=10):
        prompt = f"""Based on the following study material, generate {count} short answer questions.
Return a valid JSON array of objects with keys: question, answer, explanation. No other text.

Study material:
{text[:15000]}
"""
        response = self.client.generate(prompt)
        return self._parse_json_array(response)

    def generate_long_questions(self, text, count=5):
        prompt = f"""Based on the following study material, generate {count} long answer/essay questions.
Return a valid JSON array of objects with keys: question, answer, explanation. No other text.

Study material:
{text[:15000]}
"""
        response = self.client.generate(prompt)
        return self._parse_json_array(response)

    def generate_flashcards(self, text, count=20):
        prompt = f"""Based on the following study material, generate {count} flashcards.
Return a valid JSON array of objects with keys: front, back. No other text.

Study material:
{text[:15000]}
"""
        response = self.client.generate(prompt)
        return self._parse_json_array(response)

    def generate_summary(self, text):
        prompt = f"""Based on the following study material, write a comprehensive summary covering the main topics and key concepts. Write in clear paragraphs.

Study material:
{text[:15000]}
"""
        response = self.client.generate(prompt)
        if response.startswith('{"error"'):
            return None
        response = re.sub(r'^```(?:markdown)?\s*', '', response.strip())
        response = re.sub(r'\s*```$', '', response)
        return response.strip()

    def _parse_json_array(self, text):
        text = text.strip()
        text = re.sub(r'```(?:json)?\s*', '', text)
        text = text.strip()
        start = text.find('[')
        if start >= 0:
            text = text[start:]
            end = text.rfind(']')
            if end > 0:
                text = text[:end+1]
        else:
            start = text.find('{')
            if start >= 0:
                text = text[start:]
                end = text.rfind('}')
                if end > 0:
                    text = text[:end+1]
        try:
            result = json.loads(text)
            if isinstance(result, dict):
                if 'error' in result:
                    return []
                return [result]
            return result
        except json.JSONDecodeError:
            pass
        try:
            text = text.replace("'", '"')
            text = re.sub(r'(?<!")(\btrue\b|\bfalse\b|null)(?!")', lambda m: m.group(0).lower(), text)
            return json.loads(text) if isinstance(json.loads(text), list) else [json.loads(text)]
        except (json.JSONDecodeError, TypeError):
            pass
        items = re.findall(r'\{[^{}]*\}', text)
        parsed = []
        for item in items:
            try:
                parsed.append(json.loads(item))
            except json.JSONDecodeError:
                try:
                    fixed = item.replace("'", '"')
                    parsed.append(json.loads(fixed))
                except json.JSONDecodeError:
                    continue
        return parsed
