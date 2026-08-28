# 과제 수행 과정 — 온기록을 만든 방법

이 문서는 A1-3 과제를 수행하면서 **무엇을 만들었는지**뿐 아니라, HTML·CSS·JavaScript·Python·Vercel이 서로 어떻게 연결되는지를 학습자가 직접 설명할 수 있도록 정리한 기록이다.

## 1. 아이디어를 기능으로 좁히기

처음에는 ‘AI가 감정을 분석해 주는 서비스’라는 넓은 아이디어에서 출발했다. 그러나 감정 분석은 사용자가 결과를 진단처럼 받아들일 위험이 있고, 결과가 막연하면 당장 행동으로 옮기기 어렵다. 그래서 서비스 범위를 **“오늘의 상태와 시간을 받아 3단계 회복 루틴을 제안하는 도구”**로 줄였다. 이 선택 덕분에 입력·출력·실패 처리 기준을 명확하게 정할 수 있었다.

| 기획 질문 | 결정 | 이유 |
|---|---|---|
| 누가 쓰는가? | 잠시 쉬고 싶지만 어떻게 쉴지 정하기 어려운 학습자·직장인 | 구체적인 사용 상황을 기준으로 화면 문구를 정할 수 있다. |
| 무엇을 입력받는가? | 상태, 5/15/30분, 원하는 감각, 선택 메모 | AI가 결과를 개인화할 수 있으면서도 입력 부담이 낮다. |
| 무엇을 돌려주는가? | 제목, 짧은 안내, 3단계 행동, 조정 안내 | 사용자가 결과를 한 번에 읽고 바로 시도할 수 있다. |
| 어떻게 안전하게 표현하는가? | “정답” 대신 “초안”, 의료 진단 아님을 명시 | 서비스의 범위와 한계를 정직하게 전달한다. |

## 2. 폴더 구조를 먼저 만든 이유

프로젝트를 시작할 때 기능보다 먼저 파일의 역할을 분리했다. 이렇게 해 두면 화면 디자인을 수정할 때 Python API를 건드릴 필요가 없고, 배포할 때 비밀 키가 들어갈 위치도 명확해진다.

```text
AI 활용 학습 A1-3/
├── index.html                 # 화면의 뼈대와 텍스트
├── styles.css                 # 색, 간격, 반응형, 애니메이션
├── app.js                     # 폼 검증, fetch 요청, 결과 렌더링
├── api/
│   └── recommend.py           # Vercel Python Serverless Function
├── assets/                    # 로고와 서비스 이미지
├── evidence/                  # 스크린샷·AI 도구 사용 증빙 안내
├── requirements.txt           # Python 패키지 목록
├── vercel.json                # Vercel 함수 및 보안 헤더 설정
├── .env.example               # 실제 키 없는 환경 변수 예시
├── README.md                  # 실행·배포 안내
├── GEMINI_VERCEL_ENV_GUIDE.md # Gemini 키와 Vercel 환경 변수 안내
├── SERVICE_PLAN.md            # 서비스 기획서
├── HOW_IT_WAS_BUILT.md        # 이 문서
└── REQUIREMENTS_CHECK.md      # 요구사항 확인표
```

> **핵심 구분:** HTML은 “무엇을 보여 줄지”, CSS는 “어떻게 보일지”, JavaScript는 “사용자 행동에 어떻게 반응할지”를 맡는다. Python은 브라우저 밖에서 AI API를 안전하게 호출하는 역할을 맡는다.

## 3. 프론트엔드를 바닐라 HTML/CSS/JavaScript로 구현한 방법

### 3.1 HTML: 의미 있는 화면 구조 만들기

`index.html`은 4개의 메뉴 이동 가능한 섹션을 가진다. `header`에는 서비스 로고와 메뉴를, `main`에는 첫 장·루틴 설계·사용 방법·소개를, `footer`에는 서비스 범위 안내를 배치했다. AI 기능 폼에는 `label`, `select`, `textarea`, `button`을 연결해 키보드와 보조 기술에서도 입력 항목의 의미를 알 수 있게 했다.

`aria-live="polite"`가 적용된 결과 패널과 오류 메시지 영역은 화면을 보지 못하는 사용자에게도 결과 변화가 전달되도록 돕는다. ‘본문으로 건너뛰기’ 링크와 명확한 포커스 처리도 함께 넣었다.

