#!/usr/bin/env python3
"""
================================================================================
 travel_planner_explained.py — travel_planner.py 전체 코드에 자세한 한글 설명을 단 버전
================================================================================

[이 프로그램이 하는 일 3단계]
  main() → [1/3] create_recommendation() : AI가 추천 JSON 생성
         → [2/3] search_restaurants()   : 카카오 지도로 맛집 검색
         → [3/3] create_report()        : AI가 Markdown 리포트 작성
         → write_results()              : results/ 폴더에 저장

[왜 JSON을 먼저 만들고 그 다음 카카오 지도를 검색하나요?]
  사람 말("겨울엔 바다가 보이는 곳이 좋아요")은 애매해서 지도 API가 이해할 수 없습니다.
  그래서 1단계에서 AI가 "도시 이름 딱 하나"를 JSON 칸(recommended_city)에 정확히 적어 주고,
  그 이름을 그대로 카카오 검색창에 넣는 것입니다. JSON이 '번역기' 역할을 합니다.

[자주 나오는 용어]
  - API: 프로그램끼리 대화하는 창구. "AI에게 질문 보내기", "지도에 검색 요청"이 모두 API 호출입니다.
  - URL(주소): 서버가 있는 곳. API 키(비밀번호)와 짝을 이룹니다. 주소가 있어야 서버를 찾을 수 있습니다.
  - API 키: 이 프로그램이 서버에 접속할 수 있게 해주는 비밀번호. .env 파일에만 보관합니다.
  - JSON: {"도시": "강릉"} 처럼 칸이 정해진 데이터 형식. 다음 단계에 넘기기 쉽습니다.
  - .env: API 키 같은 비밀을 코드 밖에서 보관하는 파일. GitHub에 올라가지 않습니다.
  - class: 관련 있는 데이터와 기능을 묶는 틀.
  - requests: 인터넷으로 요청(GET/POST)을 보내는 파이썬 도구.
  - GET vs POST: GET은 '질문만 하는 요청'(지도 검색), POST는 '긴 데이터를 보내는 요청'(AI 생성)에 씁니다.
  - CLI: 명령어로 실행하는 프로그램(마우스 클릭 대신 터미널에 명령 입력).
================================================================================
"""
from __future__ import annotations

# argparse: 명령어 옵션(예: -date "2024-01-01")을 읽어 주는 도구입니다.
import argparse
# json: AI 답변 같은 텍스트를 파이썬 딕셔너리로 바꾸고(json.loads),
# 반대로 파이썬 데이터를 JSON 문자열로 바꾸는(json.dumps) 도구입니다.
import json
# os: 운영체제와 대화하는 도구. 여기서는 .env에 적어 둔 API 키를 읽을 때(os.getenv) 씁니다.
import os
# re: 정규표현식 도구. 긴 문장 속에서 JSON 부분만 골라내거나 키를 가릴 때 씁니다.
import re
# sys: 프로그램 자체와 대화하는 도구. 오류 메시지를 화면에 출력(sys.stderr)할 때 씁니다.
import sys
# time: 시간 관련 도구. API가 바쁘다고 하면 '3초 기다렸다가 다시 시도'할 때(time.sleep) 씁니다.
import time
# datetime: 날짜 도구. '2026-02-30'처럼 달력에 없는 날짜인지 검사할 때 씁니다.
from datetime import datetime
# pathlib: 파일 경로 도구. 'results' 폴더 위치를 운영체제에 맞게 다룰 때 씁니다.
from pathlib import Path
# typing: 변수에 어떤 종류의 값이 들어가는지 적어 두는 표시입니다. 실행에는 영향이 없고 가독성을 높입니다.
from typing import Any

# 아래 두 블록은 '있으면 쓰고, 없으면 친절한 안내'를 위한 방어 코드입니다.
try:
# requests: 인터넷으로 GET/POST 요청을 보내는 핵심 도구입니다.
    import requests
except ImportError:
    requests = None  # type: ignore[assignment]

try:
# dotenv: .env 파일을 읽어서 환경변수로 등록해 주는 도구입니다.
    from dotenv import load_dotenv
except ImportError:
    def load_dotenv(*args: Any, **kwargs: Any) -> bool:  # type: ignore[misc]
        return False

