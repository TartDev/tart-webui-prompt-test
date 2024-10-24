import gradio as gr
import json
import os
import openai

class MainWebUI:
    def __init__(self):
        self.components = []
        with open('config/form_template.json', 'r', encoding='utf-8') as f:
            form_data = json.load(f)
        json_files = [f for f in os.listdir('prompt_save/text_prompt') if f.endswith('.json')]
        with gr.Row():
            with gr.Column():
                for question in form_data['questions']:
                    label = question['question']
                    options = question.get('options', [])
                    if "[Open-ended field]" in options:
                        self.components.append(gr.Textbox(label=label))
                    else:
                        self.components.append(gr.Radio(choices=options, label=label))

            # 使用 Row 布局来组织文件选择和编辑部分
            with gr.Column():
                self.file_selector = gr.Dropdown(choices=json_files, label="Select a prompt file",value="default.json")
                self.prompt_textbox = gr.Textbox(label="prompt", value=self.load_file_content("default.json"), lines=4, interactive=True)
                # 如果有对prompt的更改需求，可以打开这两个文件
                self.save_filename_textbox = gr.Textbox(label="Save as", value="", placeholder="Enter filename")
                self.save_button = gr.Button("Save")
                self.mood_textbox = gr.Textbox(label="Now the mood")
                self.submit_button = gr.Button("Submit")
                self.generate_result_textbox = gr.Textbox(label="Generate result")
                gr.Markdown("1. 需要填写表单和现在的情绪 ")
                gr.Markdown("2. 点击提交按钮，生成结果 ")
                gr.Markdown("3. 如果需要修改prompt，请在文件选择器中选择文件，然后修改prompt文本框中的内容，保存后会覆盖原来的文件，保持prompt的格式")
        self.save_button.click(self.save_file_content, inputs=[self.prompt_textbox, self.save_filename_textbox], outputs=None)
        self.submit_button.click(self.generate_result, inputs=[*self.components,self.mood_textbox], outputs=self.generate_result_textbox)
        self.file_selector.change(self.load_file_content, inputs=self.file_selector, outputs=self.prompt_textbox)

    def get_form_data(self, *args):
        components_data = {}
        for component, value in zip(self.components, args):
            components_data[component.label] = value
        print(components_data)
        return json.dumps(components_data, ensure_ascii=False, indent=2)

    def load_file_content(self, selected_file):
        # 读取选定的 JSON 文件内容
        with open(f'prompt_save/text_prompt/{selected_file}', 'r', encoding='utf-8') as f:
            file_content = json.load(f)
        return json.dumps(file_content, indent=2)  # 格式化 JSON 内容以便显示

    def save_file_content(self, content, filename):
        if filename == "":
            return
        # 将内容保存到指定的 JSON 文件中
        if not filename.endswith('.json'):
            filename += '.json'
        with open(f'prompt_save/text_prompt/{filename}', 'w', encoding='utf-8') as f:
            json.dump(json.loads(content), f, ensure_ascii=False, indent=2)
    def generate_result(self, *args):
        # 组合 prompt 和表单数据
        combined_input = f"{self.prompt_textbox.value}".replace("${FORM_DATA}", self.get_form_data(*args)).replace("${USER_INPUT}",args[-1])
        # 调用 OpenAI API
        from openai import OpenAI
        client = OpenAI()
        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "user", "content": combined_input}
            ]
        )
        
        return completion.choices[0].message
