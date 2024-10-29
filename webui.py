import yaml

from webui_tab.recall_webui import RecallWebUI
from webui_tab.text_webui import TextWebUI
from webui_tab.img_webui import ImgWebUI

with open("config/config.yaml", "r") as f:
    config = yaml.safe_load(f)

print(config)

# _*_ coding:utf-8 _*_
"""
@date: 2024/6/18
@filename: webui
"""
import threading
import gradio as gr

def webui():
    interface = gr.Blocks(title='Tart')
    with interface:
        with gr.Tab('Text Prompt'):
            TextWebUI()
        with gr.Tab('Image Prompt'):
            ImgWebUI()
        with gr.Tab('Recall'):
            RecallWebUI()
    interface.launch(inbrowser=True,share=False, server_name=config["webui"]["host"], server_port=config["webui"]["port"])



if __name__ == "__main__":
    webui()
