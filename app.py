import gradio as gr
from stability_interface import GeneratorManager

gen_manager = GeneratorManager()

def generate_image_from_prompt(prompt, gallery):
    result = gen_manager.generate_image(prompt)
    if result.status_code == 200:
        gallery = gallery or []
        gallery.append(result.image)
        return result.image, gallery, gallery
    else:
        return None, gallery, gallery

def main():
    with gr.Blocks() as interface:
        with gr.Column():
            prompt = gr.Textbox(label="Enter your prompt")
            generate_btn = gr.Button("Generate")
            with gr.Row():
                preview = gr.Image(label="Latest Generation")
            with gr.Row():
                gallery = gr.Gallery(label="Generation History")
        
        gallery_state = gr.State([])
        
        generate_btn.click(
            fn=generate_image_from_prompt,
            inputs=[prompt, gallery_state],
            outputs=[preview, gallery, gallery_state]
        )
        
    interface.launch()

if __name__ == "__main__":
    main()