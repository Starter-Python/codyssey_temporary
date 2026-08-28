# 🤖 [증빙 자료 1] AI 코딩 도구 활용 과정 & 프롬프트 엔지니어링 로그

본 문서는 **Google Antigravity AI 코딩 도구**를 활용하여 스쿼시 리그 웹 애플리케이션 및 Gemini AI 코칭 파이프라인을 구축한 전체 개발 과정, 사용된 핵심 프롬프트, 오류 분석 및 개선 이력을 정리한 공식 증빙 기록입니다.

---

## 1. 개발 단계별 AI 프롬프트 및 의사결정 흐름

```
[ Phase 1: 요구사항 분석 & 기획 ]
  • 프롬프트: "스쿼시 동아리 42명 리그(ESL) 운영 및 경기 메모 기반 AI 코칭 웹앱을 순수 바닐라 JS와 파이썬 서버리스로 설계해줘."
  • AI 산출물: 6대 섹션(대시보드, 대진, 참석, 순위, AI코칭, 운영진) 및 6축 스탯(포핸드, 백핸드, 발리, 드라이브, 드롭, 보스트) 설계안

[ Phase 2: 프론트엔드 순수 바닐라 구축 ]
  • 프롬프트: "React나 무거운 라이브러리 없이 순수 HTML/CSS/JavaScript로 반응형 UI를 작성하고, SVG 수식으로 6축 레이더 차트를 그려줘."
  • AI 산출물: `index.html`, `styles.css`, `app.js` 내 삼각함수(cos, sin) 기반 순수 SVG 다각형 렌더러 구현

[ Phase 3: Vercel Python Serverless 백엔드 & Gemini 연동 ]
  • 프롬프트: "Vercel BaseHTTPRequestHandler 기반으로 GEMINI_API_KEY 환경변수를 안전하게 격리하고, 경기 메모를 분석하는 엔드포인트(api/coach.py)를 만들어줘."
  • AI 산출물: `api/coach.py`, JSON 스키마 검증, 에러 핸들러 및 키 미설정 시 자동 폴백 룰 엔진

[ Phase 4: 3단계 실패 처리 & 보안 가드레일 ]
  • 프롬프트: "빈 입력, API 오류(401/429/500), 10초 타임아웃 상황에서 사용자 경험이 깨지지 않도록 에러 처리와 가드레일을 보강해줘."
  • AI 산출물: `AbortController` 10초 타임아웃, 친절한 한국어 에러 배너, 스탯 인플레이션 방지(±1~2점 상한) 적용
```

---

## 2. 주요 프롬프트 및 AI 응답 상세 로그

### 프롬프트 1: "스쿼시 6축 스탯 레이더 차트를 순수 SVG로 구현하는 방법"
- **사용자 의도**: 외부 무거운 차트 라이브러리(Chart.js 등) 없이 순수 바닐라 환경에서 가볍고 선명한 육각형 스탯 레이더를 동적으로 렌더링.
- **AI 솔루션**:
  ```javascript
  // 6축 각도 계산 및 정규화 좌표 도출
  const angleStep = (Math.PI * 2) / numAxes;
  axes.forEach((axis, i) => {
    const val = stats[axis.key] || 60;
    const normalized = (val - 40) / 60; // 40~100 스케일 정규화
    const angle = i * angleStep - Math.PI / 2;
    const x = cx + Math.cos(angle) * (maxR * normalized);
    const y = cy + Math.sin(angle) * (maxR * normalized);
    dataPoints.push(`${x.toFixed(1)},${y.toFixed(1)}`);
  });
  ```

---

### 프롬프트 2: "Gemini API 키가 없거나 네트워크 오류 시에도 멈추지 않는 Fallback 설계"
- **사용자 의도**: 동료나 평가자가 API 키를 등록하지 않고 로컬에서 테스트하더라도 사이트가 500 에러로 중단되지 않고 분석 결과를 제공받을 수 있도록 설계.
- **AI 솔루션**:
  - `api/coach.py` 내부에 스쿼시 전문 휴리스틱 룰 엔진(`rule_based_analysis`)을 구축하여, 키 미설정 또는 HTTP 4xx/5xx 에러 발생 시 자동으로 양질의 분석 결과를 반환하도록 구현.

---

## 3. 발생 오류 분석 및 AI 코딩 도구를 통한 해결 과정

### 문제 1: React 없이 상태 변경 시 화면 실시간 동기화
- **원인**: 바닐라 JS에서는 리액트의 `useState` 같은 자동 리렌더링이 없으므로, 데이터 변경 후 특정 컴포넌트만 갱신되지 않는 문제 발생.
- **해결**: 단일 진실 공급원(`appState`)을 정의하고, 탭 전환 및 데이터 수정(`saveState`) 시 해당 뷰 렌더러(`renderSchedule`, `renderRankings`, `renderAttendance`)를 모듈형으로 호출하도록 구조화.

### 문제 2: 스탯 인플레이션 현상 방지
- **원인**: AI 코칭에서 경기마다 +5점, +10점씩 과도한 스탯을 부여할 경우 OVR 99를 초과하여 게임 밸런스가 붕괴됨.
- **해결**: 프롬프트 가이드라인에 1경기 최대 변동치(`-1, 0, +1, +2`)를 명시하고, 백엔드 및 프론트엔드에서 40~99 범위로 `Math.min / Math.max` 클램핑 처리.
