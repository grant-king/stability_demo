# path stability_demo/generate_video.py
import requests
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta
from pathlib import Path
import gradio as gr
from PIL import Image

VIDEO_API_ENDPOINT = "https://api.stability.ai/v2beta/image-to-video"
OUTPUT_DIR = "generated_videos"

load_dotenv()
api_key = os.getenv("STABILITY_API_KEY")

# Create output directory if it doesn't exist
output_dir = Path(OUTPUT_DIR)
output_dir.mkdir(exist_ok=True)

class VideoGeneratorResponse:
    """
    A class to handle the response from a video generation service and manage the polling and saving of the generated video.
    Attributes:
        start_time (datetime): The time when the response was received.
        last_poll_time (datetime): The last time the generation status was polled.
        generation_id (str): The ID of the video generation process.
        still_processing (bool): A flag indicating if the video generation is still in progress.
        output_path (str): The path where the video or error image will be saved.
        error_messages (list): A list of error messages if any occurred during the video generation.
        video_content (bytes): The content of the generated video.
    Methods:
        __init__(service_response):
            Initializes the VideoGeneratorResponse with the service response.
        poll_generation_status():
            Polls the generation status every 11 seconds until the video generation is complete or an error occurs.
        fetch_generation_status():
            Fetches the current status of the video generation process and handles the response accordingly.
        save_output():
            Saves the generated video content to a file with a unique filename based on the current timestamp.
        video_file():
            Returns the path to the saved video or error image for display.
    """
    def __init__(self, service_response):
        print(f"Response: {service_response}")
        response_data = service_response.json()

        self.start_time = datetime.now()
        self.last_poll_time = self.start_time
        self.generation_id = None
        self.still_processing = True
        self.output_path = os.path.abspath("video_pending.png")
        self.error_messages = []
        self.video_content = None

        if response_data.get('name', None) != None:
            self.error_name = response_data.get('name')
            self.error_messages = response_data.get('errors', [])
            for error_message in self.error_messages:
                print(f"Error: {error_message}")
            self.output_path = os.path.abspath("video_error.png")
            self.still_processing = False

        if service_response.status_code == 200:
            self.generation_id = service_response.json().get('id')
            self.poll_generation_status()

    def poll_generation_status(self):
        # Poll the generation status every 11 seconds    
        while self.still_processing:
            # make sure 11 seconds have passed since the last poll
            current_time = datetime.now()
            if current_time - self.last_poll_time > timedelta(seconds=11):
                self.last_poll_time = current_time
                self.fetch_generation_status()
        print("Finished polling for generation status")
        
    def fetch_generation_status(self):
        print(f"Checking status of generation {self.generation_id}")
        # fetch the status of the generation
        result_endpoint = f"{VIDEO_API_ENDPOINT}/result/{self.generation_id}"

        accept_header = {
            "Accept": "video/*",
            "Authorization": f"Bearer {api_key}",
        }
        
        response = requests.request(
            "GET",
            result_endpoint, 
            headers=accept_header
            )
        
        status = response.status_code
        if status == 200:
            self.still_processing = False
            print(f"STATUS {status} :: Video generation complete")
            self.video_content = response.content
            self.save_output()
        if status in [400, 404, 500]: # invalid parameters, expired, or internal server error
            self.still_processing = False
            self.error_id = response.json().get('id')
            self.error_name = response.json().get('name')
            print(f"STATUS {status} :: Error ID: {self.error_id}")
            self.error_messages = response.json().get('errors', [])
            for error_message in self.error_messages:
                print(f"Error: {error_message}")
            self.output_path = os.path.abspath("video_error.png")
        if status == 202:
            print(f"STATUS {status} :: Stability.ai is still processing. Checking results again in 11 seconds...")
        
    def save_output(self):
        # Generate unique filename using timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"stability_video_{timestamp}.mp4"
        output_path = os.path.abspath(f'{output_dir}/{filename}')

        print(f"Saving video to {output_path}")
        
        # Save the image directly from the response content
        with open(output_path, 'wb') as f:
            f.write(self.video_content)
        
        self.output_path = output_path

    @property
    def video_file(self):
        """Return the path to the saved image for Gradio to display"""
        return os.path.abspath(self.output_path)


def resize_and_crop_image(image_path, size):
    """
    Resize and crop the image to the given size
    """
    with Image.open(image_path) as img:
        # Resize the image to fit within the size, keeping the aspect ratio
        img.thumbnail(size)

        # Crop the image to the exact size
        width, height = img.size
        left = (width - size[0]) / 2
        top = (height - size[1]) / 2
        right = (width + size[0]) / 2
        bottom = (height + size[1]) / 2

        img = img.crop((left, top, right, bottom))

        # make sure the output directory exists
        output_dir_name = "cropped_images"
        Path(output_dir_name).mkdir(exist_ok=True)

        filename = os.path.basename(image_path)
        save_path = os.path.abspath(f"{output_dir_name}/{filename}")
        img.save(save_path)

    return save_path

