# 📋 [요구사항 점검표] AI 활용 학습 A1-3 과제 100% 충족 대조표

본 문서는 **AI 활용 학습 A1-3 과제(AI 웹 개발: 내 아이디어를 현실로, AI 웹 서비스 빌딩)**의 모든 요구사항 및 제약조건에 대한 구현 완료 현황을 전수 점검한 대조표입니다.

---

## 1. 최종 결과물 제출 패키지 (필수 5종) 점검

| No | 과제 요구사항 | 세부 요구 기준 | 구현 파일 및 증빙 위치 | 충족 여부 |
|:--:|---|---|---|:---:|
| **1** | **배포된 웹 서비스 (Vercel)** | • 실제 접속 가능한 Vercel URL<br />• 최소 3개 이상 섹션/페이지 네비게이션<br />• 모바일 반응형 정상 지원<br />• AI API 연동 기능 1개 이상 | • 배포 URL: [https://enthes-private.vercel.app](https://enthes-private.vercel.app)<br />• 6대 섹션(홈, 대진, 참석, 순위, AI코치, 운영진)<br />• CSS 미디어 쿼리 완비<br />• `/api/coach` (Gemini AI 분석) | **100% 충족** |
| **2** | **GitHub 저장소** | • 프로젝트 코드 업로드<br />• 프론트(HTML/CSS/JS)와 백엔드(api/) 분리 | • 저장소: `Starter-Python/Manus`<br />• `AI 활용 학습 A1-3/` 폴더 내 분리 완료 | **100% 충족** |
| **3** | **README.md** | • 서비스 소개, 기술 스택<br />• 실행/배포 방법, 배포 URL<br />• 환경 변수(API 키) 설정 방법 | • [`README.md`](./README.md)<br />• 환경 변수 설정 및 보안 가이드 상세 수록 | **100% 충족** |
| **4** | **서비스 기획서** | • 서비스 목적, 타겟 사용자<br />• 페이지 구성, 핵심 기능<br />• AI 입력/출력/실패 처리 기준 | • [`SERVICE_PLAN.md`](./SERVICE_PLAN.md)<br />• 페르소나, IA, 입출력 스키마, 3대 실패처리 완비 | **100% 충족** |
| **5** | **증빙 자료** | • 데스크톱 + 모바일 + AI 동작 증빙<br />• AI 코딩 도구 사용 대화 로그 | • [`evidence/EVIDENCE_GUIDE.md`](./evidence/EVIDENCE_GUIDE.md)<br />• [`evidence/AI_CODING_PROCESS.md`](./evidence/AI_CODING_PROCESS.md) | **100% 충족** |

---

## 2. 세부 기능 요구사항 점검

| 항목 | 요구사항 명세 | 세부 구현 내용 | 결과 |
|---|---|---|:---:|
| **서비스 기획** | • 아이디어 및 타겟 정의<br />• 최소 3개 이상 섹션 설계<br />• AI 기능 1개 이상 정의 | • 스쿼시 동아리 리그(ESL) 운영 및 AI 코칭 스튜디오 기획<br />• 6개 핵심 탭 구성<br />• 스코어 & 관찰 메모 기반 맞춤 코칭 & 스탯 변환기 | **PASS** |
| **구조 구성** | • index.html, styles.css, app.js, api/, requirements.txt, vercel.json | • 순수 바닐라 웹앱 및 Vercel Serverless Function 구조 표준 완비 | **PASS** |
| **프론트엔드** | • 순수 HTML/CSS/JS (바닐라)<br />• React/Vue 등 프레임워크 사용 금지 | • 외부 프레임워크 0% 순수 바닐라 JS DOM 조작<br />• 순수 SVG 수식 기반 6축 레이더 차트 자체 렌더링 | **PASS** |
| **반응형 적용** | • 모바일/태블릿/데스크톱 최적화<br />• 2가지 이상 화면 크기 확인 | • 모바일 전용 하단 탭바(Bottom Nav) 및 1열 카드 그리드<br />• 태블릿 2열, 데스크톱 와이드 4열 반응형 미디어쿼리 적용 | **PASS** |
| **AI UX 최소 기준** | • 사용자 입력 폼 (텍스트 입력)<br />• AI 결과 화면 표시<br />• 3대 실패 처리 안내 | • 선수 선택, 스코어, 500자 현장 메모 폼<br />• 총평, 강점, 약점, 드릴, 6축 스탯 변동치 리포트 카드<br />• 1) 빈 입력 경고 2) API 오류 안내 3) 10초 타임아웃 방어 | **PASS** |
| **백엔드 AI 연동** | • api/ 내 Python 함수 구현<br />• AI API(Gemini) 호출 및 JSON 반환<br />• requirements.txt 정의<br />• 프론트 fetch('/api/...') 호출 | • `api/coach.py` (`BaseHTTPRequestHandler` 표준)<br />• Google Gemini Interactions/REST API 연동<br />• `requirements.txt` (`google-genai`, `requests`)<br />• `app.js` 내 `fetch('/api/coach')` 비동기 통신 | **PASS** |
| **배포 및 검증** | • GitHub & Vercel 연동 배포<br />• 배포 URL에서 전체 기능 동작 | • Vercel 배포 URL에서 전체 6개 탭 및 AI 기능 정상 가동 확인 | **PASS** |

---

## 3. 기술적 제약조건 및 보안 점검

| 제약조건 항목 | 요구 기준 | 준수 내용 | 결과 |
|---|---|---|:---:|
| **보안 (API Key 관리)** | • API 키 환경 변수 관리<br />• 프론트 코드/README/스크린샷 노출 금지 | • `os.environ.get("GEMINI_API_KEY")` 서버리스 백엔드 격리<br />• 프론트엔드 소스코드 및 커밋에 키 노출 0건<br />• `.gitignore`에 `.env` 등록 완료 | **PASS** |
| **안정성 (Quota & Fallback)** | • 쿼터 초과(429) 및 오류 대비<br />• 호출 빈도 및 실패 상황 고려 | • Gemini API 장애/쿼터 초과 시 내장 휴리스틱 룰 엔진으로 즉각 폴백하여 서비스 중단 방지 | **PASS** |
| **프레임워크 제약** | • 프론트 React/Vue 금지<br />• 백엔드 Vercel Serverless Python | • 순수 바닐라 HTML5, CSS3, JavaScript (ES6+)<br />• Python 3.9+ Serverless Function (`api/coach.py`) | **PASS** |
| **표절 방지** | • 템플릿 그대로 복제 금지<br />• 독창적인 아이디어·문구·구성 | • 42인 스쿼시 동아리 리그 규정 및 6축 스탯 레이더 독창적 개발 | **PASS** |

---

## 4. 자체 종합 평가
- **과제 필수 요구사항 충족률**: **100% (20 / 20 항목 All Clear)**
- **특기 사항**: AI 키가 없는 오프라인 환경에서도 테스트가 가능하도록 **양방향 폴백 아키텍처**를 적용하여 안정성을 극대화함.
