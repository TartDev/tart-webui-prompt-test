import base64
import re
import uuid
import gradio as gr
import json
import os
import openai
from tqdm import tqdm

class ImgWebUI:
    def __init__(self):
        json_files = [f for f in os.listdir('prompt_save/img_prompt') if f.endswith('.json')]

        self.file_selector = gr.Dropdown(choices=json_files, label="Select a prompt file",value="default.json")
        self.image_patch = gr.Textbox(label="Select a image path",value="./image_path/", interactive=True)
        self.prompt_textbox = gr.Textbox(label="prompt", value=self.load_file_content("default.json"), lines=4, interactive=True)
        self.save_filename_textbox = gr.Textbox(label="Save as", value="", placeholder="Enter filename")
        self.save_button = gr.Button("Save")
        self.load_image_button = gr.Button("Load Image")
        self.generate_result_textbox = gr.JSON(label="Generate result")
        self.generate_result_button = gr.Button("Generate Result")
        
        self.file_selector.change(self.load_file_content, inputs=self.file_selector, outputs=self.prompt_textbox)
        self.load_image_button.click(self.load_image, inputs=None, outputs=None)
        self.generate_result_button.click(self.generate_result, inputs=None, outputs=self.generate_result_textbox)
        self.save_button.click(self.save_file_content, inputs=[self.prompt_textbox,self.save_filename_textbox], outputs=None)
    def load_file_content(self, selected_file):
        with open(f'prompt_save/img_prompt/{selected_file}', 'r', encoding='utf-8') as f:
            return f.read()
    def save_file_content(self,content,filename):
        with open(f'prompt_save/img_prompt/{filename}', 'w', encoding='utf-8') as f:
            f.write(content)
    def load_image(self):
        self.images = [os.path.join(self.image_patch.value, f) for f in os.listdir(self.image_patch.value) if f.endswith(('.png', '.jpg', '.jpeg'))]
        gr.Info("加载图片成功！,共有{}张图片".format(len(self.images)))
    def encode_image_to_base64(self, image_path):
    # 将图片编码为 base64 字符串
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    def save_json_data(self,json_data):
        filename = uuid.uuid4()
        with open(f'image_path/{filename}.json', 'w', encoding='utf-8') as f:
            json.dump(json_data, f, ensure_ascii=False, indent=2)
        return filename
    def generate_result(self,):
        res = []
        for image in tqdm(self.images):
            try:
                file_name = os.path.basename(image)
                image_url = f"https://raw.githubusercontent.com/TartDev/tart-webui-prompt-test/refs/heads/main/image_path/{file_name}"
                image_base64 = self.encode_image_to_base64(image)
                combined_input = f"{self.prompt_textbox.value}"
                messages = [
                        {
                            "role": "user",
                            "content": [
                                {"type": "text", "text": combined_input},  # 提示文本
                                {
                                    "type": "image_url",
                                    "image_url": {
                                        "url": image_url  # 使用 base64 编码的图片
                                    }
                                },
                            ],
                        }
                    ]
                client = openai.OpenAI()
                completion = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages
                )
                json_match = re.search(r'```json\n(.*?)\n```', completion.choices[0].message.content, re.DOTALL)
                if json_match:
                    json_data = json_match.group(1)
                else:
                    print("未找到 JSON 数据")
                res.append({"image":image,"json_data":json_data,"image_base64":image_base64,'content':completion.choices[0].message.content})
            except Exception as e:
                print(e)
        filename = self.save_json_data(res)
        gr.Info("保存成功！文件名为：{},成功生成信息{}条".format(filename,len(res)))
        return res[0]['json_data']

        

