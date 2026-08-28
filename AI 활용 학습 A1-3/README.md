# 🎾 ENTHES — 공식 스쿼시 리그 (ESL) & AI 코칭 스튜디오

> **과제명**: AI 활용 학습 A1-3 — AI 웹 서비스 빌딩  
> **배포 URL**: [https://enthes-private.vercel.app](https://enthes-private.vercel.app)  
> **기술 스택**: 순수 바닐라 HTML5 / CSS3 / JavaScript (ES6+) + Vercel Serverless Functions (Python 3.9+) + Google Gemini AI  
> **GitHub 저장소**: `Starter-Python/Manus` (`AI 활용 학습 A1-3` 폴더)

---

## 📌 1. 서비스 소개 (Overview)

**ENTHES(Enjoy The Squash)**는 스쿼시 동아리의 정규 리그(ESL: ENTHES Squash League)를 운영하고, 경기 결과 및 현장 관찰 메모를 바탕으로 맞춤형 피드백을 생성하는 **AI 경기 분석 & 코칭 웹 서비스**입니다.

### 🌟 핵심 가치
1. **스마트 자동 대진 & 핸디캡 계산**: 42인 3개 리그(1부·2부·3부) 엄격 격리, 티어 차이당 2점 어드밴티지, 하위 티어 우선 서브권, 자율 심판 2인 자동 배정.
2. **6축 역량 스탯 레이더 (6-Axis Radar)**: 포핸드·백핸드·발리·드라이브·드롭·보스트 6대 지표를 순수 SVG 차트로 시각화.
3. **Gemini AI 경기 코칭 파이프라인**: 경기 점수와 현장 메모 한 줄을 입력하면 **총평, 전술 강점, 보완 조언, 맞춤 드릴, 6대 스탯 변동치(+1~3점 가드레일)**를 실시간 도출.
4. **1초 비상 롤백 및 데이터 불변성**: 실수로 인한 데이터 손실을 원천 차단하는 1초 Undo 롤백 시스템과 JSON 백업/복원 지원.

---

## 🛠️ 2. 기술 스택 & 시스템 구조

```
[ Frontend (Vanilla) ]             [ Backend (Serverless) ]            [ External AI ]
┌───────────────────────────┐      ┌─────────────────────────────┐     ┌───────────────────────┐
│ index.html (Semantic HTML)│ ───► │ api/coach.py                │ ──► │ Google Gemini API     │
│ styles.css (Modern CSS3)  │      │ (BaseHTTPRequestHandler)    │     │ (gemini-2.5-flash)    │
│ app.js (Pure Vanilla JS)  │ ◄─── │ (Urllib / REST Protocol)    │ ◄── │                       │
└───────────────────────────┘      └─────────────────────────────┘     └───────────────────────┘
  • 6개 독립 탭 네비게이션             • 환경 변수(GEMINI_API_KEY) 격리        • 구조화된 JSON 응답
  • 순수 SVG 레이더 차트 엔진           • 3단계 에러 & 내장 룰 엔진 Fallback      • 인플레이션 방지 가드레일
  • localStorage 영구 저장            • 무결성 검증 및 제어문자 정제
```

- **프론트엔드**: 순수 바닐라 HTML5, CSS3, JavaScript (ES6+), React/Vue 등 프레임워크 배제
- **백엔드**: Vercel Serverless Functions (`api/coach.py`, Python 3.9+)
- **AI 엔진**: Google Gemini Interactions API / REST (`gemini-2.5-flash` / `gemini-1.5-flash`)
- **보안**: `GEMINI_API_KEY` 환경 변수 완전 은닉 (프론트엔드 및 깃허브 코드 노출 0%)

---

## 📂 3. 디렉터리 구성

```text
AI 활용 학습 A1-3/
├── api/
│   └── coach.py               # Vercel Python Serverless Function (POST /api/coach)
├── evidence/                  # 과제 증빙 패키지
│   ├── AI_CODING_PROCESS.md   # AI 코딩 도구 활용 대화 내역 및 프롬프트 과정
│   └── EVIDENCE_GUIDE.md      # 데스크톱/모바일 반응형 및 AI 동작 증빙 가이드
├── assets/                    # 정적 에셋 폴더
├── .env.example               # 환경 변수 템플릿
├── .gitignore                 # 보안 및 임시 파일 제외 규칙
├── GEMINI_VERCEL_ENV_GUIDE.md # Vercel 환경 변수 등록 및 운영 매뉴얼
├── HOW_IT_WAS_BUILT.md        # 아키텍처 및 빌드 스토리
├── index.html                 # 순수 HTML5 메인 웹앱
├── package.json               # 프로젝트 설정 메타데이터
├── README.md                  # 본 문서
├── REQUIREMENTS_CHECK.md      # A1-3 과제 요구사항 100% 충족 대조표
├── requirements.txt           # Vercel Python 의존성 목록
├── SERVICE_PLAN.md            # 공식 서비스 기획서
├── styles.css                 # 순수 CSS3 반응형 스타일시트
├── app.js                     # 순수 바닐라 JS 상태 및 AI 연동 스크립트
└── vercel.json                # Vercel 배포 및 라우팅 설정
```

---

## 🚀 4. 로컬 실행 및 테스트 방법

### 1) 정적 웹서버 실행 (프론트엔드)
별도의 빌드 과정 없이 정적 웹 서버나 브라우저 더블클릭으로 즉시 실행 가능합니다:

```bash
# Python 내장 웹서버로 실행 (권장)
cd "Manus/AI 활용 학습 A1-3"
python3 -m http.server 3000
```
브라우저에서 `http://localhost:3000` 접속

### 2) 백엔드 파이썬 서버리스 단독 검증
```bash
python3 -c "
import sys; sys.path.insert(0, './api')
import coach
res = coach.rule_based_analysis('조재경', '문찬영', 15, 12, '포핸드 드라이브 깊고 백핸드 안정적')
print(res['summary'])
"
```

---

## ☁️ 5. Vercel 배포 및 환경 변수 설정

### 1) Vercel 배포 단계
1. [Vercel Dashboard](https://vercel.com/dashboard) ➔ `Add New Project` 클릭
2. GitHub 저장소 `Starter-Python/Manus` Import
3. **Root Directory**를 `AI 활용 학습 A1-3`로 지정
4. `Deploy` 버튼 클릭

### 2) 환경 변수 (Environment Variables) 등록
Vercel 프로젝트 대시보드 ➔ **Settings** ➔ **Environment Variables**에서 다음 키를 추가합니다:

| 환경 변수명 | 권장 값 | 설명 |
|---|---|---|
| `GEMINI_API_KEY` | `AIzaSy...` (본인 발급 키) | [Google AI Studio](https://aistudio.google.com/app/apikey)에서 발급한 API 키 |
| `GEMINI_MODEL` | `gemini-2.5-flash` | 사용할 Gemini 모델명 (기본값) |

> 🔒 **보안 안내**: API 키는 서버리스 백엔드(`api/coach.py`)에서만 호출되며 프론트엔드 브라우저나 소스코드에는 일체 노출되지 않습니다.

---

## 🧪 6. AI 기능 UX 최소 기준 충족 검증

| 항목 | 구현 내용 | 정상 동작 확인 |
|---|---|:---:|
| **사용자 입력 UI** | 선수 A, 선수 B, 세트 스코어, 현장 관찰 메모(자유 서술형 텍스트) 입력 폼 제공 | ✅ PASS |
| **AI 결과 화면 표시** | 종합 총평, 전술 강점, 보완 조언, 추천 드릴 2~3종, 6대 스탯 변동량 시각화 | ✅ PASS |
| **빈 입력 처리** | 선수 미선택 또는 메모 3자 미만 입력 시 친절한 유효성 검사 경고 배너 출력 | ✅ PASS |
| **API/서버 오류 방어** | API 키 미설정 또는 Gemini 장애 시 내장 휴리스틱 룰 엔진으로 100% 정상 폴백 | ✅ PASS |
| **지연/타임아웃 방어** | 10초 `AbortSignal.timeout` 가드레일 적용 및 사용자 안내 피드백 | ✅ PASS |

---

## 📄 7. 과제 제출 패키지 5종 완비 내역

1. **배포된 웹 서비스**: [https://enthes-private.vercel.app](https://enthes-private.vercel.app)
2. **GitHub 저장소**: `Starter-Python/Manus/AI 활용 학습 A1-3`
3. **README.md**: 본 문서 ([README.md](./README.md))
4. **서비스 기획서**: [`SERVICE_PLAN.md`](./SERVICE_PLAN.md)
5. **증빙 자료**: [`evidence/AI_CODING_PROCESS.md`](./evidence/AI_CODING_PROCESS.md), [`evidence/EVIDENCE_GUIDE.md`](./evidence/EVIDENCE_GUIDE.md)
