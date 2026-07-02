import google.generativeai as genai

class GeminiLLM:
    def __init__(self, api_key):
        self.client = genai.Client(api_key=api_key)

    def generate(self, contents, json_mode=False):
        config = {"response_mime_type": "application/json"} if json_mode else None
        response = self.client.models.generate_content(
            model="gemini-2.5-flash",
            contents=contents,
            config=config
        )
        return response.text