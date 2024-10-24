from openai import OpenAI

class GenTextModel:
    def __init__(self, config):
        self.openai_api_key = config.get("openai_api_key")
        self.openai_client = OpenAI(api_key=self.openai_api_key)

    def generate_text(self, prompt: str) -> str:
        response = self.openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "system", "content": prompt}]
        )
        return response.choices[0].message.content