# ---------------------------------------------------------------------------
# 설정값(상수) 영역: 프로그램 전체에서 쓰는 값들을 한 곳에 모아 둡니다.
# 대문자로 쓰는 것은 '프로그램 실행 중 바뀌지 않는 값'이라는 약속입니다.
# ---------------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent
RESULTS_DIR = BASE_DIR / "results"
# 카카오 장소 검색 API의 '주소'입니다.
# 왜 주소가 필요할까? API 키는 '비밀번호'일 뿐이고,
# 키만으로는 서버가 '어디에 있는지' 알 수 없습니다.
# 집 주소(URL) 없이 열쇠(API 키)만 들고 가면 집을 못 찾는 것과 같습니다.
# → URL은 서버가 있는 곳, API 키는 출입 허가증이라고 이해하면 됩니다.
KAKAO_KEYWORD_URL = "https://dapi.kakao.com/v2/local/search/keyword.json"
# 구글 Gemini API의 주소입니다. {model} 자리에 모델명이 들어갑니다.
GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
# (대체 제공자) OpenRouter API 주소입니다.
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
# (대체 제공자) Groq API 주소입니다.
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
# 외부 API가 20초 안에 답하지 않으면 '실패'로 처리합니다. 무한정 기다리지 않게 하는 장치입니다.
TIMEOUT_SECONDS = 20
# AI가 반드시 지켜야 할 답변 형식(칸막이)입니다.
# 형식: {"recommended_city": "강릉", "weather": "맑음", "events": ["축제"], "reason": "..."}
# 이 형식으로 답하도록 강제하면 다음 단계(카카오 검색)에서 파싱 실패 확률이 줄어듭니다.
RECOMMENDATION_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "recommended_city": {"type": "string"},
        "weather": {"type": "string"},
        "events": {"type": "array", "items": {"type": "string"}},
        "reason": {"type": "string"},
    },
    "required": ["recommended_city", "weather", "events", "reason"],
}


# class(클래스)란? 관련 있는 데이터와 기능을 묶어 두는 '틀'입니다.
# 파이썬에 원래 있는 RuntimeError를 상속받아,
# '사용자에게 친절하게 보여 줄 우리 프로그램 전용 오류'를 만든 것입니다.
class PlannerError(RuntimeError):
    """사용자에게 안내할 수 있는 오류."""


# HTTP 상태 코드(401, 403, 429 등)를 함께 들고 다니는 오류입니다. status_code 속성에 담아 둡니다.
class GeminiRequestError(RuntimeError):
    """HTTP 상태를 포함하는 Gemini API 요청 오류."""

    def __init__(self, message: str, status_code: int | None = None) -> None:
        super().__init__(message)
        self.status_code = status_code


# 명령어로 입력된 옵션(-date, --cached, --refresh)을 읽고 검증합니다.
# 날짜를 안 주면 실행 중에 직접 물어보고, 진짜 달력에 없는 날짜(예: 2026-02-30)는 거부합니다.
def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Gemini API와 Kakao Local API로 국내 여행 추천 리포트를 생성합니다.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("-date", "--date", dest="travel_date", required=False, default=None, metavar="YYYY-MM-DD", help="여행 날짜 (생략하면 실행 중에 입력받습니다)")
    parser.add_argument("--cached", action="store_true", help="저장된 원본 데이터(JSON)가 있으면 API 재호출 없이 캐시를 재사용합니다.")
    parser.add_argument("--refresh", action="store_true", help="기존 캐시를 무시하고 API를 새로 호출합니다.")
    args = parser.parse_args()
    if args.travel_date is None:
        while True:
            try:
                args.travel_date = input("여행 날짜를 입력하세요 (YYYY-MM-DD): ").strip()
            except (EOFError, KeyboardInterrupt):
                print()
                parser.error("날짜가 입력되지 않았습니다.")
            try:
                datetime.strptime(args.travel_date, "%Y-%m-%d")
                break
            except ValueError:
                print("  - YYYY-MM-DD 형식의 실제 날짜로 다시 입력하세요.")
    else:
        try:
            datetime.strptime(args.travel_date, "%Y-%m-%d")
        except ValueError:
            parser.error("-date/--date는 YYYY-MM-DD 형식의 실제 날짜여야 합니다.")
    return args


