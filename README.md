# LangChain Agent

**LangChain**과 **Claude API**를 결합한 AI 에이전트 — 사용자 요청을 분석하고 도구를 자율적으로 선택하여 이미지 생성 작업을 수행

---

## 프로젝트 개요

단순한 API 호출을 넘어, AI가 스스로 판단하여 어떤 도구를 사용할지 결정하는 에이전트 구조를 구현합니다. LangChain의 Tool Calling 기능과 Claude의 추론 능력을 결합하여, 사용자의 자연어 요청을 처리하는 자율적인 AI 에이전트입니다.

---

## 아키텍처

```
사용자 자연어 요청 입력
            ↓
    [ LangChain Agent ]
    Claude claude-sonnet-4-6 (추론 엔진)
    요청 분석 → 필요한 도구 자율 선택
            ↓
    ┌───────────────────────────────┐
    │  사용 가능한 도구 (Tools)       │
    │  ① analyze_prompt            │
    │     텍스트 → 최적화 프롬프트    │
    │  ② get_style_suggestions     │
    │     주제별 스타일 키워드 추천   │
    │  ③ generate_image            │
    │     FLUX.1 이미지 생성        │
    └───────────────────────────────┘
            ↓
    도구 실행 결과를 바탕으로 최종 응답 생성
```

---

## 사용 기술 스택

| 기술 | 역할 |
|------|------|
| **LangChain** | 에이전트 프레임워크, Tool Calling |
| **langchain-anthropic** | LangChain-Claude 연동 |
| **Claude API** (claude-sonnet-4-6) | 추론 엔진 + 도구 선택 |
| **FLUX.1-schnell** | 이미지 생성 도구 |
| **FastAPI** | REST API 서버 |

---

## 에이전트 도구 (Tools)

| 도구 | 입력 | 출력 | 설명 |
|------|------|------|------|
| `analyze_prompt` | 텍스트 | 최적화된 프롬프트 | 자연어를 FLUX 최적 프롬프트로 변환 |
| `get_style_suggestions` | 주제 키워드 | 스타일 키워드 | nature/city/portrait/fantasy별 스타일 추천 |
| `generate_image` | 영어 프롬프트 | 생성 결과 메시지 | FLUX.1-schnell 이미지 생성 |

---

## API 엔드포인트

| 메서드 | 경로 | 설명 |
|--------|------|------|
| `GET` | `/` | 서버 상태 확인 |
| `POST` | `/run` | 에이전트 실행 |
| `GET` | `/docs` | Swagger UI |

---

## 요청 / 응답 예시

```bash
curl -X POST http://localhost:8000/run \
  -H "Content-Type: application/json" \
  -d '{"request": "사이버펑크 도시 야경 이미지를 만들어줘"}'
```

**에이전트 처리 과정:**
1. 요청 분석 → "도시 야경" 테마 파악
2. `get_style_suggestions("city")` 호출 → 스타일 키워드 획득
3. `analyze_prompt(...)` 호출 → 최적화된 프롬프트 생성
4. `generate_image(...)` 호출 → FLUX.1 이미지 생성
5. 최종 결과 반환

**응답:**

```json
{
  "request": "사이버펑크 도시 야경 이미지를 만들어줘",
  "response": "사이버펑크 스타일의 도시 야경 이미지를 생성했습니다. 네온 불빛이 빗물에 반사되는 미래적인 도시 풍경을 표현했습니다."
}
```

---

## 실행 방법

```bash
cp .env.example .env
pip install -r requirements.txt
cd app && uvicorn main:app --host 0.0.0.0 --port 8009
```

## 환경 변수

| 변수 | 설명 |
|------|------|
| `ANTHROPIC_API_KEY` | Anthropic Claude API 키 |
| `HF_TOKEN` | HuggingFace API 토큰 |