### 3.2 CSS: 반응형 화면과 시각적 일관성 만들기

`styles.css`는 따뜻한 미색·먹빛·이끼 녹색을 변수로 정의했다. 데스크톱에서는 세로 인덱스와 넓은 여백이 있는 비대칭 편집 레이아웃을 사용하고, 화면 폭이 900px 아래가 되면 메뉴와 컬럼을 단순화한다. 560px 아래에서는 세로 인덱스를 숨기고 한 줄 레이아웃으로 바꾼다.

| 화면 크기 | 적용 방식 | 확인 포인트 |
|---|---|---|
| 데스크톱(1280px 기준) | 좌측 인덱스 + 콘텐츠 + 이미지/결과 패널의 비대칭 구성 | 메뉴, 폼과 결과가 나란히 보이는지 |
| 태블릿(약 768px) | 메뉴를 접고, 결과 패널을 폼 아래로 이동 | 선택 버튼이 줄바꿈되어도 눌리는지 |
| 모바일(375px 기준) | 단일 열, 짧은 여백, 접힘 메뉴 | 글자가 겹치지 않고 버튼을 누르기 쉬운지 |

CSS에서 `@media (prefers-reduced-motion: reduce)`를 추가해 운영체제에서 모션 감소를 선택한 사용자에게는 진입 애니메이션을 줄인다. 다크 모드는 CSS 변수만 바꾸므로 HTML 구조를 복제하지 않고도 화면 대비를 유지한다.

### 3.3 JavaScript: 입력 → 요청 → 화면 반영 흐름 만들기

`app.js`의 핵심은 폼 제출 이벤트다. 사용자가 버튼을 누르면 `FormData`로 값을 모으고, 필수값이 비어 있으면 API를 부르지 않고 즉시 안내한다. 값이 정상일 때만 `fetch('/api/recommend')`가 JSON `POST` 요청을 보낸다. 12초 안에 응답이 없으면 `AbortController`가 요청을 중단하고, 사용자에게 지연 안내를 보여 준다.

```js
const response = await fetch('/api/recommend', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify(values),
  signal: controller.signal,
});
```

응답이 성공하면 `showResult()`가 제목·안내·세 단계의 문자열을 `textContent`로 화면에 삽입한다. `innerHTML`로 사용자가 입력한 내용을 바로 넣지 않고 `textContent`를 쓰는 이유는 의도하지 않은 HTML 실행을 피하기 위해서다. 실패하면 HTTP 상태 또는 타임아웃을 구분해 사용자가 다시 시도할 행동을 알 수 있게 한다.

## 4. Python 서버리스 API를 만든 방법

### 4.1 왜 브라우저가 아니라 Python에서 AI API를 호출하는가

Gemini API 키는 비밀 정보다. 공식 문서는 키를 브라우저나 앱 같은 클라이언트 코드에 노출하지 말고 서버의 환경 변수나 키 관리 서비스에서 읽으라고 안내한다. [1] 따라서 `app.js`에는 키가 없고, `api/recommend.py`가 `GEMINI_API_KEY` 환경 변수를 읽는다.

Vercel은 루트의 `api/` 안에 있는 Python 파일을 파일 기반 함수로 매핑할 수 있으며, ASGI·WSGI 앱 또는 `BaseHTTPRequestHandler` 기반 핸들러를 지원한다. [2] 온기록은 한 개의 단순한 POST 엔드포인트만 필요하므로 표준 라이브러리의 `BaseHTTPRequestHandler`를 사용했다. `/api/recommend` 경로는 `api/recommend.py` 파일에 연결된다.

### 4.2 API 내부의 처리 순서

1. `Content-Length`를 확인하여 비어 있거나 4KB를 넘는 요청을 거절한다.
2. JSON을 읽고 상태·시간·원하는 감각을 검사한다. 시간은 5/15/30분만 허용한다.
3. 메모는 제어 문자를 제거하고 200자로 제한한다.
4. `GEMINI_API_KEY`가 설정되어 있는지 확인한다. 없으면 서비스 설정 안내를 반환한다.
5. 공식 Gemini Python SDK의 `client.interactions.create()`로 AI에게 루틴 생성 요청을 보낸다. Gemini 공식 시작 문서는 `google-genai` SDK와 환경 변수 사용법을 안내한다. [3]
6. 모델 결과에서 JSON 객체를 파싱하고, 단계가 정확히 3개인지 다시 검사한다.
7. 성공·인증 실패·요청 과다·연결 실패·형식 오류를 다른 HTTP 상태와 한국어 안내 문구로 반환한다.