# AI가 "경기도" 같은 넓은 지역을 추천해도,
# 지도 검색이 잘 되도록 "가평"처럼 구체적인 도시 이름으로 바꿔 줍니다.
def normalize_city_name(city: str) -> str:
    """광역시/도 등 광역 지자체 명칭이나 수식어를 지도 검색에 적합한 대표 도시/지역명으로 정규화."""
    cleaned = city.strip()
    replacements = {
        "제주특별자치도": "제주",
        "강원특별자치도": "강원",
        "전북특별자치도": "전북",
        "강원도": "강릉",  # 광역 도 단위일 경우 관광 중심 도시로 보정
        "경기도": "가평",
        "충청북도": "단양",
        "충청남도": "태안",
        "전라북도": "전주",
        "전라남도": "여수",
        "경상북도": "경주",
        "경상남도": "통영",
        "서울특별시": "서울",
        "부산광역시": "부산",
        "대구광역시": "대구",
        "인천광역시": "인천",
        "광주광역시": "광주",
        "대전광역시": "대전",
        "울산광역시": "울산",
        "세종특별자치시": "세종",
    }
    return replacements.get(cleaned, cleaned)


# AI 답변 앞뒤에 붙은 설명 문구나 ```json 코드블록을 걷어 내고
# 순수한 JSON 부분만 뽑아냅니다. 그래야 json.loads()가 성공합니다.
def extract_json_object(raw_text: str) -> str:
    """마크다운 코드블록이나 불필요한 앞뒤 텍스트가 섞여 있어도 유효한 JSON 객체 블록만 추출."""
    text = raw_text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text, flags=re.IGNORECASE)
        text = re.sub(r"\s*```$", "", text)
    match = re.search(r"(\{.*\})", text, re.DOTALL)
    if match:
        return match.group(1).strip()
    return text


# 오류 메시지에 API 키가 섞여 나올 수도 있으므로 [REDACTED]로 가려 줍니다.
def redact_secrets(message: str) -> str:
    safe = str(message)
    for name in ("GEMINI_API_KEY", "KAKAO_REST_API_KEY", "OPENROUTER_API_KEY"):
        if key := os.getenv(name):
            safe = safe.replace(key, "[REDACTED]")
    return re.sub(r"(?:AIza|sk-)[A-Za-z0-9_-]+", "[REDACTED]", safe)


# 오류 하나를 {단계, 종류, 내용} 형태로 errors 목록에 추가합니다.
def add_error(errors: list[dict[str, str]], step: str, kind: str, message: str) -> None:
    errors.append({"step": step, "type": kind, "message": redact_secrets(message)[:300]})


# AI가 준 JSON이 우리가 원하는 모양인지 한 번 더 검사합니다.
# (필수 키 4개, 문자열/배열 타입, 빈 값 여부 등)
def validate_recommendation(data: Any) -> dict[str, Any]:
    if not isinstance(data, dict):
        raise ValueError("추천 결과의 최상위 형식이 객체가 아닙니다.")
    if "recommended_city" not in data and len(data) == 1:
        only = next(iter(data.values()))
        if isinstance(only, dict):
            data = only
    if isinstance(data.get("events"), str):
        data["events"] = [s.strip() for s in data["events"].split(",") if s.strip()]
    required = {"recommended_city": str, "weather": str, "events": list, "reason": str}
    for name, value_type in required.items():
        if not isinstance(data.get(name), value_type):
            raise ValueError(f"필수 키 또는 타입이 올바르지 않습니다: {name}")
    if not all(data[name].strip() for name in ("recommended_city", "weather", "reason")):
        raise ValueError("문자열 필수 값이 비어 있습니다.")
    if not all(isinstance(item, str) for item in data["events"]):
        raise ValueError("events의 모든 항목은 문자열이어야 합니다.")
    return data


# .env에서 Gemini 키와 모델명을 읽습니다. 키가 없으면 바로 안내 메시지를 띄웁니다.
def build_gemini_settings() -> tuple[str, str]:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise PlannerError(
            "GEMINI_API_KEY가 설정되지 않았습니다. .env에 GEMINI_API_KEY를 설정하거나 "
            "export GEMINI_API_KEY='YOUR_KEY'를 실행한 뒤 다시 시도하세요."
        )
    # 무료 등급 사용 가능 모델은 계정·시점별로 다를 수 있어 환경변수로 바꿀 수 있다.
    return api_key, os.getenv("GEMINI_MODEL", "gemini-3.8-flash")


