# 온기록 — AI 회복 루틴 설계소

> **오늘의 에너지를, 오늘의 속도로 정리합니다.**

온기록은 사용자의 현재 상태, 확보한 시간, 원하는 감각을 바탕으로 **오늘 바로 시도할 수 있는 3단계 회복 루틴 초안**을 제안하는 바닐라 웹 서비스입니다. AI가 정답이나 진단을 내리는 대신, 사용자가 자신의 속도에 맞춰 조정할 수 있는 작은 행동을 제시합니다.

| 항목 | 내용 |
|---|---|
| 과제 | AI 활용 학습 A1-3 — AI 웹 서비스 빌딩 |
| 서비스 유형 | AI 기반 일상 웰니스 루틴 제안 웹 서비스 |
| 배포 URL | **배포 후 실제 URL로 교체 필요:** `https://[your-vercel-project].vercel.app` |
| 주요 기능 | 상태·시간·원하는 감각 입력 → AI의 3단계 회복 루틴 결과 출력 |
| 반응형 | 데스크톱, 태블릿, 모바일 레이아웃 지원 |

## 서비스 화면 구성

상단 메뉴를 통해 아래 4개 섹션으로 이동할 수 있습니다.

| 메뉴 | 기능 |
|---|---|
| 첫 장 | 온기록의 목적과 이용 범위 소개 |
| 루틴 설계 | AI 기능의 입력 폼과 생성 결과 표시 |
| 사용 방법 | 입력이 루틴으로 변환되는 과정 설명 |
| 온기록 소개 | 대상 사용자, 서비스 성격, 사용 기술 안내 |

## 기술 스택

| 구분 | 사용 기술 | 역할 |
|---|---|---|
| 프론트엔드 | HTML5 | 시맨틱 화면 구조와 접근성 요소 |
| 프론트엔드 | CSS3 | 반응형 레이아웃, 다크 모드, 애니메이션 |
| 프론트엔드 | Vanilla JavaScript | 폼 검증, `fetch` 요청, 결과 렌더링, 타임아웃 처리 |
| 백엔드 | Python | 입력 검증과 AI API 호출 |
| 서버리스 | Vercel Functions | `/api/recommend` 엔드포인트 실행 |
| AI | Gemini Interactions API | 한국어 3단계 루틴 초안 생성 |

Vercel은 루트의 `api/` 디렉터리에 있는 Python 파일을 파일 기반 함수로 제공할 수 있고, Python의 ASGI·WSGI·`BaseHTTPRequestHandler` 방식을 지원합니다. [1] 본 프로젝트는 단일 POST 엔드포인트에 적합한 `BaseHTTPRequestHandler` 방식을 사용했습니다.

## 프로젝트 구조

```text
AI 활용 학습 A1-3/
├── index.html                 # 화면과 메뉴·폼 구조
├── styles.css                 # 반응형 스타일·다크 모드
├── app.js                     # 입력 검증·AI 요청·결과 표시
├── api/
│   └── recommend.py           # POST /api/recommend Python 함수
├── assets/                    # 서비스용 이미지·로고
├── evidence/                  # 캡처 및 AI 도구 사용 증빙 안내
├── requirements.txt           # openai Python SDK
├── .env.example               # 환경 변수 이름 예시(실제 키 없음)
├── vercel.json                # Vercel 함수·보안 헤더 설정
├── SERVICE_PLAN.md            # 서비스 기획서
├── HOW_IT_WAS_BUILT.md        # 과제 수행 상세 설명
└── REQUIREMENTS_CHECK.md      # 과제 요구사항 확인표
```

## AI 기능 동작 흐름

```text
사용자 입력
  ↓
app.js의 빈 입력 검증
  ↓
fetch('/api/recommend', POST JSON)
  ↓
api/recommend.py의 입력 검증·길이 제한
  ↓
GEMINI_API_KEY 환경 변수로 Gemini Interactions API 호출
  ↓
3단계 루틴 JSON 응답
  ↓
app.js가 안전하게 화면에 결과 렌더링
```

API 키는 **절대로 `app.js`나 `index.html`에 넣지 않습니다.** Gemini 공식 문서는 API 키를 비밀번호처럼 취급하고, Git과 프로덕션 클라이언트 코드에 노출하지 말라고 안내합니다. [2] 이 프로젝트는 `api/recommend.py`가 Vercel 환경 변수에서 키를 읽도록 구현했습니다. 자세한 설정 방법은 [`GEMINI_VERCEL_ENV_GUIDE.md`](./GEMINI_VERCEL_ENV_GUIDE.md)를 참고하세요.

## 로컬 실행 방법

### 1. 저장소 복제 및 과제 폴더 이동

```bash
git clone https://github.com/Starter-Python/Manus.git
cd "Manus/AI 활용 학습 A1-3"
```

### 2. Python 패키지 설치

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 3. 환경 변수 설정

