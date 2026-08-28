"""온기록의 Vercel Python Serverless Function.

디자인 원칙: AI는 회복 루틴의 '정답'이 아니라 사용자가 조정할 수 있는 짧은 초안을 만든다.
보안 원칙: Gemini API 키는 GEMINI_API_KEY 환경 변수에서만 읽으며, HTTP 응답·로그에 노출하지 않는다.
"""

from __future__ import annotations

import json
import os
import re
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler
from typing import Any

from google import genai


MAX_NOTE_LENGTH = 200
ALLOWED_MINUTES = {"5", "15", "30"}
ROUTINE_SCHEMA = {
    "type": "object",
    "properties": {
        "kicker": {"type": "string"},
        "title": {"type": "string"},
        "opening": {"type": "string"},
        "steps": {"type": "array", "items": {"type": "string"}, "minItems": 3, "maxItems": 3},
        "note": {"type": "string"},
    },
    "required": ["kicker", "title", "opening", "steps", "note"],
}


def safe_text(value: Any, limit: int = 200) -> str:
    """입력 크기를 제한하고 제어 문자를 제거한다."""
    if not isinstance(value, str):
        return ""
    return re.sub(r"[\x00-\x1f\x7f]", " ", value).strip()[:limit]


def parse_routine(raw: str) -> dict[str, Any]:
    """Gemini의 구조화된 JSON 텍스트를 검사하고 최소 형식을 보장한다."""
    data = json.loads(raw)
    steps = data.get("steps", [])
    if not isinstance(steps, list):
        steps = []

    cleaned_steps = [safe_text(step, 160) for step in steps if safe_text(step, 160)][:3]
    if len(cleaned_steps) < 3:
        raise ValueError("AI 결과의 단계가 충분하지 않습니다.")

    return {
        "kicker": safe_text(data.get("kicker"), 50) or "오늘의 작은 계획",
        "title": safe_text(data.get("title"), 90) or "당신의 회복 루틴",
        "opening": safe_text(data.get("opening"), 260) or "지금 가능한 만큼만 시작해 보세요.",
        "steps": cleaned_steps,
        "note": safe_text(data.get("note"), 220) or "가장 쉬운 단계 하나만 골라도 충분합니다.",
    }


def build_prompt(feeling: str, minutes: str, focus: str, note: str) -> str:
    """서비스 목적에 맞는 짧고 안전한 JSON 응답을 요청한다."""
    optional_note = note if note else "(사용자가 추가 문장을 남기지 않았습니다.)"
    return f"""
당신은 한국어 웰니스 서비스 '온기록'의 루틴 편집 도우미입니다.
사용자가 오늘 바로 해볼 수 있는, 부담이 낮은 일상 회복 루틴의 초안을 작성합니다.
의료적 진단, 치료, 약물 조언, 확정적 심리 판단은 하지 마세요. 위기·자해·타해가 언급되면
다른 루틴을 제시하지 말고 가까운 사람·지역의 응급 서비스·전문 도움에 즉시 연락하도록 부드럽고 명확하게 안내하세요.

사용자 상태: {feeling}
확보 시간: {minutes}분
원하는 감각: {focus}
사용자 메모: {optional_note}

규칙:
1. 총 {minutes}분 안에 가능한 3단계로 구성하고, 각 단계에 대략적인 시간 또는 행동의 크기를 포함하세요.
2. 지나치게 낙관적이거나 훈계하는 말투를 피하고, 선택과 조정의 여지를 남기세요.
3. 결과는 한국어로만 작성하세요.
4. 반환 스키마의 kicker, title, opening, steps, note를 모두 채우세요. steps는 정확히 3개여야 합니다.
"""


class handler(BaseHTTPRequestHandler):
    """POST /api/recommend 요청을 받아 Gemini Interactions API를 호출한다."""

    def _send_json(self, status: int, payload: dict[str, Any]) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self) -> None:  # noqa: N802 - BaseHTTPRequestHandler interface
        self.send_response(HTTPStatus.NO_CONTENT)
        self.send_header("Allow", "POST, OPTIONS")
        self.end_headers()

    def do_POST(self) -> None:  # noqa: N802 - BaseHTTPRequestHandler interface
        content_length = int(self.headers.get("Content-Length", "0"))
        if content_length <= 0 or content_length > 4096:
            self._send_json(HTTPStatus.BAD_REQUEST, {"error": "요청 내용을 확인해 주세요."})
            return

        try:
            payload = json.loads(self.rfile.read(content_length).decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            self._send_json(HTTPStatus.BAD_REQUEST, {"error": "입력 형식을 읽을 수 없습니다."})
            return

        feeling = safe_text(payload.get("feeling"), 80)
        minutes = safe_text(payload.get("minutes"), 8)
        focus = safe_text(payload.get("focus"), 80)
        note = safe_text(payload.get("note"), MAX_NOTE_LENGTH)

        if not feeling or minutes not in ALLOWED_MINUTES or not focus:
            self._send_json(HTTPStatus.BAD_REQUEST, {"error": "현재 상태, 시간, 원하는 감각을 모두 입력해 주세요."})
            return

        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            self._send_json(HTTPStatus.SERVICE_UNAVAILABLE, {"error": "AI 기능 설정이 아직 완료되지 않았습니다. 관리자에게 환경 변수 설정을 요청해 주세요."})
            return

        try:
            client = genai.Client(api_key=api_key)
            interaction = client.interactions.create(
                model=os.environ.get("GEMINI_MODEL", "gemini-3.6-flash"),
                input=build_prompt(feeling, minutes, focus, note),
                response_format={"type": "text", "mime_type": "application/json", "schema": ROUTINE_SCHEMA},
            )
            self._send_json(HTTPStatus.OK, parse_routine(interaction.output_text))
        except (ValueError, json.JSONDecodeError):
            self._send_json(HTTPStatus.BAD_GATEWAY, {"error": "루틴 결과를 정리하지 못했습니다. 다시 시도해 주세요."})
        except Exception as error:  # SDK 버전에 따른 오류 형식을 함께 처리하고 세부 정보는 숨긴다.
            raw_status = getattr(error, "code", None) or getattr(error, "status_code", None)
            try:
                status = int(raw_status) if raw_status is not None else None
            except (TypeError, ValueError):
                status = None
            if status in {401, 403}:
                self._send_json(HTTPStatus.SERVICE_UNAVAILABLE, {"error": "Gemini API 인증 설정을 확인해 주세요."})
            elif status == 429:
                self._send_json(HTTPStatus.TOO_MANY_REQUESTS, {"error": "Gemini 무료 사용량 또는 요청 한도에 도달했습니다. 잠시 후 다시 시도해 주세요."})
            elif status and int(status) >= 500:
                self._send_json(HTTPStatus.BAD_GATEWAY, {"error": "Gemini 서비스가 응답하지 않습니다. 잠시 후 다시 시도해 주세요."})
            else:
                self._send_json(HTTPStatus.INTERNAL_SERVER_ERROR, {"error": "예기치 못한 문제가 발생했습니다. 잠시 후 다시 시도해 주세요."})

    def do_GET(self) -> None:  # noqa: N802 - BaseHTTPRequestHandler interface
        self._send_json(HTTPStatus.METHOD_NOT_ALLOWED, {"error": "POST 요청만 사용할 수 있습니다."})

    def log_message(self, format: str, *args: Any) -> None:  # noqa: A002
        """민감한 요청 본문이나 API 키가 로그에 남지 않도록 기본 로그를 비활성화한다."""
        return