### 4.3 프롬프트에 넣은 안전 기준

프롬프트는 AI에게 의료적 진단, 치료, 약물 조언을 하지 말라고 명시한다. 또한 위기·자해·타해가 언급되면 일반적인 루틴을 제안하는 대신 주변 사람, 지역의 응급 서비스, 전문 도움을 찾도록 안내하도록 제한한다. 이는 웰니스 서비스가 자신의 범위를 넘지 않기 위한 설계다.

## 5. 환경 변수와 배포를 준비한 방법

실제 키는 `.env.example`이 아닌 Vercel 프로젝트 설정에만 입력한다. `.env.example`은 변수 이름을 알려 주는 예시이고, `.gitignore`는 `.env`, `.env.local` 등이 Git에 올라가지 않게 막는다. Vercel 환경 변수는 코드 밖에서 설정되며, 배포 환경별로 값이 달라질 수 있다. [4] 구체적인 화면 경로와 키 보안 원칙은 [`GEMINI_VERCEL_ENV_GUIDE.md`](./GEMINI_VERCEL_ENV_GUIDE.md)에 정리했다.

배포할 때는 GitHub 저장소를 Vercel에 Import하고, **Root Directory를 `AI 활용 학습 A1-3`**로 지정한다. 그다음 `GEMINI_API_KEY`와 선택적인 `GEMINI_MODEL`을 Production·Preview·Development 중 필요한 환경에 설정한다. 값 변경은 이전 배포에 적용되지 않으므로, 변경 후 새 배포가 필요하다. [4]

## 6. 오류를 발견했을 때의 점검 순서

AI 코딩 도구를 사용해 코드를 만들더라도, 오류를 ‘도구가 고쳐 주는 문제’로만 보면 안 된다. 아래 순서로 원인을 좁힌다.

| 증상 | 먼저 확인할 곳 | 예상 원인 | 수정 방향 |
|---|---|---|---|
| 버튼을 눌러도 아무 반응이 없음 | 브라우저 개발자 도구 Console | JavaScript 문법 오류 또는 파일 경로 오류 | 오류 줄을 확인하고 `app.js` 연결·문법 점검 |
| 400 오류 | Network 탭의 요청 본문 | 필수값 누락·허용하지 않은 시간값 | 폼의 `name`과 서버 검증 조건을 비교 |
| 503 ‘설정 미완료’ | Vercel Environment Variables | `GEMINI_API_KEY` 미설정 | 키를 환경 변수로 추가하고 재배포 |
| 429 오류 | API 응답 상태 | Gemini Free Tier 사용량 또는 요청 한도 | 잠시 기다린 뒤 재시도, AI Studio Usage 확인 |
| 502 오류 | Vercel Function Logs | Gemini 연결·응답 형식 문제 | 네트워크 상태·모델명·응답 파싱 점검 |
| 배포에서만 실패 | Vercel Deployment Logs | 루트 디렉터리·패키지·환경 변수 차이 | 로컬과 Vercel 설정을 한 항목씩 비교 |

## 7. 직접 확인해야 하는 최종 흐름

배포 전에는 데스크톱과 모바일 너비에서 메뉴·폼·결과 패널을 확인한다. 배포 뒤에는 실제 URL에서 필수 입력 누락 메시지, 정상 AI 결과, 네트워크 또는 API 실패 메시지를 각각 확인한다. 수정이 필요하면 원인을 문장으로 정리하고 코드를 고친 뒤 GitHub에 푸시하면 Vercel이 새 배포를 만든다. 이 흐름이 **로컬 확인 → 배포 확인 → 원인 파악 → 수정 → 재배포**의 기본 반복이다.

## 참고 자료

[1]: https://ai.google.dev/gemini-api/docs/api-key "Google AI for Developers — Using Gemini API keys"
[2]: https://vercel.com/docs/functions/runtimes/python/api-directory "Vercel — Python Functions in the /api Directory"
[3]: https://ai.google.dev/gemini-api/docs/get-started "Google AI for Developers — Gemini API get started"
[4]: https://vercel.com/docs/environment-variables "Vercel — Environment variables"
