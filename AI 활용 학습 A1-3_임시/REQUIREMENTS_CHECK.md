# A1-3 요구사항 확인표

이 문서는 과제 안내문에 제시된 필수 조건을 파일·기능·직접 확인 항목으로 나누어 점검한 결과다. **코드와 문서로 확인 가능한 조건**과, 계정·실제 키가 필요해 사용자가 배포 후 확인해야 하는 조건을 구분했다.

## 1. 제출 패키지 5종

| 제출물 | 요구사항 | 구현/저장 위치 | 상태 | 확인 방법 |
|---|---|---|---|---|
| 배포된 웹 서비스 | Vercel URL, 3개 이상 페이지/섹션, 반응형, AI 입력→출력 | `index.html`, `styles.css`, `app.js`, `api/recommend.py` | **배포 전** | Vercel Import 및 환경 변수 설정 후 URL 기록 필요 |
| GitHub 저장소 | 코드 업로드, 프론트·백엔드 구조 분리 | `index.html`·`styles.css`·`app.js` / `api/recommend.py` | **충족** | `Manus` 저장소의 `AI 활용 학습 A1-3` 폴더 확인 |
| README.md | 소개, 기술 스택, 실행·배포, URL, 환경 변수 | `README.md` | **충족** | 문서 목차 확인 |
| 서비스 기획서 | 목적, 타겟, 페이지 구성, 핵심 기능, AI 입출력·실패 처리 | `SERVICE_PLAN.md` | **충족** | 기획서 1~3장 확인 |
| 증빙 자료 | 데스크톱·모바일·AI 동작 스크린샷, AI 코딩 도구 사용 과정 | `evidence/` | **배포 후 최종 확인 필요** | `EVIDENCE_GUIDE.md`에 따라 실제 화면을 캡처해 추가 |

## 2. 기능 요구사항

| 번호 | 요구사항 | 구현 내용 | 근거 파일 | 상태 |
|---:|---|---|---|---|
| 1 | 서비스 아이디어·목적·타겟 정의 | AI 회복 루틴 초안 서비스와 사용자 문제 정의 | `SERVICE_PLAN.md` | **충족** |
| 1 | 3개 이상 페이지/섹션 및 메뉴 이동 | 첫 장, 루틴 설계, 사용 방법, 온기록 소개의 4개 섹션과 상단 메뉴 | `index.html` | **충족** |
| 1 | AI 기능의 입력·출력·가치 정의 | 상태·시간·감각·메모 입력 → 3단계 루틴 출력 | `SERVICE_PLAN.md`, `api/recommend.py` | **충족** |
| 2 | 기본 프로젝트 구조 구성 | HTML/CSS/JS, `api/`, `assets/`, `evidence/`, `requirements.txt` | 프로젝트 파일 구조 | **충족** |
| 2 | GitHub 저장소·커밋 이력 | 기존 `Manus` 저장소의 지정 폴더에 커밋 예정 | Git 커밋 기록 | **반영 단계** |
| 3 | 바닐라 프론트엔드 구현 | React/Vue 없이 HTML/CSS/JavaScript 사용 | `index.html`, `styles.css`, `app.js` | **충족** |
| 3 | 네비게이션·기본 레이아웃·스타일 | 앵커 메뉴, 접힘 모바일 메뉴, 편집형 레이아웃 | `index.html`, `styles.css`, `app.js` | **충족** |
| 4 | 반응형 적용 | 900px·560px 미디어 쿼리 및 모바일 메뉴 | `styles.css` | **구현 완료 / 실제 기기 확인 필요** |
| 5 | 입력 UI 제공 | select, radio, textarea 폼 | `index.html` | **충족** |
| 5 | AI 결과 표시 | 결과 제목·안내·3단계·메모를 DOM에 표시 | `app.js` | **충족** |
| 5 | 실패 처리 1개 이상 | 빈 입력, 4xx/5xx, 429, 연결 오류, 12초 지연 처리 | `app.js`, `api/recommend.py` | **충족** |
| 6 | `api/` Python 엔드포인트 | `POST /api/recommend` Vercel Python 함수 | `api/recommend.py` | **충족** |
| 6 | AI API 호출과 결과 반환 | Gemini Interactions API 호출, JSON 파싱·반환 | `api/recommend.py` | **코드 구현 완료 / 키 설정 후 실동작 확인 필요** |
| 6 | `requirements.txt` | Gemini Python SDK 선언 | `requirements.txt` | **충족** |
| 6 | 프론트에서 `fetch('/api/...')` 호출 | `fetch('/api/recommend')` POST 요청 | `app.js` | **충족** |
| 7 | GitHub와 Vercel 연결·배포 | Vercel 설정 파일·배포 절차 준비 | `vercel.json`, `README.md` | **사용자 계정 작업 필요** |
| 7 | 배포 URL에서 전체 기능 검증 | 검증 절차 문서화 | `README.md`, `EVIDENCE_GUIDE.md` | **배포 후 확인 필요** |
| 8 | README 정리 | 소개, 스택, URL 표기, 실행, 환경 변수 포함 | `README.md` | **충족** |
| 8 | 스크린샷·AI 도구 증빙 준비 | 캡처 목록과 대화 기록 문서 작성 | `evidence/EVIDENCE_GUIDE.md`, `evidence/AI_CODING_PROCESS.md` | **준비 완료 / 실제 URL 캡처 필요** |
| 8 | 서비스 기획서 포함 | 기획서 작성 | `SERVICE_PLAN.md` | **충족** |

## 3. 제약 사항 및 보안 점검

| 제약 사항 | 점검 결과 | 근거 |
|---|---|---|
| 프론트는 순수 HTML/CSS/JS | **충족** | 프레임워크 의존성·빌드 도구 없이 정적 파일로 작성 |
| 백엔드는 Vercel Python Serverless Function | **충족** | `api/recommend.py`의 `BaseHTTPRequestHandler` 기반 함수 |
| API 키를 코드·문서·스크린샷에 노출하지 않음 | **충족** | 실제 키 없음, `.env.example`은 플레이스홀더, `.gitignore` 설정 |
| 템플릿 복제 금지 | **충족** | ‘온기록’ 서비스 기획·문구·편집형 디자인을 독자적으로 구성 |
| AI API 과금·쿼터 고려 | **충족** | 입력 길이 제한, 10초 API 타임아웃, 1회 재시도, 429 안내 |

## 4. 최종 결론

과제의 **설계·코드·문서·보안·실패 처리 요건은 구현했다.** 다만 실제 Vercel 배포 URL, 실제 API 키로 만든 동작 화면, 배포된 모바일 화면은 외부 계정 및 비밀 키가 필요한 마지막 단계이므로 아직 검증할 수 없다. 아래 항목만 완료하면 제출 패키지의 실서비스·증빙 요구까지 충족된다.

1. Vercel에서 GitHub 저장소를 Import하고 Root Directory를 `AI 활용 학습 A1-3`로 지정한다.
2. `GEMINI_API_KEY`를 Vercel Environment Variables에 추가하고 Production 배포한다.
3. 공개 URL에서 정상 결과, 빈 입력 메시지, 모바일 화면을 캡처해 `evidence/`에 넣는다.
4. `README.md`와 이 문서의 배포 URL 표기를 실제 URL로 교체한다.