# 어떤 AI 제공자(Gemini/Groq/OpenRouter)를 쓸지 정합니다.
# .env의 LLM_PROVIDER 값에 따르고, 없으면 Groq → OpenRouter → Gemini 순으로 키가 있는 것을 씁니다.
def build_llm_settings() -> tuple[str, str, str]:
    """LLM 제공자를 결정한다."""
    provider = os.getenv("LLM_PROVIDER", "").strip().lower()
    groq_key = os.getenv("GROQ_API_KEY")
    if provider == "groq":
        if not groq_key:
            raise PlannerError("GROQ_API_KEY가 설정되지 않았습니다. .env에 GROQ_API_KEY를 설정하세요.")
        return "groq", groq_key, os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
    if provider == "openrouter":
        openrouter_key = os.getenv("OPENROUTER_API_KEY")
        if not openrouter_key:
            raise PlannerError("OPENROUTER_API_KEY가 설정되지 않았습니다. .env에 OPENROUTER_API_KEY를 설정하세요.")
        return "openrouter", openrouter_key, os.getenv("OPENROUTER_MODEL", "openrouter/free")
    if provider == "gemini":
        api_key, model = build_gemini_settings()
        return "gemini", api_key, model

    # LLM_PROVIDER 미설정: Groq → OpenRouter → Gemini 순으로 키가 있으면 사용
    if groq_key:
        return "groq", groq_key, os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
    openrouter_key = os.getenv("OPENROUTER_API_KEY")
    if openrouter_key:
        return "openrouter", openrouter_key, os.getenv("OPENROUTER_MODEL", "openrouter/free")
    api_key, model = build_gemini_settings()
    return "gemini", api_key, model


