import os
import requests
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from dotenv import load_dotenv

from langchain_anthropic import ChatAnthropic
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain.tools import tool
from langchain_core.prompts import ChatPromptTemplate

load_dotenv()

app = FastAPI(title="LangChain Agent API")

llm = ChatAnthropic(model="claude-sonnet-4-6", anthropic_api_key=os.environ["ANTHROPIC_API_KEY"])
HF_API_URL = "https://router.huggingface.co/hf-inference/models/black-forest-labs/FLUX.1-schnell"


@tool
def generate_image(prompt: str) -> str:
    """이미지를 생성합니다. 영어 프롬프트를 입력받아 이미지를 생성하고 결과를 반환합니다."""
    headers = {"Authorization": f"Bearer {os.environ['HF_TOKEN']}"}
    response = requests.post(HF_API_URL, headers=headers, json={"inputs": prompt}, timeout=120)
    if response.status_code == 200:
        return f"이미지 생성 완료 (크기: {len(response.content)} bytes)"
    return f"이미지 생성 실패: {response.status_code}"


@tool
def analyze_prompt(text: str) -> str:
    """텍스트를 분석하여 이미지 생성에 적합한 프롬프트로 변환합니다."""
    return f"Analyzed and optimized prompt: {text}, high quality, detailed, photorealistic, 8k"


@tool
def get_style_suggestions(theme: str) -> str:
    """주제에 맞는 이미지 스타일을 추천합니다."""
    styles = {
        "nature": "cinematic, golden hour, dramatic lighting, landscape photography",
        "city": "urban, neon lights, night photography, bokeh",
        "portrait": "studio lighting, shallow depth of field, professional photography",
        "fantasy": "magical, ethereal, concept art, digital painting",
    }
    for key, value in styles.items():
        if key in theme.lower():
            return value
    return "high quality, detailed, artistic, professional"


tools = [generate_image, analyze_prompt, get_style_suggestions]

prompt = ChatPromptTemplate.from_messages([
    ("system", "당신은 이미지 생성을 도와주는 AI 에이전트입니다. 사용자의 요청을 분석하고 적절한 도구를 사용하여 최적의 결과를 만들어내세요. 한국어로 응답하세요."),
    ("human", "{input}"),
    ("placeholder", "{agent_scratchpad}"),
])

agent = create_tool_calling_agent(llm, tools, prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=False)


class AgentRequest(BaseModel):
    request: str


@app.get("/")
def root():
    return {"status": "running", "message": "LangChain Agent API"}


@app.post("/run")
def run_agent(req: AgentRequest):
    if not req.request.strip():
        raise HTTPException(status_code=400, detail="요청을 입력해주세요")

    result = agent_executor.invoke({"input": req.request})

    return JSONResponse(content={
        "request": req.request,
        "response": result["output"],
    })
