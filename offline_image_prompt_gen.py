import base64
import json
import os
import re

import openai

from tqdm import tqdm
def encode_image_to_base64(image_path):
    # 将图片编码为 base64 字符串
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def load_file_content(selected_file):
    with open(f'prompt_save/img_prompt/{selected_file}', 'r', encoding='utf-8') as f:
        return f.read()
def generate_result(image):
    try:
        file_name = os.path.basename(image)
        image_url = f"https://raw.githubusercontent.com/TartDev/tart-webui-prompt-test/refs/heads/main/image_path/{file_name}"
        # image_base64 = encode_image_to_base64("./image_path/"+image)
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
            return {"image":image,"json_data":json_data,"image_url":image_url,'content':completion.choices[0].message.content}

        else:
            print("未找到 JSON 数据")
            return None
    except Exception as e:
        print(e)
def load_image(image_patch):
    images = [os.path.join(image_patch, f) for f in os.listdir(image_patch) if f.endswith(('.png', '.jpg', '.jpeg'))]
    return images

def update_json_with_results(input_file, images):
    with open(input_file, 'r', encoding='utf-8') as f:
        data = [json.loads(line) for line in f]

    json_images = set(os.path.basename(item.get('image')) for item in data)
    missing_images = [os.path.basename(img) for img in images if os.path.basename(img) not in json_images]
    print("需要更新的数据量：",len(missing_images))
    
    for item in tqdm(missing_images):
        result = generate_result(item)
        if result:
            with open(input_file, 'a+', encoding='utf-8') as out_f:
                out_f.write(json.dumps(result,ensure_ascii=False) + '\n')

# 使用示例
input_file = 'result_new.json'
image_patch = 'image_path/'

combined_input = load_file_content("default.json")
images = load_image(image_patch)

update_json_with_results(input_file, images)
    