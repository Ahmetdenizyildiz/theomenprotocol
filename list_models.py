import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(
    api_key=os.getenv("QWEN_API_KEY"),
    base_url="https://hackathon.bitgetops.com/v1",
)
try:
    models = client.models.list()
    for m in models.data:
        print(m.id)
except Exception as e:
    print("Error:", e)
