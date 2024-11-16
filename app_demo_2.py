# path stability_demo/app_demo_2.py
import requests
import os
from dotenv import load_dotenv
from datetime import datetime
from pathlib import Path
import gradio as gr

load_dotenv()

class GeneratorManager:
    """
    A class to manage the generation of images using the Stability API.
    Attributes:
        api_key (str): The API key for accessing the Stability API.
        base_url (str): The base URL for the Stability API.
        model_appendage (str): The model appendage for the API endpoint.
        responses (list): A list to store responses from the API.
        output_dir (Path): The directory where generated images will be saved.
    Methods:
        generate_image(prompt, aspect_ratio="1:1"):
            Generates an image based on the provided prompt and aspect ratio.
            Args:
                prompt (str): The text prompt to generate the image.
                aspect_ratio (str): The aspect ratio of the generated image. Default is "1:1".
            Returns:
                GeneratorResponse: The response object containing the generated image and metadata.
    """
    def __init__(self, output_dir="generated_images"):
        self.api_key = os.getenv("STABILITY_API_KEY")
        self.base_url = "https://api.stability.ai/v2beta/stable-image"
        self.model_appendage = "core"
        self.responses = []
        
        # Create output directory if it doesn't exist
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)

    def generate_image(self, prompt, aspect_ratio="1:1"):
        headers = {
            "Accept": "image/*",  # Request direct image response
            "Authorization": f"Bearer {self.api_key}",
        }

        files = {
            "prompt": (None, prompt),
            "aspect_ratio": (None, aspect_ratio),
            "output_format": (None, "png"),  # Explicitly request PNG format
        }

        host = f'{self.base_url}/generate/{self.model_appendage}'
        
        # Make the request
        service_response = requests.post(
            host,
            headers=headers,
            files=files,
        )
        
        response = GeneratorResponse(service_response, self.output_dir)
        self.responses.append(response)
        return response

class GeneratorResponse:
    """
    A class to handle the response from a service and save the image content to a specified directory.
    Attributes:
        status_code (int): The HTTP status code from the service response.
        finish_reason (str): The reason for the completion of the service response.
        image_path (Path or None): The path where the image is saved, or None if the image was not saved.
    Methods:
        __init__(service_response, output_dir):
            Initializes the GeneratorResponse with the service response and output directory.
            Saves the image content to the specified directory if the response is successful.
        image:
            Returns the path to the saved image as a string for Gradio to display, or None if the image was not saved.
    """
    def __init__(self, service_response, output_dir):
        self.status_code = service_response.status_code
        self.finish_reason = service_response.headers.get('finish_reason')
        self.image_path = None
        
        if self.status_code != 200:
            print(f'Error: {service_response.content}')
            return
        
        # Generate unique filename using timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"stability_{timestamp}.png"
        self.image_path = output_dir / filename
        
        # Save the image directly from the response content
        with open(self.image_path, 'wb') as f:
            f.write(service_response.content)

    @property
    def image(self):
        """Return the path to the saved image for Gradio to display"""
        return str(self.image_path) if self.image_path else None

gen_manager = GeneratorManager()

def generate_image_from_prompt(prompt, aspect_ratio, gallery):
    result = gen_manager.generate_image(prompt, aspect_ratio)
    if result.status_code == 200:
        gallery = gallery or []
        gallery.append(result.image)
        return result.image, gallery, gallery
    else:
        return None, gallery, gallery

def main():
    with gr.Blocks() as interface:
        with gr.Column():
            with gr.Row():
                prompt = gr.Textbox(label="Enter your prompt")
                aspect_ratio = gr.Dropdown(
                    choices=["1:1", "16:9", "9:16", "4:5", "5:4", "3:2", "2:3", "9:21", "21:9"],
                    value="1:1",
                    label="Aspect Ratio"
                )
            generate_btn = gr.Button("Generate")
            with gr.Row():
                preview = gr.Image(label="Latest Generation")
            with gr.Row():
                gallery = gr.Gallery(label="Generation History")
        
        gallery_state = gr.State([])
        
        generate_btn.click(
            fn=generate_image_from_prompt,
            inputs=[prompt, aspect_ratio, gallery_state],
            outputs=[preview, gallery, gallery_state]
        )
    
    interface.launch()

if __name__ == "__main__":
    main()