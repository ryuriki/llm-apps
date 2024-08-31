import streamlit as st
import json 
import time
from openai import OpenAI
import openai
from pydantic import BaseModel, Field
import os
import base64
import requests

openai.api_key = st.secrets["OPENAI_API_KEY"]

class Ingredient(BaseModel):
    ingredients: str = Field(description="材料", examples=["鶏もも肉"])
    quantity: str = Field(description="分量", examples=["200g"])
    
class Recipe(BaseModel):
    ingredients: list[Ingredient]
    instructions: list[str] = Field(description="手順", examples=["材料を切ります", "材料を炒めます"])
    in_english: str = Field(description="英語の料理名")
    
OUTPUT_RECIPE_FUNCTION = {
    "name": "output_recipe",
    "description": "レシピを出力する",
    "parameters": Recipe.schema(),
}

PROMPT_TEMPLATE = """料理のレシピを教えてください。

料理名: {dish}
"""

st.title("レシピ生成AI")

dish = st.text_input(label="料理名")

if dish:
    with st.spinner(text="AIがレシピを生成中..."):
        client = OpenAI()
        messages = [
            {
                "role": "user",
                "content": PROMPT_TEMPLATE.format(dish=dish)
            }
        ]
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,  
            functions=[OUTPUT_RECIPE_FUNCTION],
            function_call = {"name":OUTPUT_RECIPE_FUNCTION["name"]},
            temperature=0.0,
        )
        response_message = response.choices[0].message
        function_call_args = response_message.function_call.arguments
        
        st.success("AIがレシピを生成しました！")

        # JSONをパース
        recipe = json.loads(function_call_args)

        # レシピを表示
        st.write(f"## 材料")
        st.table(recipe["ingredients"])
        
        # ## 手順
        instruction_markdown = "## 手順\n"
        for i, instruction in enumerate(recipe["instructions"]):
            instruction_markdown += f"{i+1}. {instruction}\n"
        st.markdown(instruction_markdown)
        
        # 画像生成
        engine_id = "stable-diffusion-v1-6"
        api_host = os.getenv('API_HOST', 'https://api.stability.ai')
        api_key = os.environ["STABILITY_API_KEY"]
        
        response = requests.post(
                    f"{api_host}/v1/generation/{engine_id}/text-to-image",
                    headers={
                        "Content-Type": "application/json",
                        "Accept": "application/json",
                        "Authorization": f"Bearer {api_key}"
                    },
                    json={
                        "text_prompts": [
                            {
                                "text": recipe["in_english"],
                            }
                        ],
                        "cfg_scale": 7,
                        "height": 1024,
                        "width": 1024,
                        "samples": 1,
                        "steps": 30,
                    },
                    )
        if response.status_code != 200:
            raise Exception(f"画像生成に失敗しました: {response.text}")
        
        data = response.json()
        for i, image in enumerate(data["artifacts"]):
            with open(f"./out/v1_txt2img_{i}.png", "wb") as f:
                f.write(base64.b64decode(image["base64"]))
                
        st.image(f"./out/v1_txt2img_0.png")