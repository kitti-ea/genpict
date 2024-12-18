# app.py

import os
import streamlit as st
import openai
import pandas as pd
import requests
from io import BytesIO
from PIL import Image
import base64

# ตั้งค่า OpenAI API key จาก Streamlit Secrets หรือ Environment Variable
openai_api_key = st.secrets["OPENAI_API_KEY"] if "secrets" in st.__dict__ else os.getenv("OPENAI_API_KEY")

if not openai_api_key:
    st.warning("กรุณากรอก OpenAI API Key ของคุณในช่องด้านล่าง!")
    openai_api_key = st.text_input("OpenAI API Key", type="password")

st.title("สร้างภาพด้วย OpenAI DALL·E")
st.write("Desing by kitti.isuzu@gmail.com")
st.write("ป้อนคำอธิบายภาพที่คุณต้องการ จากนั้น OpenAI จะสร้างภาพให้คุณ!")

# ฟังก์ชันในการสร้างภาพ
def generate_image(prompt, api_key):
    try:
        response = openai.Image.create(
            prompt=prompt,
            n=1,
            size="1024x1024",  # ขนาดภาพ 1080x1080 โดยใช้ 1024x1024 เนื่องจาก OpenAI รองรับขนาดนี้
            response_format="url"  # รับ URL ของภาพ
        )
        image_url = response['data'][0]['url']
        return image_url
    except Exception as e:
        st.error(f"เกิดข้อผิดพลาด: {e}")
        return None

# ฟังก์ชันในการดาวน์โหลดภาพและแปลงเป็น Base64
def download_image(image_url):
    try:
        response = requests.get(image_url)
        img = Image.open(BytesIO(response.content))
        buffered = BytesIO()
        img.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        return img_str
    except Exception as e:
        st.error(f"เกิดข้อผิดพลาดในการดาวน์โหลดภาพ: {e}")
        return None

# ฟอร์มสำหรับรับ prompt จากผู้ใช้
with st.form(key='image_form'):
    prompt = st.text_input("ป้อนคำอธิบายภาพที่ต้องการ", "")
    submit_button = st.form_submit_button(label='สร้างภาพ')

if submit_button and prompt and openai_api_key:
    with st.spinner('กำลังสร้างภาพ...'):
        image_url = generate_image(prompt, openai_api_key)
    
    if image_url:
        # ดาวน์โหลดภาพจาก URL
        img_data = download_image(image_url)
        
        if img_data:
            # สร้าง DataFrame สำหรับแสดงผล
            df = pd.DataFrame({
                "Prompt": [prompt],
                "Image": [f'<img src="data:image/png;base64,{img_data}" width="256">']
            })

            st.markdown("### ผลลัพธ์ที่ได้:")
            # แสดง DataFrame พร้อมกับภาพ
            st.markdown(df.to_html(escape=False, index=False), unsafe_allow_html=True)

            # ปุ่มดาวน์โหลดภาพ
            st.markdown("#### ดาวน์โหลดภาพ:")
            href = f'<a href="data:file/png;base64,{img_data}" download="generated_image.png">คลิกที่นี่เพื่อดาวน์โหลดภาพ</a>'
            st.markdown(href, unsafe_allow_html=True)