def resize_and_cover_image(image_path, size):
    """
    Resize and cover the image to the given size
    """
    with Image.open(image_path) as img:
        # calculate the aspect ratio of the image
        input_width, input_height = img.size
        target_width, target_height = size
        input_ratio = input_width / input_height
        target_ratio = target_width / target_height

        # resize the image to fill the target area
        if input_ratio > target_ratio:
            # wider than target, fit to height and crop width
            new_height = target_height
            new_width = int(new_height * input_ratio)
        else:
            # taller than target, fit to width and crop height
            new_width = target_width
            new_height = int(new_width / input_ratio)

        img = img.resize((new_width, new_height))

        # center crop the image to the target size
        left = (new_width - target_width) / 2
        top = (new_height - target_height) / 2
        right = (new_width + target_width) / 2
        bottom = (new_height + target_height) / 2

        img = img.crop((left, top, right, bottom))

        # make sure the output directory exists
        output_dir_name = "covered_images"
        Path(output_dir_name).mkdir(exist_ok=True)

        filename = os.path.basename(image_path)
        save_path = os.path.abspath(f"{output_dir_name}/{filename}")
        img.save(save_path)

    return save_path

def fetch_generate_video(prompt_image_path):
    """
    Generates a video from a given prompt image.
    This function takes the path to a prompt image, resizes and covers it to 1024x576 dimensions,
    and then sends it to a video generation API. The response from the API is then wrapped in a
    VideoGeneratorResponse object and returned.
    Args:
        prompt_image_path (str): The file path to the prompt image.
    Returns:
        VideoGeneratorResponse: The response object containing the details of the generated video.
    """
    print(f"Generating video from {prompt_image_path}")
    # crop to 1024x576
    # cropped_image_path = resize_and_crop_image(prompt_image_path, (1024, 576))
    # cover to 1024x576
    cropped_image_path = resize_and_cover_image(prompt_image_path, (1024, 576))

    headers = {
        "Authorization": f"Bearer {api_key}",
    }
    files = {
        "image": open(cropped_image_path, "rb"), # raw image bytes
        "motion_bucket_id": (None, 222), # motion bucket id
    }
    # Make the request
    service_response = requests.post(
        VIDEO_API_ENDPOINT,
        headers=headers,
        files=files,
    )
    print(f"Response: {service_response}")
    print(f"Response Headers: {service_response.headers}")
    print(f"Response Content: {service_response.content}")
    
    response = VideoGeneratorResponse(service_response)
    return response

def generate_video_from_image(prompt_image_path=None):
    """
    Generates a video from a given image.

    If no image path is provided, the function will use the most recently
    generated image from the "generated_images" directory.

    Args:
        prompt_image_path (str, optional): The file path to the image to be used
                                           for generating the video. Defaults to None.

    Returns:
        dict: A data structure containing the response from the video generation process.
    """
    if prompt_image_path == '' or prompt_image_path is None:
        generated_images_dir = os.listdir("generated_images")
        prompt_image_path = os.path.abspath(f'generated_images/{generated_images_dir[-1]}')
    print(f"Generating video from {prompt_image_path}")
    response_datastruct = fetch_generate_video(prompt_image_path)
    return response_datastruct

def start_generation(prompt_image_path):
    """
    Gradio button callback function. Starts the video generation process from a given prompt image path.

    Args:
        prompt_image_path (str): The file path to the prompt image.

    Returns:
        tuple: A tuple containing:
            - response_datastruct (object): The data structure containing the response from the video generation process.
            - preview (str): The file path to the generated video file for preview.
            - status_text (str): A status message indicating that the generation has started.
            - gallery (list): A list of file paths to the generated video files in the output directory.
    """
    response_datastruct = generate_video_from_image(prompt_image_path)
    return (
        response_datastruct, # current_generation
        response_datastruct.video_file, # preview
        "Generation Started :: click 'Check Status' to see the progress", # status_text
        [os.path.abspath(f'{output_dir}/{file}') for file in os.listdir(output_dir)[::-1] if file.endswith(".mp4")], # gallery
    )


with gr.Blocks() as demo:
    gallery_files = gr.State(value=[])
    current_generation = gr.State(None) # store the current VideoGeneratorResponse object

    with gr.Column():
        with gr.Row():
            image_path = gr.Textbox(
                label="You can paste the image path string here, otherwise the latest image will be used.",
                placeholder="generated_images/your_image.png"
                
                )
        with gr.Row():
            generate_btn = gr.Button("Generate")

        with gr.Row():
            status_text = gr.Textbox(label="Status", interactive=False)
        with gr.Row():
            preview = gr.Image(label="Latest Generation")
        with gr.Row():
            gallery = gr.Gallery(
                value=[os.path.abspath(f'{output_dir}/{file}') for file in os.listdir(output_dir)[::-1] if file.endswith(".mp4")],
                label="Generation History",
                )
    
    generate_btn.click(
        fn=start_generation,
        inputs=[image_path],
        outputs=[current_generation, preview, status_text, gallery],
    )

demo.launch()

    