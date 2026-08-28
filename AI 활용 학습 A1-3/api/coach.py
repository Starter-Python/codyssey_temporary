"""ENTHES 공식 스쿼시 리그 (ESL) AI 코칭 분석 엔진.

Vercel Python Serverless Function (POST /api/coach).
보안 원칙: GEMINI_API_KEY는 환경 변수에서만 안전하게 읽으며, 응답이나 로그에 노출하지 않습니다.
안전 원칙: API 키 미설정 또는 네트워크 장애 시에도 내장 휴리스틱 룰 엔진으로 분석을 지속합니다.
"""

from __future__ import annotations

import json
import os
import re
import urllib.error
import urllib.request
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler
from typing import Any

MAX_MEMO_LENGTH = 500
VALID_LEAGUES = {"1부", "2부", "3부"}

COACH_RESPONSE_SCHEMA = {
    "type": "object",
    "properties": {
        "summary": {"type": "string"},
        "strengths": {"type": "string"},
        "improvements": {"type": "string"},
        "drills": {"type": "array", "items": {"type": "string"}, "minItems": 2, "maxItems": 3},
        "stat_adjustments": {
            "type": "object",
            "properties": {
                "forehand": {"type": "integer"},
                "backhand": {"type": "integer"},
                "volley": {"type": "integer"},
                "drive": {"type": "integer"},
                "drop": {"type": "integer"},
                "boast": {"type": "integer"},
            },
            "required": ["forehand", "backhand", "volley", "drive", "drop", "boast"],
        },
        "model_used": {"type": "string"},
    },
    "required": ["summary", "strengths", "improvements", "drills", "stat_adjustments"],
}


def clean_text(value: Any, max_len: int = 500) -> str:
    """텍스트 입력값을 정제하고 제어 문자를 제거합니다."""
    if not isinstance(value, str):
        return ""
    sanitized = re.sub(r"[\x00-\x1f\x7f]", " ", value).strip()
    return sanitized[:max_len]


def rule_based_analysis(player_a: str, player_b: str, score_a: int, score_b: int, memo: str) -> dict[str, Any]:
    """Gemini API 키가 없거나 외부 API 호출 실패 시 작동하는 고품질 내장 휴리스틱 룰 엔진."""
    winner = player_a if score_a > score_b else player_b
    diff = abs(score_a - score_b)

    adjustments = {
        "forehand": 0,
        "backhand": 0,
        "volley": 0,
        "drive": 0,
        "drop": 0,
        "boast": 0,
    }

    strengths_list = []
    improvements_list = []
    drills_list = []

    # 포핸드 / 드라이브 분석
    if any(k in memo for k in ["포핸드", "드라이브", "스트로크", "포"]):
        if any(w in memo for w in ["깊", "강", "좋", "안정", "정확", "꽂", "승리"]):
            adjustments["forehand"] += 1
            adjustments["drive"] += 1
            strengths_list.append("사이드월을 타고 흐르는 깊은 렝스 드라이브로 랠리 주도권을 확보했습니다.")
        if any(w in memo for w in ["범실", "빗", "아쉬", "뜬", "길", "짧", "실수"]):
            adjustments["drive"] = max(-1, adjustments["drive"] - 1)
            improvements_list.append("드라이브 타점이 뒤로 밀려 사이드월 간격이 벌어지는 현상을 줄여야 합니다.")
            drills_list.append("단독 사이드월 밀착 솔로 드라이브 50회 연습 (벽과 라켓 1그립 유지)")

    # 백핸드 분석
    if any(k in memo for k in ["백핸드", "백", "백사이드"]):
        if any(w in memo for w in ["좋", "정확", "깊", "탈출", "성공"]):
            adjustments["backhand"] += 1
            strengths_list.append("백핸드 코너에서의 안정적인 리턴과 수비 전환 능력이 돋보였습니다.")
        if any(w in memo for w in ["부족", "범실", "어려", "불안", "약"]):
            adjustments["backhand"] = max(-1, adjustments["backhand"] - 1)
            improvements_list.append("백핸드 수비 시 몸의 회전(어깨 턴)을 미리 만들어 여유를 확보하세요.")
            drills_list.append("백핸드 코너 3벽 보스트 탈출 및 크로스 리턴 20회 반복 드릴")

    # 발리 / 전위 / T존 분석
    if any(k in memo for k in ["발리", "t존", "T존", "가로채", "전위", "커팅"]):
        if any(w in memo for w in ["좋", "빠르", "선제", "공격", "장악"]):
            adjustments["volley"] += 1
            strengths_list.append("T-존에서 한 템포 빠른 가로채기 발리로 상대의 복귀 타이밍을 빼앗았습니다.")
        if any(w in memo for w in ["놓침", "느림", "밀림", "범실"]):
            adjustments["volley"] = max(-1, adjustments["volley"] - 1)
            improvements_list.append("공이 지나간 뒤 뒤쫓기보다 T-존에서 라켓 헤드를 미리 들고 준비해야 합니다.")
            drills_list.append("파트너와 2인 T-존 연속 발리 랠리 30회 유지 훈련")

    # 드롭 / 숏게임 / 닉샷 분석
    if any(k in memo for k in ["드롭", "앞벽", "닉", "숏", "앞코너"]):
        if any(w in memo for w in ["정교", "예리", "득점", "좋", "완벽"]):
            adjustments["drop"] += 1
            strengths_list.append("전위에서 부드러운 손목 각도로 구석 닉(Nick)을 찌르는 드롭샷이 결정적이었습니다.")
        if any(w in memo for w in ["틴", "범실", "높", "아쉬", "걸림"]):
            adjustments["drop"] = max(-1, adjustments["drop"] - 1)
            improvements_list.append("무리한 프론트 드롭 시도 시 틴(Tin) 범실 위험이 있으므로 완벽한 오픈 찬스에서만 구사하세요.")
            drills_list.append("앞 코너 전위 타깃 맞추기 드롭 정밀 타격 40구 드릴")

    # 보스트 / 3벽 수비 분석
    if any(k in memo for k in ["보스트", "각도", "수비", "탈출", "3벽"]):
        if any(w in memo for w in ["탈출", "좋", "각", "역습", "유효"]):
            adjustments["boast"] += 1
            strengths_list.append("깊숙한 뒷벽 코너에서 사이드 각도를 살린 보스트로 위기 상황을 역전 기회로 전환했습니다.")
        if any(w in memo for w in ["길", "읽", "카운터", "아쉬"]):
            adjustments["boast"] = max(-1, adjustments["boast"] - 1)
            improvements_list.append("보스트 각도가 완만하여 상대에게 오픈 킬샷 찬스를 내주지 않도록 주의해야 합니다.")
            drills_list.append("뒷벽 2바운드 전 사이드 3벽 보스트 각도 제어 30회 훈련")

    # 기본값 보정
    if not strengths_list:
        strengths_list.append(f"{winner} 선수가 세트 후반까지 집중력을 잃지 않고 랠리 템포를 안정적으로 유지했습니다.")
    if not improvements_list:
        improvements_list.append(f"점수 차({diff}점)가 팽팽할 때 체력 저하로 인한 풋워크 지연을 예방하는 페이스 조절이 필요합니다.")
    if not drills_list:
        drills_list.append("기본 렝스 드라이브 4구 후 전위 킬샷으로 마무리하는 2인 컴비네이션 드릴")
        drills_list.append("코트 6점 고스트 풋워크(Ghosting Footwork) 3세트 (각 1분)")

    summary = (
        f"[{player_a} vs {player_b}] {score_a}:{score_b} 경기 분석: "
        f"{winner} 선수가 {diff}점 차로 승리한 경기입니다. "
        f"작성된 경기 메모를 바탕으로 경기 중 나타난 주요 기술적 강점과 훈련 포인트를 도출했습니다."
    )

    return {
        "summary": summary,
        "strengths": " ".join(strengths_list),
        "improvements": " ".join(improvements_list),
        "drills": drills_list[:3],
        "stat_adjustments": adjustments,
        "model_used": "ENTHES Heuristic Rules Engine (Fallback)",
    }


