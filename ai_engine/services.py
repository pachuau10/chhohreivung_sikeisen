import json
import re
from django.conf import settings
from .gemini import GeminiClient


class AIService:
    def __init__(self):
        self.client = GeminiClient()

    def generate_mcqs(self, text, count=20):
        prompt = f"""Generate {count} multiple choice questions from this text. Return ONLY a JSON array. Each object must have keys: question, options (array of 4 strings), correct (0-based index), explanation.

{text[:15000]}
"""
        response = self.client.generate(prompt)
        return self._parse_json_array(response)

    def generate_short_questions(self, text, count=10):
        prompt = f"""Generate {count} short answer questions from this text. Return ONLY a JSON array. Each object must have keys: question, answer, explanation.

{text[:15000]}
"""
        response = self.client.generate(prompt)
        return self._parse_json_array(response)

    def generate_long_questions(self, text, count=5):
        prompt = f"""Generate {count} long answer/essay questions from this text. Return ONLY a JSON array. Each object must have keys: question, answer, explanation.

{text[:15000]}
"""
        response = self.client.generate(prompt)
        return self._parse_json_array(response)

    def generate_flashcards(self, text, count=20):
        prompt = f"""Generate {count} flashcards from this text. Return ONLY a JSON array. Each object must have keys: front, back.

{text[:15000]}
"""
        response = self.client.generate(prompt)
        return self._parse_json_array(response)

    def generate_summary(self, text):
        prompt = f"""Write a concise summary of this text covering main topics and key concepts.

{text[:15000]}
"""
        response = self.client.generate(prompt)
        if response.startswith('{"error"'):
            return None
        response = re.sub(r'^```(?:markdown)?\s*', '', response.strip())
        response = re.sub(r'\s*```$', '', response)
        return response.strip()

    def _parse_json_array(self, text):
        import logging
        logger = logging.getLogger(__name__)
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
                    logger.warning('AI returned error: %s', text[:200])
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
        if not parsed:
            logger.warning('Failed to parse AI response (first 500 chars): %s', text[:500])
        return parsed