`.env.example`을 참고해 로컬 전용 `.env.local` 파일을 만들되, 이 파일은 Git에 올리지 않습니다.

```bash
cp .env.example .env.local
# .env.local 파일의 GEMINI_API_KEY=... 부분만 실제 키로 변경
```

macOS/Linux의 현재 터미널에서만 임시로 설정하려면 다음처럼 사용할 수 있습니다.

```bash
export GEMINI_API_KEY="실제_Gemini_API_키"
export GEMINI_MODEL="gemini-3.6-flash"  # 선택 사항
```

### 4. Vercel 로컬 개발 서버 실행

정적 HTML만 확인하려면 간단한 로컬 서버를 사용할 수 있지만, `/api/recommend`까지 함께 확인하려면 Vercel 개발 서버를 실행해야 합니다.

```bash
npx vercel dev
```

브라우저에 표시된 로컬 주소를 열고 다음을 확인합니다.

1. 필수 선택값을 비우고 제출했을 때 안내가 나오는지 확인합니다.
2. 상태·시간·원하는 감각을 선택한 뒤 결과가 3단계로 표시되는지 확인합니다.
3. 브라우저 너비를 375px, 768px, 1280px 부근으로 바꿔 메뉴·폼·결과가 읽기 좋은지 확인합니다.

## Vercel 배포 방법

1. [Vercel](https://vercel.com/new)에서 **Add New → Project**를 선택하고 GitHub의 `Starter-Python/Manus` 저장소를 Import합니다.
2. 프로젝트 설정의 **Root Directory**를 `AI 활용 학습 A1-3`로 지정합니다.
3. **Environment Variables**에 아래 값을 추가합니다. Production과 Preview에서 모두 시험하려면 두 환경을 모두 선택합니다.

| 변수명 | 필수 여부 | 설명 |
|---|---:|---|
| `GEMINI_API_KEY` | 필수 | Google AI Studio에서 만든 실제 Gemini API 키. GitHub에 커밋하지 않습니다. |
| `GEMINI_MODEL` | 선택 | 계정에서 사용 가능한 텍스트 생성 모델명. 기본값은 `gemini-3.6-flash`입니다. |

4. **Deploy**를 실행합니다.
5. 배포가 완료되면 생성된 `https://...vercel.app` 주소를 이 README 맨 위의 **배포 URL** 칸에 기록합니다.
6. 실제 URL에서 입력·결과·모바일 화면을 확인하고 `evidence/EVIDENCE_GUIDE.md`의 목록에 따라 캡처합니다.

Vercel 환경 변수는 코드 밖에서 환경별로 관리되며, 값 변경은 이전 배포에 자동 적용되지 않으므로 변경 뒤 새 배포가 필요합니다. [3]

## AI 기능의 실패 처리

| 상황 | 사용자에게 보이는 안내 |
|---|---|
| 필수 입력 누락 | “현재 상태, 시간, 원하는 감각을 모두 골라주세요.” |
| 요청 지연(12초) | “응답이 조금 늦어지고 있습니다. 잠시 후 다시 시도해 주세요.” |
| Gemini 키 미설정 | “AI 기능 설정이 아직 완료되지 않았습니다.” |
| 요청 과다(429) | “Gemini 무료 사용량 또는 요청 한도에 도달했습니다.” |
| AI 연결·응답 오류 | 원인을 노출하지 않고 재시도 가능한 안내를 표시 |

## 제출 문서와 증빙

| 문서/폴더 | 내용 |
|---|---|
| [`SERVICE_PLAN.md`](./SERVICE_PLAN.md) | 서비스 목적, 타겟, 페이지 구성, AI 입출력과 실패 처리 |
| [`HOW_IT_WAS_BUILT.md`](./HOW_IT_WAS_BUILT.md) | HTML/CSS/JS/Python/Vercel 구조를 이해하기 위한 상세 수행 기록 |
| [`REQUIREMENTS_CHECK.md`](./REQUIREMENTS_CHECK.md) | 과제 요구사항별 충족 여부와 배포 후 할 일 |
| [`evidence/`](./evidence/) | 실제 Vercel URL 캡처와 AI 코딩 도구 사용 과정 기록 안내 |

## 주의 사항

온기록은 일상 웰니스 루틴을 제안하는 도구이며 의료적 진단, 치료, 응급 지원을 대신하지 않습니다. 위기 상황이나 자신 또는 타인의 안전이 걱정되는 경우에는 주변의 신뢰할 수 있는 사람, 지역의 응급 서비스, 전문 도움에 즉시 연락해야 합니다.

## 참고 자료

[1]: https://vercel.com/docs/functions/runtimes/python/api-directory "Vercel — Python Functions in the /api Directory"
[2]: https://ai.google.dev/gemini-api/docs/api-key "Google AI for Developers — Using Gemini API keys"
[3]: https://vercel.com/docs/environment-variables "Vercel — Environment variables"
