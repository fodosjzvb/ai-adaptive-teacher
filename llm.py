from google import genai

class GeminiLLM:
    def __init__(self, api_key):
        self.client = genai.Client(api_key=api_key)

    def generate(self, prompt):
        response = self.client.models.generate_content(
            model="gemini-1.5-pro",
            contents=prompt
        )
        return response.text
