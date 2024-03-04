from io import BytesIO
import logging

from openai import OpenAI
import base64
from PIL import Image
import os
logger = logging.getLogger(__name__)

# scale down image and convert to base64
def base64_image(image_path, max_size=512):
    image = Image.open(image_path)
    image.thumbnail((max_size, max_size))
    buffered = BytesIO()
    image.save(buffered, format="JPEG")
    encoded = base64.b64encode(buffered.getvalue()).decode("utf-8")
    image_str = 'data:image/jpeg;base64,{}'.format(encoded)

    return image_str


class OpenAIApiClient:
    def __init__(self, **kwargs) -> None:
        self.url = kwargs["url"]
        self.model = kwargs.get("model", "None")
        self.api_key = kwargs.get("api_key", "None")
        self.headers = kwargs.get("headers", None)
        self.max_tokens = kwargs.get("max_tokens", 1000)
        self.stop = kwargs.get("stop_sequence", ["###", "\n\n"])
        self.temperature = kwargs.get("temperature", 0.8)
        self.top_p = kwargs.get("top_p", 0.95)

        self.client = OpenAI(api_key=self.api_key, default_headers=self.headers, base_url=self.url)


    def generate_text(self, prompt: str) -> str:
        response = self.client.completions.create(
            model=self.model,
            prompt=prompt,
            max_tokens=self.max_tokens,
            stop=self.stop,
            temperature=self.temperature,
            top_p=self.top_p,
            stream=True
        )
        result = ""
        for chunk in response:
            if chunk.choices[0].text:
                token = chunk.choices[0].text
                result += token
                print(token, end="", flush=True)
        return result.strip()


    def generate_multimodal(self, prompt: str, image: bytes|str) -> str:
        encoded_image = base64_image(image)

        completion = self.client.chat.completions.create(
            model=self.model,
            temperature=self.temperature,
            top_p=self.top_p,
            messages=[
                {
                    "role": "system",
                    "content": "This is a chat between a user and an assistant. The assistant is helping the user to describe an image. Assistant won't ask questions, but will provide answers to the user's prompts."
                },
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": encoded_image,
                            },
                        },
                    ],
                }
            ],
            max_tokens=self.max_tokens,
            stream=True
        )
        result = ""
        for chunk in completion:
            if chunk.choices[0].delta.content:
                token = chunk.choices[0].delta.content
                result += token
                print(token, end="", flush=True)
        return result.strip()