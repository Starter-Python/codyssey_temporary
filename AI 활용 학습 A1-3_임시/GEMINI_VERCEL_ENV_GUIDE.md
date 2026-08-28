# Gemini API 키와 Vercel 환경 변수 설정 안내

## 먼저 알아야 할 결론

온기록의 AI 기능은 **Gemini API 키가 있어야 실제로 동작**한다. 하지만 키를 `app.js`나 `index.html`에 넣으면 사이트 방문자가 브라우저 도구를 통해 키를 꺼내 볼 수 있다. 따라서 키는 GitHub와 대화창이 아닌 **Vercel 환경 변수**에 한 번만 저장하고, Vercel의 Python 함수가 실행될 때만 읽게 해야 한다.

> **환경 변수란?** 코드 파일 밖에 저장하는 ‘이름표가 붙은 비밀값’이다. 이 프로젝트에서는 `GEMINI_API_KEY`라는 이름표 아래에 실제 Gemini 키를 저장한다. Python 코드는 `os.environ.get("GEMINI_API_KEY")`로 그 값을 읽지만, 브라우저로는 값을 보내지 않는다.

Vercel은 환경 변수를 코드 밖에서 환경별로 저장하고, 암호화된 상태로 관리한다고 설명한다. 또한 값 변경은 이미 만들어진 과거 배포에 적용되지 않으므로 새 배포가 필요하다. [1]

## 1. Gemini API 키 만들기

Google AI Studio에서 Gemini API 키를 만든다. 처음 사용하는 계정은 AI Studio가 기본 Google Cloud 프로젝트와 API 키를 만들 수 있으며, 필요하면 API Keys 화면에서 새 키를 생성할 수 있다. [2]