# OpenRouter 서버에 질문을 보내고 답변 텍스트를 받습니다. 429/503이면 3초 쉬고 최대 2번 더 시도합니다.
def request_openrouter(
    api_key: str, model: str, prompt: str, *, max_output_tokens: int, response_schema: dict[str, Any] | None = None
) -> str:
    if requests is None:
        raise PlannerError("외부 API 호출을 위해 requests 패키지가 필요합니다. pip install -r requirements.txt를 실행하세요.")
    payload: dict[str, Any] = {
        "model": model,
        "messages": [
            {"role": "system", "content": "당신은 한국 국내 여행 추천 전문가입니다. 사용자의 지시를 충실히 따르고, 요구된 형식(JSON 또는 Markdown)으로만 답변하세요."},
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.5,
        "max_tokens": max_output_tokens,
    }
    for attempt in range(3):
        try:
            response = requests.post(
                OPENROUTER_URL,
                headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
                json=payload,
                timeout=TIMEOUT_SECONDS,
            )
            if response.status_code in (429, 503) and attempt < 2:
                print(f"  - OpenRouter 일시적 오류(HTTP {response.status_code}): 3초 후 재시도합니다.")
                time.sleep(3)
                continue
            if response.status_code >= 400:
                raise GeminiRequestError(f"HTTP {response.status_code}", response.status_code)
            data = response.json()
            return str(data["choices"][0]["message"]["content"])
        except GeminiRequestError:
            raise
        except requests.Timeout as exc:
            raise GeminiRequestError(f"timeout after {TIMEOUT_SECONDS} seconds") from exc
        except requests.RequestException as exc:
            raise GeminiRequestError(f"network error: {exc}") from exc
        except (KeyError, IndexError, TypeError, ValueError, json.JSONDecodeError) as exc:
            raise GeminiRequestError(f"response parse error: {exc}") from exc
    raise GeminiRequestError("OpenRouter 요청 재시도 한도를 초과했습니다.")


# Gemini 응답 JSON에서 실제 답변 문장 부분만 꺼냅니다.
def extract_gemini_text(payload: dict[str, Any]) -> str:
    try:
        parts = payload["candidates"][0]["content"]["parts"]
        text = "".join(str(part.get("text", "")) for part in parts if isinstance(part, dict))
    except (KeyError, IndexError, TypeError) as exc:
        raise ValueError("Gemini 응답에 생성 텍스트가 없습니다.") from exc
    if not text.strip():
        raise ValueError("Gemini가 빈 텍스트를 반환했습니다.")
    return text


# Gemini 서버에 질문을 보내고 답변 텍스트를 받습니다.
# thinkingConfig(thinkingBudget: 0)으로 AI의 내부 '생각하기'를 꺼서
# 답변이 중간에 잘리는 현상을 막습니다.
def request_gemini(
    api_key: str, model: str, prompt: str, *, max_output_tokens: int, response_schema: dict[str, Any] | None = None
) -> str:
    if requests is None:
        raise PlannerError("외부 API 호출을 위해 requests 패키지가 필요합니다. pip install -r requirements.txt를 실행하세요.")
    generation: dict[str, Any] = {"temperature": 0.5, "maxOutputTokens": max_output_tokens}
    # thinking 토큰이 maxOutputTokens를 잡아먹어 본문이 잘리는 문제 방지
    generation["thinkingConfig"] = {"thinkingBudget": 0}
    if response_schema:
        generation.update({"responseMimeType": "application/json", "responseSchema": response_schema})
    payload = {
        "systemInstruction": {"parts": [{"text": "당신은 한국 국내 여행 추천 전문가입니다. 사용자의 지시를 충실히 따르고, 요구된 형식(JSON 또는 Markdown)으로만 답변하세요."}]},
        "contents": [{"role": "user", "parts": [{"text": prompt}]}],
        "generationConfig": generation,
    }
    for attempt in range(3):
        try:
            response = requests.post(
                GEMINI_URL.format(model=model),
                headers={"x-goog-api-key": api_key, "Content-Type": "application/json"},
                json=payload,
                timeout=TIMEOUT_SECONDS,
            )
            if response.status_code == 503 and attempt < 2:
                print("  - Gemini 일시적 과부하(HTTP 503): 3초 후 재시도합니다.")
                time.sleep(3)
                continue
            if response.status_code >= 400:
                raise GeminiRequestError(f"HTTP {response.status_code}", response.status_code)
            return extract_gemini_text(response.json())
        except GeminiRequestError:
            raise
        except requests.Timeout as exc:
            raise GeminiRequestError(f"timeout after {TIMEOUT_SECONDS} seconds") from exc
        except requests.RequestException as exc:
            raise GeminiRequestError(f"network error: {exc}") from exc
        except (ValueError, json.JSONDecodeError) as exc:
            raise GeminiRequestError(f"response parse error: {exc}") from exc
    raise GeminiRequestError("Gemini 요청 재시도 한도를 초과했습니다.")


# Groq 서버에 질문을 보내고 답변 텍스트를 받습니다.
def request_groq(
    api_key: str, model: str, prompt: str, *, max_output_tokens: int, response_schema: dict[str, Any] | None = None
) -> str:
    if requests is None:
        raise PlannerError("requests 패키지가 필요합니다. pip install -r requirements.txt")
    payload: dict[str, Any] = {
        "model": model,
        "messages": [
            {"role": "system", "content": "당신은 한국 국내 여행 추천 전문가입니다. 사용자의 지시를 충실히 따르고, 요구된 형식(JSON 또는 Markdown)으로만 답변하세요."},
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.5,
        "max_tokens": max_output_tokens,
    }
    for attempt in range(3):
        try:
            response = requests.post(
                GROQ_URL,
                headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
                json=payload,
                timeout=TIMEOUT_SECONDS,
            )
            if response.status_code in (429, 503) and attempt < 2:
                print(f"  - Groq 일시적 오류(HTTP {response.status_code}): 3초 후 재시도합니다.")
                time.sleep(3)
                continue
            if response.status_code >= 400:
                raise GeminiRequestError(f"HTTP {response.status_code}", response.status_code)
            data = response.json()
            return str(data["choices"][0]["message"]["content"])
        except GeminiRequestError:
            raise
        except requests.Timeout as exc:
            raise GeminiRequestError(f"timeout after {TIMEOUT_SECONDS} seconds") from exc
        except requests.RequestException as exc:
            raise GeminiRequestError(f"network error: {exc}") from exc
        except (KeyError, IndexError, TypeError, ValueError, json.JSONDecodeError) as exc:
            raise GeminiRequestError(f"response parse error: {exc}") from exc
    raise GeminiRequestError("Groq 요청 재시도 한도를 초과했습니다.")


# 1단계: 여행 날짜로 계절을 계산하고, AI에게 도시·날씨·행사·이유를 JSON으로 요청합니다.
# JSON이 깨지면 보정 지시로 최대 2회 다시 시도합니다.
# 여기서 만든 JSON의 recommended_city가 다음 단계 카카오 검색의 입력이 됩니다.
def create_recommendation(api_key: str, model: str, travel_date: str, errors: list[dict[str, str]], provider: str = "gemini") -> dict[str, Any]:
    month = int(travel_date.split("-")[1])
    season = "봄" if month in (3, 4, 5) else "여름" if month in (6, 7, 8) else "가을" if month in (9, 10, 11) else "겨울"
    initial = f"""여행 날짜는 {travel_date}입니다. 이 날짜는 {season}에 해당합니다.
같은 계절이라도 매번 다른 지역을 선정할 수 있도록, {season} 시기에 실제로 방문객이 많은 지역 중 하나를 다양하게 추천하세요.
도/광역 단위(예: 강원도, 경기도)가 아닌 시/군/구 단위의 구체적인 도시명(예: 제주, 강릉, 경주, 여수)을 추천하세요.
추천 근거(reason)에는 반드시 해당 계절({season})의 날씨 특징과 그 계절에 어울리는 이유를 포함하세요.
실시간 예보·확정 행사가 아닌 일반적 계절 경향과 행사 후보를 제시하세요.
JSON 객체만 반환하세요: recommended_city(문자열), weather(문자열), events(문자열 배열 1~3개), reason(2~4문장 문자열)."""
    repair = "설명이나 마크다운 코드블록 없이 recommended_city, weather, events, reason 네 키만 가진 유효한 JSON 객체만 반환하세요."
    for attempt in range(3):
        try:
            raw_text = (request_gemini if provider == "gemini" else request_openrouter if provider == "openrouter" else request_groq)(
                api_key, model, initial if attempt == 0 else repair, max_output_tokens=700, response_schema=RECOMMENDATION_SCHEMA
            )
            json_text = extract_json_object(raw_text)
            return validate_recommendation(json.loads(json_text))
        except (json.JSONDecodeError, ValueError) as exc:
            if attempt < 2:
                print("  - JSON 검증 실패: 형식을 보정하여 재시도합니다.")
                continue
            add_error(errors, "recommendation", "JSON_PARSE_ERROR", str(exc))
            raise PlannerError("LLM 추천 JSON을 생성하지 못했습니다. 잠시 후 다시 시도하세요.") from exc
        except GeminiRequestError as exc:
            status = exc.status_code
            kind = "AUTH_ERROR" if status in (401, 403) else "QUOTA_ERROR" if status == 429 else "NETWORK_OR_API_ERROR"
            add_error(errors, "recommendation", kind, str(exc))
            if status == 429:
                raise PlannerError("LLM 무료 모델의 요청 제한 또는 쿼터를 확인하세요(HTTP 429). 잠시 후 다시 시도하거나 다른 모델을 사용하세요.") from exc
            if status in (401, 403):
                raise PlannerError(f"LLM API 키 또는 설정을 확인하세요(HTTP {status}).") from exc
            raise PlannerError("Gemini API 연결 또는 응답 처리에 실패했습니다.") from exc
    raise PlannerError("Gemini 추천 생성 재시도 한도를 초과했습니다.")


# 카카오가 돌려준 장소 정보를 우리가 쓰는 표준 모양(name, address, ...)으로 바꿉니다.
def normalize_place(place: dict[str, Any]) -> dict[str, Any]:
    def as_number(value: Any) -> float | None:
        try:
            return float(value) if value not in (None, "") else None
        except (TypeError, ValueError):
            return None
    return {
        "name": str(place.get("place_name", "")),
        "address": str(place.get("road_address_name") or place.get("address_name") or ""),
        "category": str(place.get("category_name", "")),
        "url": str(place.get("place_url", "")),
        "x": as_number(place.get("x")), "y": as_number(place.get("y")),
    }


# 2단계: '도시 맛집'으로 카카오 지도에서 검색해 최대 5곳을 가져옵니다.
# 키 없음·인증 실패·결과 0건 등 어떤 문제가 있어도 프로그램은 계속 진행합니다.
def search_restaurants(city: str, errors: list[dict[str, str]]) -> list[dict[str, Any]]:
    kakao_key = os.getenv("KAKAO_REST_API_KEY")
    search_city = normalize_city_name(city)
    if not kakao_key:
        add_error(errors, "place_search", "MISSING_API_KEY", "KAKAO_REST_API_KEY가 없어 장소 검색을 건너뛰었습니다.")
        print("  - KAKAO_REST_API_KEY 미설정: 맛집을 '데이터 없음'으로 처리하고 계속합니다.")
        return []
    try:
        response = requests.get(
            KAKAO_KEYWORD_URL,
            headers={"Authorization": f"KakaoAK {kakao_key}"},
            params={"query": f"{search_city} 맛집", "size": 5},
            timeout=TIMEOUT_SECONDS,
        )
        if response.status_code in (401, 403):
            add_error(errors, "place_search", "AUTH_ERROR", f"HTTP {response.status_code}")
            print(f"  - 장소 검색 인증 실패(HTTP {response.status_code}): 데이터 없음으로 계속합니다.")
            return []
        if response.status_code == 429:
            add_error(errors, "place_search", "QUOTA_ERROR", "HTTP 429")
            print("  - 장소 검색 쿼터 제한(HTTP 429): 데이터 없음으로 계속합니다.")
            return []
        response.raise_for_status()
        documents = response.json().get("documents", [])
        if not isinstance(documents, list):
            raise ValueError("Kakao 응답의 documents 형식이 목록이 아닙니다.")
        places = [normalize_place(place) for place in documents[:5] if isinstance(place, dict)]
        if not places:
            add_error(errors, "place_search", "EMPTY_RESULT", f"0 results for query={city} 맛집")
            print("  - 검색 결과 0건: 데이터 없음으로 계속합니다.")
        return places
    except requests.Timeout:
        add_error(errors, "place_search", "NETWORK_TIMEOUT", f"timeout after {TIMEOUT_SECONDS} seconds")
    except requests.RequestException as exc:
        add_error(errors, "place_search", "NETWORK_OR_HTTP_ERROR", str(exc))
    except (ValueError, json.JSONDecodeError) as exc:
        add_error(errors, "place_search", "RESPONSE_PARSE_ERROR", str(exc))
    print("  - 장소 검색 요청 또는 응답 처리 실패: 데이터 없음으로 계속합니다.")
    return []


# AI 리포트 생성이 실패했을 때, 지금까지 모은 데이터만으로 최소한의 리포트를 만듭니다.
def fallback_report(date: str, recommendation: dict[str, Any], places: list[dict[str, Any]], errors: list[dict[str, str]]) -> str:
    restaurants = "\n".join(f"- **{p['name']}** — {p['address']}" for p in places) or "- 데이터 없음"
    events = "\n".join(f"- {event}" for event in recommendation["events"]) or "- 데이터 없음"
    errors_text = "\n".join(f"- [{e['step']}/{e['type']}] {e['message']}" for e in errors) or "- 없음"
    return f"""# {date} 국내 여행 추천 리포트

> 최종 Gemini 리포트 생성에 실패해 확보한 데이터로 만든 대체 리포트입니다.

## 추천 지역

**{recommendation['recommended_city']}**

## 추천 이유

{recommendation['reason']}

## 날씨 요약

{recommendation['weather']}

## 행사/축제

{events}

## 맛집 추천

{restaurants}

## 1일 일정 제안

오전에는 대표 관광지와 산책 코스를 둘러보고, 오후에는 지역 문화 공간 또는 카페를 방문합니다. 저녁에는 맛집 목록을 확인해 식사하고 야간 산책으로 마무리합니다.

## 오류 요약(errors)

{errors_text}
"""


# 3단계: 추천 JSON·맛집 목록·오류 목록을 AI에게 주고 최종 Markdown 리포트를 받습니다. 실패 시 fallback_report()를 씁니다.
def create_report(api_key: str, model: str, date: str, recommendation: dict[str, Any], places: list[dict[str, Any]], errors: list[dict[str, str]], provider: str = "gemini") -> str:
    source = json.dumps({"recommendation": recommendation, "restaurants": places, "errors": errors}, ensure_ascii=False, indent=2)
    prompt = f"""다음은 {date} 국내 여행 추천 입력 데이터입니다. 이 데이터만 근거로 한국어 Markdown 리포트를 작성하세요.

{source}

반드시 추천 지역, 추천 이유, 날씨 요약, 행사/축제, 맛집 추천, 1일 일정 제안, 오류 요약(errors) 제목을 포함하세요. 맛집 목록이 비어 있으면 맛집 추천에 정확히 '데이터 없음'이라고 쓰고, 행사는 확정이 아닌 후보임을 밝히세요."""
    try:
        report = (request_gemini if provider == "gemini" else request_openrouter if provider == "openrouter" else request_groq)(api_key, model, prompt, max_output_tokens=1400)
        return f"# {date} 국내 여행 추천 리포트\n\n{report.lstrip('# ').strip()}\n"
    except (GeminiRequestError, ValueError) as exc:
        add_error(errors, "report_generation", "GEMINI_REPORT_ERROR", str(exc))
        print("  - 최종 Gemini 리포트 생성 실패: 대체 Markdown 리포트를 저장합니다.")
        return fallback_report(date, recommendation, places, errors)


# 예전에 같은 날짜로 실행해 저장해 둔 JSON이 있으면 읽어 옵니다. (API 비용 절약)
def load_cached_data(date: str) -> dict[str, Any] | None:
    """기존 저장된 원본 데이터(JSON)가 있으면 읽어와 반환 (항목 4: 결과 캐싱 전략)."""
    data_path = RESULTS_DIR / f"{date}_travel_data.json"
    if not data_path.exists():
        return None
    try:
        content = json.loads(data_path.read_text(encoding="utf-8"))
        if isinstance(content, dict) and "recommendation" in content and "restaurants" in content:
            return content
    except Exception:
        return None
    return None


# 최종 결과(원본 JSON과 Markdown 리포트)를 results/ 폴더에 저장합니다.
def write_results(date: str, recommendation: dict[str, Any], places: list[dict[str, Any]], errors: list[dict[str, str]], report: str) -> tuple[Path, Path]:
    RESULTS_DIR.mkdir(exist_ok=True)
    data_path, report_path = RESULTS_DIR / f"{date}_travel_data.json", RESULTS_DIR / f"{date}_travel_plan.md"
    data_path.write_text(json.dumps({"travel_date": date, "recommendation": recommendation, "restaurants": places, "errors": errors}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    report_path.write_text(report, encoding="utf-8")
    return data_path, report_path


# 프로그램의 시작점. 전체 흐름을 지휘합니다.
# 캐시가 있으면 그대로 쓰고, 없으면 [1/3] → [2/3] → [3/3] 순서로 실행합니다.
def main() -> int:
    args = parse_args()
    load_dotenv(BASE_DIR / ".env")
    errors: list[dict[str, str]] = []

    # 항목 4: 결과 캐싱 검사
    cached_data = None
    if args.cached or (not args.refresh and (RESULTS_DIR / f"{args.travel_date}_travel_data.json").exists()):
        cached_data = load_cached_data(args.travel_date)

    if cached_data:
        print(f"[캐시 재사용] {args.travel_date} 저장된 원본 JSON을 활용하여 외부 API 호출을 생략합니다.")
        print("  - (새로고침을 원할 경우 --refresh 옵션을 사용하세요)")
        recommendation = cached_data["recommendation"]
        places = cached_data["restaurants"]
        errors = cached_data.get("errors", [])
        report_path = RESULTS_DIR / f"{args.travel_date}_travel_plan.md"
        data_path = RESULTS_DIR / f"{args.travel_date}_travel_data.json"

        if not report_path.exists():
            report = fallback_report(args.travel_date, recommendation, places, errors)
            report_path.write_text(report, encoding="utf-8")

        print("  - 캐시 기반 리포트 로드 완료")
        print(f"완료! {report_path.relative_to(BASE_DIR)} 및 {data_path.relative_to(BASE_DIR)}를 확인하세요.")
        return 0

    try:
        provider, api_key, model = build_llm_settings()
        print(f"[1/3] 1차 추천 생성 중({provider})...")
        recommendation = create_recommendation(api_key, model, args.travel_date, errors, provider)
        print(f"  - recommended_city: {recommendation['recommended_city']}")
        print("[2/3] 맛집 검색 중(Kakao Local API)...")
        places = search_restaurants(recommendation["recommended_city"], errors)
        print(f"  - 맛집 {len(places)}곳 검색 완료")
        print(f"[3/3] 최종 리포트 생성 중({provider})...")
        report = create_report(api_key, model, args.travel_date, recommendation, places, errors, provider)
        data_path, report_path = write_results(args.travel_date, recommendation, places, errors, report)
        print("  - 리포트 생성 완료")
        print(f"완료! {report_path.relative_to(BASE_DIR)} 및 {data_path.relative_to(BASE_DIR)}를 확인하세요.")
        return 0
    except PlannerError as exc:
        print(f"오류: {exc}", file=sys.stderr)
        return 1


# 이 파일을 직접 실행했을 때만 main()을 호출합니다. (다른 파일에서 import하면 실행되지 않음)
if __name__ == "__main__":
    raise SystemExit(main())
