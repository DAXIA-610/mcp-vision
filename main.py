from fastapi import FastAPI
from pydantic import BaseModel
import requests
import base64
import json

app = FastAPI()

class ImageRequest(BaseModel):
    image_url: str

class MCPSuccess(BaseModel):
    output: str

class MCPError(BaseModel):
    error: str

@app.get("/")
def root():
    return {"status": "I from 颖颖造的壳里，正在服役。"}

@app.get("/health")
def health():
    return {"status": "活着，等你发图。"}

@app.post("/mcp", response_model=MCPSuccess)
def mcp_handler(req: ImageRequest):
    try:
        img_resp = requests.get(req.image_url, timeout=15)
        if img_resp.status_code != 200:
            return MCPSuccess(output="图片下载失败，检查链接是否有效。")
        
        img_b64 = base64.b64encode(img_resp.content).decode("utf-8")
        
        payload = {
            "model": "Qwen/Qwen2.5-VL-72B-Instruct",
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "请详细描述这张图片里有什么，包括场景、物体、颜色、文字内容。"},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img_b64}"}}
                    ]
                }
            ]
        }
        
        headers = {
            "Authorization": "Bearer sk-qwtpmqldxlahkwfrllhsrcoaempquogeayizylbhqwotyekm",
            "Content-Type": "application/json"
        }
        
        ai_resp = requests.post(
            "https://api.siliconflow.cn/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=30
        )
        
        if ai_resp.status_code == 200:
            result = ai_resp.json()
            description = result["choices"][0]["message"]["content"]
            return MCPSuccess(output=description)
        else:
            return MCPSuccess(output=f"硅基流动接口返回异常，状态码：{ai_resp.status_code}，建议检查密钥是否有效或余额是否充足。")
    
    except requests.exceptions.Timeout:
        return MCPSuccess(output="图片处理超时，建议换小一点的图或检查网络。")
    except Exception as e:
        return MCPSuccess(output=f"处理出错：{str(e)}")
