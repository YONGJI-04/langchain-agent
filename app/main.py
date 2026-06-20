import os
import uuid
from typing import Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
import anthropic
import requests
import base64

load_dotenv()
client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
HF_API_URL = "https://router.huggingface.co/hf-inference/models/black-forest-labs/FLUX.1-schnell"

app = FastAPI(title="LangChain Agent API", description="자율적으로 도구를 선택하는 AI 에이전트", version="1.1.0")

sessions: dict[str, list] = {}

TOOLS = [
    {
        "name": "analyze_prompt",
        "description": "사용자의 이미지 생성 요청을 분석하여 의도와 스타일을 파악합니다",
        "input_schema": {"type": "object", "properties": {"user_request": {"type": "string", "description": "사용자의 이미지 생성 요청"}}, "required": ["user_request"]}
    },
    {
        "name": "get_style_suggestions",
        "description": "이미지 스타일과 품질 향상을 위한 키워드를 제안합니다",
        "input_schema": {"type": "object", "properties": {"theme": {"type": "string"}, "mood": {"type": "string"}}, "required": ["theme"]}
    },
    {
        "name": "generate_image",
        "description": "최적화된 프롬프트로 FLUX.1을 사용하여 이미지를 생성합니다",
        "input_schema": {"type": "object", "properties": {"optimized_prompt": {"type": "string"}}, "required": ["optimized_prompt"]}
    }
]

def handle_tool(name: str, inputs: dict) -> str:
    if name == "analyze_prompt":
        return f"분석 완료: '{inputs['user_request']}' - 사용자는 특정 이미지 생성을 원합니다"
    elif name == "get_style_suggestions":
        theme = inputs.get("theme", "")
        mood = inputs.get("mood", "balanced")
        return f"스타일 제안: {theme} 테마, {mood} 분위기 - high quality, detailed, cinematic lighting, 8k resolution"
    elif name == "generate_image":
        prompt = inputs["optimized_prompt"]
        hf_res = requests.post(HF_API_URL, headers={"Authorization": f"Bearer {os.environ['HF_TOKEN']}"}, json={"inputs": prompt, "parameters": {"width": 1024, "height": 1024}}, timeout=120)
        if hf_res.status_code == 200:
            return f"이미지 생성 완료 (base64): {base64.b64encode(hf_res.content).decode('utf-8')[:50]}..."
        return f"이미지 생성 실패: {hf_res.status_code}"

class AgentRequest(BaseModel):
    request: str
    session_id: Optional[str] = None

@app.get("/")
def root():
    return {"status": "running", "message": "LangChain Agent API"}

@app.post("/run")
def run_agent(req: AgentRequest):
    session_id = req.session_id or uuid.uuid4().hex
    history = sessions.get(session_id, [])

    history.append({"role": "user", "content": req.request})

    system = "당신은 이미지 생성을 도와주는 AI 에이전트입니다. 주어진 도구를 활용하여 사용자의 요청을 처리하세요."
    messages = history.copy()

    final_answer = ""
    tool_calls_made = []

    for _ in range(5):
        response = client.messages.create(model="claude-sonnet-4-6", max_tokens=1000, system=system, tools=TOOLS, messages=messages)
        if response.stop_reason == "end_turn":
            for block in response.content:
                if hasattr(block, "text"):
                    final_answer = block.text
            break
        if response.stop_reason == "tool_use":
            messages.append({"role": "assistant", "content": response.content})
            tool_results = []
            for block in response.content:
                if block.type == "tool_use":
                    tool_calls_made.append(block.name)
                    result = handle_tool(block.name, block.input)
                    tool_results.append({"type": "tool_result", "tool_use_id": block.id, "content": result})
            messages.append({"role": "user", "content": tool_results})

    history.append({"role": "assistant", "content": final_answer})
    sessions[session_id] = history

    return {"session_id": session_id, "request": req.request, "answer": final_answer, "tools_used": tool_calls_made, "turn": len([m for m in history if m["role"] == "user"])}

@app.delete("/session/{session_id}")
def clear_session(session_id: str):
    if session_id in sessions:
        del sessions[session_id]
        return {"message": "세션 삭제 완료"}
    raise HTTPException(status_code=404, detail="세션을 찾을 수 없습니다")
