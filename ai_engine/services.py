import json
import re
from django.conf import settings
from .gemini import GeminiClient


class AIService:
    def __init__(self):
        self.client = GeminiClient()

    def generate_mcqs(self, text, count=20):
        prompt = f"""Based on the following study material, generate {count} multiple choice questions.
For each question, provide:
- question: The question text
- options: An array of 4 possible answers
- correct: The index (0-3) of the correct answer
- explanation: Brief explanation of the correct answer

Format your response as a valid JSON array of objects with keys: question, options, correct, explanation

Study material:
{text[:15000]}

Return ONLY the JSON array, no other text."""
        response = self.client.generate(prompt)
        return self._parse_json_array(response)

    def generate_short_questions(self, text, count=10):
        prompt = f"""Based on the following study material, generate {count} short answer questions.
For each question, provide:
- question: The question text
- answer: The expected answer (2-3 sentences)
- explanation: Additional context

Format your response as a valid JSON array of objects with keys: question, answer, explanation

Study material:
{text[:15000]}

Return ONLY the JSON array, no other text."""
        response = self.client.generate(prompt)
        return self._parse_json_array(response)

    def generate_long_questions(self, text, count=5):
        prompt = f"""Based on the following study material, generate {count} long answer/essay questions.
For each question, provide:
- question: The question text
- answer: Model answer with key points
- explanation: Grading criteria or hints

Format your response as a valid JSON array of objects with keys: question, answer, explanation

Study material:
{text[:15000]}

Return ONLY the JSON array, no other text."""
        response = self.client.generate(prompt)
        return self._parse_json_array(response)

    def generate_flashcards(self, text, count=20):
        prompt = f"""Based on the following study material, generate {count} flashcards.
Each flashcard should have:
- front: The question/term
- back: The answer/definition

Format your response as a valid JSON array of objects with keys: front, back

Study material:
{text[:15000]}

Return ONLY the JSON array, no other text."""
        response = self.client.generate(prompt)
        return self._parse_json_array(response)

    def generate_summary(self, text):
        prompt = f"""Based on the following study material, write a comprehensive summary.
Cover the main topics, key concepts, and important details.
Keep the summary well-structured with paragraphs.

Study material:
{text[:15000]}

Write the summary in clear, concise language."""
        response = self.client.generate(prompt)
        if response.startswith('{"error"'):
            return None
        return response

    def _parse_json_array(self, text):
        text = text.strip()
        text = re.sub(r'```json\s*', '', text)
        text = re.sub(r'```\s*', '', text)
        text = text.strip()
        start = text.find('[')
        end = text.rfind(']')
        if start >= 0 and end > start:
            text = text[start:end+1]
        try:
            result = json.loads(text)
            if isinstance(result, dict) and 'error' in result:
                return []
            return result
        except json.JSONDecodeError:
            try:
                text = text.replace("'", '"')
                text = re.sub(r'(?<!")(\btrue\b|\bfalse\b|null)(?!")', lambda m: m.group(0).lower(), text)
                return json.loads(text)
            except json.JSONDecodeError:
                return []
