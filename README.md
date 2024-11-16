# Stability Image Generation Demo

This project demonstrates a simple application for generating images using the Stability API, leveraging the Gradio library for a user-friendly interface.

## Table of Contents

- [Overview](#overview)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Running the Application](#running-the-application)
- [Usage](#usage)
- [Application Structure](#application-structure)
- [Important Notes](#important-notes)

## Overview

This demonstration app allows users to generate images using text prompts through Stability's API. It features a graphical interface created with Gradio to make the generation process straightforward and interactive.

The primary components of the project include:

- **GeneratorManager**: Handles API calls to generate images.
- **GeneratorResponse**: Processes and saves the responses from the Stability API.
- **Gradio Interface**: Provides a user-friendly web interface for inputting prompts and viewing the generated images.

## Prerequisites

Before running the application, ensure you have the following installed:

- Python 3.8 or later
- [Pip](https://pip.pypa.io/en/stable/installation/)
- [Stability AI API Key](https://stability.ai/), which should be saved in an `.env` file.

Your `.env` file should include:

```
STABILITY_API_KEY=your_stability_api_key_here
```

## Installation

To get started, follow these steps to set up your environment:

1. Clone the repository to your local machine:

   ```
   git clone https://github.com/grant-king/stability_demo.git
   cd stability_demo
   ```

2. Create a virtual environment and activate it:

   ```
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```

3. Install the necessary packages:

   ```
   pip install -r requirements.txt
   ```

4. Create an `.env` file in the root directory and add your Stability API key:

   ```
   echo "STABILITY_API_KEY=your_stability_api_key_here" > .env
   ```

## Running the Application

To launch the application, simply run:

```sh
python stability_demo/app_demo_2.py
```

The application will start a Gradio web interface that you can interact with through your browser at the provided local address.

## Usage

1. **Enter Your Prompt**: Type in a text prompt describing the image you want to generate.
2. **Select Aspect Ratio**: Choose an aspect ratio for the generated image. Available options include "1:1", "16:9", "9:16", etc.
3. **Generate**: Click on the "Generate" button to create an image. The generated image will be displayed below, and you can view a gallery of all your generated images.

The images are saved locally in the `generated_images` folder.

## Application Structure

- `app_demo_2.py`: Main script that includes the `GeneratorManager` and `GeneratorResponse` classes for interacting with the Stability API and the Gradio interface for user interaction.

### Key Components

- **GeneratorManager**: This class is responsible for making requests to the Stability API and saving responses.

  - `__init__()`: Initializes the API key, base URL, and output directory.
  - `generate_image()`: Sends a request to the Stability API using a given prompt and returns a `GeneratorResponse`.

- **GeneratorResponse**: Handles the response from the API and saves the image.

  - `__init__()`: Processes the API response and saves the generated image to a file if successful.
  - `image()`: Returns the path of the saved image, which Gradio uses for display.

## Important Notes

- **Environment Variables**: The API key is accessed through environment variables for security. Ensure the `.env` file is properly configured before running the script.
- **Stability API**: This demo utilizes the Stability AI API, specifically targeting a model endpoint for image generation. Ensure your API key is valid and has the correct permissions.
- **Gradio UI**: Gradio provides an interactive way for users to input text prompts and view results. The gallery feature keeps a history of generated images during the session.

## Contributions

Contributions are welcome! Feel free to fork the repository and submit pull requests for improvements.

## License

This project is licensed under the Unlicense. See the LICENSE file for more information.

## Contact

For questions or support, please open an issue on the GitHub repository or reach out to `g@grantking.dev`.

---

Happy spinning.