def build_gemini_prompt(player_a: str, player_b: str, score_a: int, score_b: int, memo: str) -> str:
    """스쿼시 전문 AI 코칭을 위한 정밀 프롬프트를 구성합니다."""
    return f"""당신은 공식 스쿼시 리그(ESL)의 공인 수석 코치 AI입니다.
선수들의 경기 점수와 현장 관찰 메모를 바탕으로 전문적이고 따뜻하며 실전 적용 가능한 코칭 리포트를 작성하세요.

[경기 정보]
- 선수 A: {player_a}
- 선수 B: {player_b}
- 최종 스코어: {score_a} : {score_b}
- 현장 관찰 메모: "{memo}"

[작성 가이드라인]
1. summary: 경기의 전체적인 양상과 핵심 흐름을 2~3문장으로 간결하게 요약합니다.
2. strengths: 경기 메모에서 발견된 긍정적 플레이, 전술적 성공 요인, 기술적 장점을 구체적으로 칭찬합니다.
3. improvements: 범실 원인, 전술적 약점, 다음 경기 보완점을 부드럽고 명확한 어조로 조언합니다.
4. drills: 코트에서 2인 또는 혼자서 즉시 수행할 수 있는 실천 훈련 드릴 2~3가지를 추천합니다.
5. stat_adjustments: 경기 메모에 나타난 활약상을 기반으로 6대 스탯(forehand, backhand, volley, drive, drop, boast)의 변동치(-1, 0, +1, +2 중 하나)를 정수로 산출하세요. 지나친 인플레이션을 방지하기 위해 각 항목은 최대 ±2 이내여야 합니다.

[반환 형식]
반드시 유효한 JSON 형식으로만 응답해야 합니다. Markdown 코드 블록(```json 등) 없이 순수 JSON 문자열만 출력하세요:
{{
  "summary": "총평 요약",
  "strengths": "잘한 점 및 강점 분석",
  "improvements": "아쉬운 점 및 보완 전술",
  "drills": ["추천 드릴 1", "추천 드릴 2"],
  "stat_adjustments": {{
    "forehand": 1,
    "backhand": 0,
    "volley": 0,
    "drive": 1,
    "drop": 0,
    "boast": 0
  }}
}}"""


