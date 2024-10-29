import base64
from transformers import AutoTokenizer, AutoModel
import torch
import re
import uuid
import gradio as gr
import json
import os
import openai
import faiss

class RecallWebUI:
    def __init__(self):
        self.image_data = []
        self.index = faiss.IndexFlatL2(768)
        
        self.model_name = "BAAI/bge-base-en-v1.5"
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        self.model = AutoModel.from_pretrained(self.model_name).to(self.device)

        json_files = [f for f in os.listdir('./image_path/') if f.endswith('.json')]
        json_files.sort(key=lambda f: os.path.getmtime(os.path.join('./image_path/', f)))
        self.file_selector = gr.Dropdown(choices=json_files, label="Select a prompt file", value=json_files[0])
        self.doc_offline_button = gr.Button("Doc offline")

        self.query_textbox = gr.Textbox(label="Query",value="")
        self.topk = gr.Textbox(label="TopK",value="3")
        self.recall_button = gr.Button("Recall")
        self.image_gallery = gr.Gallery(label="Retrieved Images")  # 创建图像画廊
        
        self.file_selector.change(self.update_file_selector, inputs=None, outputs=self.file_selector)

        self.doc_offline_button.click(self.insert_query, inputs=None, outputs=None)
        self.recall_button.click(self.query_embeddings, inputs=[self.query_textbox,self.topk], outputs=self.image_gallery)
    
    def get_openai_embeddings(self, text):
        response = openai.Embedding.create(
            input=text,
            model="text-embedding-ada-002"  # 使用 OpenAI 的嵌入模型
        )
        return response['data'][0]['embedding']

    def get_embeddings(self,text):
        inputs = self.tokenizer([text], return_tensors="pt", padding=True, truncation=True).to(self.device)
        with torch.no_grad():
            outputs = self.model(**inputs)
        return outputs[0][:, 0].cpu().numpy()
    def insert_query(self,key="summary",use_cache = False):
        doc_list = self.load_file_content(self.file_selector.value)
        if use_cache:
            self.load_index(f"./index/{self.file_selector.value}")
            return
        else:
            for item in doc_list:
                self.image_data.append(item['image_base64'])
                self.index.add(self.get_embeddings(eval(item["json_data"])[key]))
    def query_embeddings(self, query, topk):
        query_embedding = self.get_embeddings(query)
        _, indices = self.index.search(query_embedding, int(topk))
        
        # 使用 indices 获取对应的 image_data
        retrieved_images = [self.image_data[i] for i in indices[0]]  # 假设 indices 是二维数组
        
        # 保存图像并返回路径
        image_paths = []
        for i, img in enumerate(retrieved_images):
            image_path = f"./tmp/image_{i}.jpg"  # 定义保存路径
            with open(image_path, "wb") as f:
                f.write(base64.b64decode(img))  # 解码并保存图像
            image_paths.append(image_path)  # 添加路径到列表
        
        return image_paths  # 返回图像路径列表
    def load_file_content(self, selected_file):
        with open(f'./image_path/{selected_file}', 'r', encoding='utf-8') as f:
            return json.load(f)
        
    def save_index(self, file_path="./"):
        faiss.write_index(self.index, file_path)  # 保存 FAISS 索引到文件
        with open(file_path + '_images.json', 'w', encoding='utf-8') as f:
            json.dump(self.image_data, f)  # 保存图像数据到 JSON 文件

    def load_index(self, file_path="./"):
        self.index = faiss.read_index(file_path)  # 从文件加载 FAISS 索引
        with open(file_path + '_images.json', 'r', encoding='utf-8') as f:
            self.image_data = json.load(f)  # 从 JSON 文件加载图像数据

    def update_file_selector(self):
        json_files = [f for f in os.listdir('./image_path/') if f.endswith('.json')]
        json_files.sort(key=lambda f: os.path.getmtime(os.path.join('./image_path/', f)))
        return json_files  # 返回更新后的文件列表
