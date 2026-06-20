# LangChain Agent

LangChain과 Claude를 결합한 AI 에이전트 - 도구를 사용해 이미지 생성 작업을 자율적으로 수행

## 아키텍처

```
사용자 요청 입력
        ↓
Claude (claude-sonnet-4-6) + LangChain Agent
        ↓
상황에 따라 도구 선택 및 실행
   ├── analyze_prompt: 프롬프트 최적화
   ├── get_style_suggestions: 스타일 추천
   └── generate_image: FLUX.1 이미지 생성
        ↓
최종 결과 반환
```

## 사용 도구 (Tools)

| 도구 | 설명 |
|------|------|
| `analyze_prompt` | 텍스트를 이미지 생성 최적 프롬프트로 변환 |
| `get_style_suggestions` | 주제에 맞는 스타일 키워드 추천 |
| `generate_image` | FLUX.1-schnell로 이미지 생성 |

## API 엔드포인트

| 메서드 | 경로 | 설명 |
|--------|------|------|
| GET | `/` | 서버 상태 확인 |
| POST | `/run` | 에이전트 실행 |
| GET | `/docs` | Swagger UI |

## 요청 예시

```bash
curl -X POST http://localhost:8000/run \
  -H "Content-Type: application/json" \
  -d '{"request": "도시 야경 이미지를 사이버펑크 스타일로 만들어줘"}'
```

## 응답 예시

```json
{
  "request": "도시 야경 이미지를 사이버펑크 스타일로 만들어줘",
  "response": "사이버펑크 스타일의 도시 야경 이미지를 생성했습니다. 네온 불빛과 비에 젖은 도로가 특징적인 이미지입니다."
}
```

## 실행 방법

```bash
cp .env.example .env
pip install -r requirements.txt
cd app && uvicorn main:app --host 0.0.0.0 --port 8009
```

## 환경 변수

```
ANTHROPIC_API_KEY=   # Anthropic Claude API 키
HF_TOKEN=            # HuggingFace API 토큰
```