1. [Google AI Studio API Keys](https://aistudio.google.com/api-keys)에 Google 계정으로 로그인한다.
2. **Create API key**를 누른다.
3. 연결할 Google Cloud 프로젝트를 선택하거나 새 프로젝트를 만든다.
4. 표시되는 키를 복사한다. 이 값은 비밀번호처럼 취급하며, 공개된 화면이나 GitHub에 붙여 넣지 않는다.

현재 Gemini API는 일부 모델을 대상으로 **Free Tier**를 제공하지만, 모델별 사용량 한도가 있고 서비스 조건은 바뀔 수 있다. 무료 등급에서는 입력·출력 토큰이 무료인 특정 모델이 제공되며, 더 높은 한도나 일부 고급 기능에는 유료 등급이 필요하다. [3] 이 과제의 짧은 텍스트 루틴 생성에는 기본값인 `gemini-3.6-flash`를 사용하도록 준비했지만, 실제 계정에서 사용 가능한 무료 모델과 한도는 AI Studio의 Usage 화면에서 확인해야 한다.

| 선택 항목 | 과제용 권장값 | 이유 |
|---|---|---|
| API 제공자 | Gemini API | 일부 모델에 Free Tier가 있어 소규모 과제 테스트에 적합할 수 있다. |
| 환경 변수 이름 | `GEMINI_API_KEY` | Google의 Python SDK가 인식하는 권장 변수명이다. [2] |
| 모델 변수 | `GEMINI_MODEL=gemini-3.6-flash` | 코드 수정 없이 AI Studio에서 가능한 텍스트 모델로 교체할 수 있다. |
| 키 보관 위치 | Vercel Environment Variables | GitHub와 브라우저 코드에서 키를 분리한다. |

## 2. Vercel 환경 변수에 넣는 방법

Vercel에 이미 GitHub 저장소를 연결했다는 기준으로 설명한다. 아직 연결하지 않았다면 먼저 [Vercel New Project](https://vercel.com/new)에서 `Starter-Python/Manus` 저장소를 Import하고 **Root Directory**를 `AI 활용 학습 A1-3`로 지정한다.

1. Vercel Dashboard에서 배포한 프로젝트를 연다.
2. 상단 또는 좌측의 **Settings**로 이동한다.
3. **Environment Variables** 메뉴를 연다.
4. Key 칸에는 정확히 `GEMINI_API_KEY`를 입력한다.
5. Value 칸에는 Google AI Studio에서 복사한 실제 키를 붙여 넣는다.
6. Environment는 우선 **Production**을 선택한다. 배포 전 미리보기에서도 시험하고 싶다면 **Preview**도 선택한다. 로컬 `vercel dev`까지 사용할 계획이면 **Development**도 선택한다.
7. Save를 누른다.
8. Deployments로 이동해 가장 최근 배포에서 **Redeploy**를 실행하거나, GitHub에 새 커밋을 푸시한다.
9. 배포 URL의 루틴 설계 화면에서 입력값을 넣고 AI 결과가 나오는지 확인한다.

`GEMINI_MODEL`은 선택 변수다. 기본값이 코드에 있으므로 넣지 않아도 된다. 다만 AI Studio에서 다른 모델을 쓰고 싶다면 동일한 방법으로 Key를 `GEMINI_MODEL`, Value를 해당 모델명으로 추가할 수 있다.

## 3. 왜 채팅이나 GitHub에 API 키를 보내면 안 되는가

Gemini 공식 문서는 API 키를 비밀번호처럼 취급하고, 소스 제어 시스템에 커밋하지 말며, 프로덕션의 클라이언트 코드에 노출하지 말라고 안내한다. 노출된 키는 다른 사람이 프로젝트 사용량을 소모하거나 예기치 않은 요금·리소스 접근을 일으킬 수 있다. [2]

따라서 이 작업에서는 **사용자가 키 값을 나에게 보내지 않아도 된다.** 코드에는 키의 이름만 있고 실제 값은 없다. 사용자는 Vercel 화면에서 직접 한 번만 붙여 넣고, 저는 코드가 그 이름을 읽도록 구현한다. 이것이 가장 단순하면서도 안전한 역할 분리다.

| 위치 | 실제 키 저장 여부 | 안전한가? | 이유 |
|---|---:|---:|---|
| 이 대화창 | 저장하지 않음 | 아니오 | 대화 기록·복사·공유 과정에서 노출될 수 있다. |
| GitHub 코드·README | 저장하지 않음 | 아니오 | 저장소 접근자가 보거나 커밋 이력에 남을 수 있다. |
| `app.js`·`index.html` | 저장하지 않음 | 아니오 | 방문자가 브라우저 개발자 도구에서 추출할 수 있다. |
| 로컬 `.env.local` | 개인 테스트용으로만 저장 | 조건부 | `.gitignore`로 제외하고 공유하지 않아야 한다. |
| Vercel Environment Variables | 저장함 | 예 | 서버 함수가 실행될 때만 읽고, 배포 코드와 분리된다. |

만약 실수로 키를 GitHub, 채팅, 스크린샷에 올렸다면 즉시 Google AI Studio에서 새 키를 만들고, Vercel 환경 변수 값을 새 키로 바꾼 후 재배포한다. 기존 노출 키는 검증 뒤 비활성화하거나 삭제한다. [2]

## 4. 자주 묻는 질문

### Q. Vercel에 키를 넣으면 방문자가 볼 수 있나요?

아니요. `GEMINI_API_KEY`는 Python 함수 서버에서만 읽는다. 브라우저는 `/api/recommend`에 입력값을 보내고 결과 JSON만 받는다. 단, 실수로 키를 프론트엔드 파일에 작성하면 노출되므로 절대 넣지 않는다.

### Q. 무료 등급이면 카드 등록이 전혀 필요 없나요?

Gemini API 문서에 따르면 새 계정은 Free Tier에서 시작하고, 특정 모델에 한해 무료 사용량이 제공된다. [4] 다만 국가·계정·선택 모델·한도 상태에 따라 조건이 달라질 수 있으므로, 키 생성 후 AI Studio의 프로젝트 상태와 Usage 화면을 확인해야 한다. 유료 등급 전환은 별도의 결제 설정 절차가 필요한 선택 사항이다. [4]

### Q. 키를 한 번 저장했는데 다시 배포해야 하나요?

네. Vercel은 환경 변수 변경을 이전 배포에 소급 적용하지 않는다. 값을 저장한 뒤 Redeploy 또는 새 커밋으로 새 배포를 만들어야 한다. [1]

## 참고 자료

[1]: https://vercel.com/docs/environment-variables "Vercel — Environment variables"
[2]: https://ai.google.dev/gemini-api/docs/api-key "Google AI for Developers — Using Gemini API keys"
[3]: https://ai.google.dev/gemini-api/docs/pricing "Google AI for Developers — Gemini Developer API pricing"
[4]: https://ai.google.dev/gemini-api/docs/billing "Google AI for Developers — Gemini API billing"