def call_gemini_rest_api(api_key: str, model_name: str, prompt: str) -> dict[str, Any]:
    """urllib를 사용해 Google Gemini REST API를 직접 호출합니다."""
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}"
    payload = {
        "contents": [
            {
                "parts": [
                    {"text": prompt}
                ]
            }
        ],
        "generationConfig": {
            "temperature": 0.3,
            "responseMimeType": "application/json",
        },
    }

    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json; charset=utf-8"},
        method="POST",
    )

    with urllib.request.urlopen(req, timeout=12) as response:
        res_data = json.loads(response.read().decode("utf-8"))

    candidates = res_data.get("candidates", [])
    if not candidates:
        raise ValueError("Gemini API에서 생성된 결과가 없습니다.")

    text_output = candidates[0]["content"]["parts"][0]["text"]
    cleaned_json = re.sub(r"^```(?:json)?\s*", "", text_output.strip(), flags=re.IGNORECASE)
    cleaned_json = re.sub(r"\s*```$", "", cleaned_json)

    parsed = json.loads(cleaned_json)
    parsed["model_used"] = f"Google Gemini ({model_name})"
    return parsed


class handler(BaseHTTPRequestHandler):
    """Vercel Python Serverless Function 요청 처리 핸들러."""

    def _send_json(self, status: int, payload: dict[str, Any]) -> None:
        body = json.dumps(payload, ensure_ascii=False, indent=2).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Cache-Control", "no-store, no-cache, must-revalidate")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self) -> None:  # noqa: N802
        self.send_response(HTTPStatus.NO_CONTENT)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self) -> None:  # noqa: N802
        self._send_json(
            HTTPStatus.OK,
            {
                "status": "online",
                "service": "ENTHES ESL AI Coach API",
                "version": "2026.2.0",
                "method": "POST /api/coach with JSON body",
            },
        )

    def do_POST(self) -> None:  # noqa: N802
        content_length = int(self.headers.get("Content-Length", "0"))
        if content_length <= 0 or content_length > 8192:
            self._send_json(HTTPStatus.BAD_REQUEST, {"error": "요청 본문의 크기가 올바르지 않습니다."})
            return

        try:
            raw_body = self.rfile.read(content_length).decode("utf-8")
            data = json.loads(raw_body)
        except Exception:
            self._send_json(HTTPStatus.BAD_REQUEST, {"error": "JSON 요청 형식을 파싱할 수 없습니다."})
            return

        player_a = clean_text(data.get("player_a"), 40)
        player_b = clean_text(data.get("player_b"), 40)
        memo = clean_text(data.get("memo"), MAX_MEMO_LENGTH)

        try:
            score_a = int(data.get("score_a", 0))
            score_b = int(data.get("score_b", 0))
        except (ValueError, TypeError):
            self._send_json(HTTPStatus.BAD_REQUEST, {"error": "점수는 올바른 숫자 형식이어야 합니다."})
            return

        # 1. 빈 입력 검증 (필수값 누락 체크)
        if not player_a or not player_b:
            self._send_json(HTTPStatus.BAD_REQUEST, {"error": "경기 참가 선수 A와 B를 모두 지정해 주세요."})
            return

        if not memo or len(memo.strip()) < 3:
            self._send_json(HTTPStatus.BAD_REQUEST, {"error": "AI 코칭 분석을 위해 최소 3자 이상의 경기 현장 메모를 입력해 주세요."})
            return

        api_key = os.environ.get("GEMINI_API_KEY", "").strip()
        model_name = os.environ.get("GEMINI_MODEL", "gemini-2.5-flash").strip()

        # 2. API Key 존재 시 Google Gemini 호출 시도, 실패 시 Fallback
        if api_key:
            try:
                prompt = build_gemini_prompt(player_a, player_b, score_a, score_b, memo)
                result = call_gemini_rest_api(api_key, model_name, prompt)
                self._send_json(HTTPStatus.OK, result)
                return
            except urllib.error.HTTPError as http_err:
                if http_err.code in (401, 403):
                    fallback = rule_based_analysis(player_a, player_b, score_a, score_b, memo)
                    fallback["notice"] = "Gemini API 인증 오류로 내장 룰 엔진으로 전환하여 안전하게 분석을 완료했습니다."
                    self._send_json(HTTPStatus.OK, fallback)
                    return
                elif http_err.code == 429:
                    fallback = rule_based_analysis(player_a, player_b, score_a, score_b, memo)
                    fallback["notice"] = "Gemini API 무료 요청 한도 초과로 내장 룰 엔진으로 전환하여 분석했습니다."
                    self._send_json(HTTPStatus.OK, fallback)
                    return
            except Exception:
                pass

        # API Key 미설정 또는 호출 오류 시 로컬 룰 엔진 즉시 제공
        fallback = rule_based_analysis(player_a, player_b, score_a, score_b, memo)
        self._send_json(HTTPStatus.OK, fallback)

    def log_message(self, format: str, *args: Any) -> None:  # noqa: A002
        return
