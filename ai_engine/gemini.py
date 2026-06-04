import json
import logging
import requests
from django.conf import settings

logger = logging.getLogger(__name__)


class GeminiClient:
    def __init__(self):
        self.provider = settings.AI_PROVIDER
        self._init_client()

    def _init_client(self):
        if self.provider == 'groq':
            self.api_key = settings.GROQ_API_KEY
            self.model = settings.GROQ_MODEL
            if not self.api_key:
                logger.warning('GROQ_API_KEY not configured, using mock responses')
        elif self.provider == 'gemini':
            self.api_key = settings.GEMINI_API_KEY
            self.model = None
            if self.api_key:
                try:
                    import google.generativeai as genai
                    genai.configure(api_key=self.api_key)
                    self.model = genai.GenerativeModel('gemini-2.0-flash')
                except Exception as e:
                    logger.error(f'Failed to init Gemini: {e}')
            else:
                logger.warning('GEMINI_API_KEY not configured, using mock responses')

    def generate(self, prompt, temperature=0.7, max_tokens=8192):
        if self.provider == 'groq':
            return self._groq_generate(prompt, temperature, max_tokens)
        elif self.provider == 'gemini':
            return self._gemini_generate(prompt, temperature, max_tokens)
        return self._mock_response(prompt)

    def _groq_generate(self, prompt, temperature, max_tokens):
        if not self.api_key:
            return self._mock_response(prompt)
        try:
            resp = requests.post(
                'https://api.groq.com/openai/v1/chat/completions',
                headers={'Authorization': f'Bearer {self.api_key}', 'Content-Type': 'application/json'},
                json={'model': self.model, 'messages': [{'role': 'user', 'content': prompt}], 'temperature': temperature, 'max_tokens': max_tokens},
                timeout=60,
            )
            resp.raise_for_status()
            return resp.json()['choices'][0]['message']['content']
        except Exception as e:
            logger.error(f'Groq API error: {e}')
            return json.dumps({'error': f'Groq API error: {e}'})

    def _gemini_generate(self, prompt, temperature, max_tokens):
        if not self.model:
            return self._mock_response(prompt)
        try:
            import google.generativeai as genai
            response = self.model.generate_content(prompt, generation_config={'temperature': temperature, 'max_output_tokens': max_tokens})
            return response.text
        except Exception as e:
            logger.error(f'Gemini API error: {e}')
            return json.dumps({'error': f'Gemini API error: {e}'})

    def _mock_response(self, prompt):
        if 'MCQ' in prompt or 'multiple choice' in prompt.lower():
            return self._mock_mcqs()
        elif 'short answer' in prompt.lower():
            return self._mock_short()
        elif 'long answer' in prompt.lower() or 'essay' in prompt.lower():
            return self._mock_long()
        elif 'flashcard' in prompt.lower():
            return self._mock_flashcards()
        elif 'summary' in prompt.lower():
            return self._mock_summary()
        return 'AI generation requires a valid API key.'

    def _mock_mcqs(self):
        return json.dumps([
            {'question': 'What is the primary function of the cell membrane?', 'options': ['Energy production', 'Selective barrier', 'Protein synthesis', 'DNA replication'], 'correct': 1, 'explanation': 'The cell membrane acts as a selective barrier.'},
            {'question': 'Which organelle is responsible for ATP production?', 'options': ['Nucleus', 'Ribosome', 'Mitochondria', 'Golgi apparatus'], 'correct': 2, 'explanation': 'Mitochondria are the powerhouses of the cell.'},
        ])

    def _mock_short(self):
        return json.dumps([
            {'question': 'Explain the process of photosynthesis.', 'answer': 'Photosynthesis converts light energy into chemical energy using chlorophyll.', 'explanation': 'Occurs in chloroplasts.'},
            {'question': 'What is the difference between DNA and RNA?', 'answer': 'DNA is double-stranded with deoxyribose; RNA is single-stranded with ribose.', 'explanation': 'Both are nucleic acids.'},
        ])

    def _mock_long(self):
        return json.dumps([
            {'question': 'Describe evolution by natural selection.', 'answer': 'Organisms better adapted to their environment survive and produce more offspring.', 'explanation': 'Key: variation, selection pressure, inheritance.'},
        ])

    def _mock_flashcards(self):
        return json.dumps([
            {'front': 'What is photosynthesis?', 'back': 'Plants convert light into chemical energy'},
            {'front': 'What is DNA?', 'back': 'Deoxyribonucleic acid - genetic material'},
        ])

    def _mock_summary(self):
        return 'This study material covers fundamental biological concepts including cell structure, energy production, and molecular biology.'
