import yaml

from webui_tab.main_webui import MainWebUI
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
    interface = gr.Blocks(title='PodcaSphere')
    with interface:
        with gr.Tab('Text Prompt'):
            MainWebUI()
    interface.launch(inbrowser=True,share=False, server_name=config["webui"]["host"], server_port=config["webui"]["port"])



if __name__ == "__main__":
    webui()
