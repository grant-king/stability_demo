# stability_interface.py
import requests
import os
from dotenv import load_dotenv
import base64
import io
from PIL import Image

load_dotenv()

class GeneratorManager:
    def __init__(self):
        self.api_key = os.getenv("STABILITY_API_KEY")
        self.base_url = "https://api.stability.ai/v2beta/stable-image"
        self.model_appendage = "core"
        self.responses = []

    def generate_image(self, prompt):
        headers = {
            "Accept": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }

        files = {
            "prompt": (None, prompt),
            "aspect_ratio": (None, "1:1"),
        }

        host = f'{self.base_url}/generate/{self.model_appendage}'
        service_response = requests.post(
            host,
            headers=headers,
            files=files,
            )
        print(service_response)
        response = GeneratorResponse(service_response)
        self.responses.append(response)
        return response
        
    
class GeneratorResponse:
    def __init__(self, service_response):
        self.status_code = service_response.status_code
        self.finish_reason = service_response.headers.get('finish_reason')
        if self.status_code != 200:
            print(f'Error: {service_response.content}')
            return
        
        response_data = service_response.json()
        self.image = self.parse_convert_image(response_data)
        self.seed = response_data.get('seed')


    def parse_convert_image(self, response_data):
        image_data = base64.b64decode(response_data['image'])
        image = Image.open(io.BytesIO(image_data))
        return image
