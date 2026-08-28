/**
 * ENTHES Official Squash League (ESL) & AI Studio
 * Pure Vanilla JavaScript Client Application
 */

// ==========================================
// 1. Initial 42-Player Official Dataset
// ==========================================
const INITIAL_PLAYERS = [
  // 1부 리그 (13명)
  { id: 1, name: '조재경', league: '1부', tier: 1, gender: 'M', ovr: 89, stats: { forehand: 92, backhand: 88, volley: 90, drive: 91, drop: 87, boast: 86 }, played: 8, win: 7, loss: 1, aiSummary: '깊은 사이드월 렝스 드라이브와 T-존 선제 발리가 뛰어난 올라운더.' },
  { id: 2, name: '문찬영', league: '1부', tier: 2, gender: 'M', ovr: 86, stats: { forehand: 88, backhand: 84, volley: 87, drive: 88, drop: 85, boast: 84 }, played: 7, win: 5, loss: 2, aiSummary: '예리한 프론트 코너 드롭과 안정적인 랠리 템포 조절이 장점.' },
  { id: 3, name: '심규성', league: '1부', tier: 2, gender: 'M', ovr: 85, stats: { forehand: 86, backhand: 85, volley: 84, drive: 87, drop: 83, boast: 85 }, played: 8, win: 6, loss: 2, aiSummary: '강력한 포핸드 파워와 3벽 보스트를 활용한 역습 능력이 돋보임.' },
  { id: 4, name: '이창민', league: '1부', tier: 2, gender: 'M', ovr: 84, stats: { forehand: 85, backhand: 82, volley: 86, drive: 85, drop: 84, boast: 82 }, played: 7, win: 4, loss: 3, aiSummary: '민첩한 풋워크와 전위 가로채기 플레이에 강점이 있음.' },
  { id: 5, name: '김동규', league: '1부', tier: 2, gender: 'M', ovr: 83, stats: { forehand: 84, backhand: 83, volley: 82, drive: 84, drop: 82, boast: 83 }, played: 8, win: 5, loss: 3, aiSummary: '안정적인 수비 전환과 긴 랠리에서의 체력적 우위 보유.' },
  { id: 6, name: '김성모', league: '1부', tier: 2, gender: 'M', ovr: 83, stats: { forehand: 85, backhand: 80, volley: 85, drive: 83, drop: 84, boast: 81 }, played: 7, win: 4, loss: 3, aiSummary: '공격적인 발리와 닉샷 구사율이 높은 플레이스타일.' },
  { id: 7, name: '전유나', league: '1부', tier: 2, gender: 'F', ovr: 82, stats: { forehand: 82, backhand: 84, volley: 83, drive: 82, drop: 86, boast: 81 }, played: 8, win: 4, loss: 4, aiSummary: '부드러운 손목 스냅을 이용한 전위 드롭과 코스 분배가 정교함.' },
  { id: 8, name: '전용성', league: '1부', tier: 2, gender: 'M', ovr: 82, stats: { forehand: 83, backhand: 81, volley: 82, drive: 83, drop: 81, boast: 82 }, played: 7, win: 3, loss: 4, aiSummary: '후위 코너 깊은 수비와 끈질긴 랠리 지속력이 특징.' },
  { id: 9, name: '전서진', league: '1부', tier: 2, gender: 'F', ovr: 81, stats: { forehand: 80, backhand: 82, volley: 81, drive: 81, drop: 85, boast: 80 }, played: 7, win: 3, loss: 4, aiSummary: '정확한 백핸드 리턴과 침착한 게임 운영 능력 보유.' },
  { id: 10, name: '황은재', league: '1부', tier: 2, gender: 'M', ovr: 80, stats: { forehand: 82, backhand: 79, volley: 80, drive: 82, drop: 80, boast: 79 }, played: 8, win: 3, loss: 5, aiSummary: '직선 드라이브의 속도가 빠르고 전환 속도가 우수함.' },
  { id: 11, name: '남서현', league: '1부', tier: 2, gender: 'F', ovr: 80, stats: { forehand: 79, backhand: 81, volley: 80, drive: 79, drop: 83, boast: 78 }, played: 7, win: 2, loss: 5, aiSummary: '높은 로브 수비와 빈 공간을 찌르는 크로스 샷이 위협적.' },
  { id: 12, name: '조유나', league: '1부', tier: 2, gender: 'F', ovr: 79, stats: { forehand: 78, backhand: 80, volley: 79, drive: 78, drop: 82, boast: 78 }, played: 8, win: 2, loss: 6, aiSummary: '수비 복귀 속도가 빠르고 숏게임 센스가 뛰어남.' },
  { id: 13, name: '원명', league: '1부', tier: 2, gender: 'M', ovr: 79, stats: { forehand: 81, backhand: 78, volley: 78, drive: 80, drop: 78, boast: 79 }, played: 7, win: 2, loss: 5, aiSummary: '강한 서브와 순간적인 가속을 활용한 압박 수비 능숙.' },

  // 2부 리그 (17명)
  { id: 14, name: '최한재', league: '2부', tier: 3, gender: 'M', ovr: 78, stats: { forehand: 80, backhand: 77, volley: 78, drive: 79, drop: 77, boast: 77 }, played: 7, win: 6, loss: 1, aiSummary: '2부 최상위권 안정감과 사이드월 밀착 드라이브 강점.' },
  { id: 15, name: '문지환', league: '2부', tier: 3, gender: 'M', ovr: 77, stats: { forehand: 79, backhand: 76, volley: 77, drive: 78, drop: 76, boast: 76 }, played: 8, win: 6, loss: 2, aiSummary: 'T존 장악력이 우수하고 빠른 발리 찬스 포착 능력 보유.' },
  { id: 16, name: '장지낭', league: '2부', tier: 4, gender: 'M', ovr: 76, stats: { forehand: 78, backhand: 75, volley: 76, drive: 77, drop: 75, boast: 75 }, played: 7, win: 5, loss: 2, aiSummary: '보스트를 이용한 수비 탈출과 역습 전환이 날카로움.' },
  { id: 17, name: '김성우', league: '2부', tier: 3, gender: 'M', ovr: 75, stats: { forehand: 77, backhand: 74, volley: 75, drive: 76, drop: 74, boast: 74 }, played: 7, win: 4, loss: 3, aiSummary: '지속적인 랠리에서 범실을 줄이는 탄탄한 기본기.' },
  { id: 18, name: '정연훈', league: '2부', tier: 3, gender: 'M', ovr: 75, stats: { forehand: 76, backhand: 74, volley: 75, drive: 76, drop: 75, boast: 74 }, played: 8, win: 4, loss: 4, aiSummary: '포핸드 앵글 샷과 코트 구석을 활용한 각도 플레이 우수.' },
  { id: 19, name: '양선주', league: '2부', tier: 3, gender: 'F', ovr: 74, stats: { forehand: 73, backhand: 75, volley: 74, drive: 73, drop: 78, boast: 72 }, played: 7, win: 4, loss: 3, aiSummary: '네트 앞 정교한 드롭으로 상대 풋워크를 흔드는 전술.' },
  { id: 20, name: '김영완', league: '2부', tier: 3, gender: 'M', ovr: 74, stats: { forehand: 75, backhand: 73, volley: 74, drive: 75, drop: 73, boast: 74 }, played: 7, win: 3, loss: 4, aiSummary: '후위 백월 바운드 예측과 차분한 리턴이 안정적.' },
  { id: 21, name: '오세훈', league: '2부', tier: 3, gender: 'M', ovr: 73, stats: { forehand: 74, backhand: 72, volley: 73, drive: 74, drop: 72, boast: 73 }, played: 8, win: 3, loss: 5, aiSummary: '파워풀한 스윙과 공격적인 랠리 주도 시도가 돋보임.' },
  { id: 22, name: '지명훈', league: '2부', tier: 4, gender: 'M', ovr: 73, stats: { forehand: 75, backhand: 71, volley: 72, drive: 74, drop: 72, boast: 74 }, played: 7, win: 3, loss: 4, aiSummary: '상대 허를 찌르는 크로스 드라이브가 강점.' },
  { id: 23, name: '김기환', league: '2부', tier: 3, gender: 'M', ovr: 72, stats: { forehand: 73, backhand: 71, volley: 72, drive: 73, drop: 71, boast: 72 }, played: 7, win: 3, loss: 4, aiSummary: '서브 리턴 안정성과 코트 중앙 복귀 타이밍 준수.' },
  { id: 24, name: '서유나', league: '2부', tier: 4, gender: 'F', ovr: 72, stats: { forehand: 71, backhand: 73, volley: 72, drive: 71, drop: 75, boast: 70 }, played: 8, win: 3, loss: 5, aiSummary: '침착한 경기 조율과 수비 시 정확한 로브 샷 구사.' },
  { id: 25, name: '백송이', league: '2부', tier: 3, gender: 'F', ovr: 71, stats: { forehand: 70, backhand: 72, volley: 71, drive: 70, drop: 74, boast: 69 }, played: 7, win: 2, loss: 5, aiSummary: '전위 숏게임에서 강한 집중력을 발휘하는 스타일.' },
  { id: 26, name: '김지애', league: '2부', tier: 4, gender: 'F', ovr: 71, stats: { forehand: 70, backhand: 72, volley: 70, drive: 70, drop: 73, boast: 70 }, played: 7, win: 2, loss: 5, aiSummary: '백핸드 3벽 보스트와 라인 안쪽 깊은 리턴이 장점.' },
  { id: 27, name: '한기헌', league: '2부', tier: 3, gender: 'M', ovr: 70, stats: { forehand: 72, backhand: 69, volley: 70, drive: 71, drop: 69, boast: 69 }, played: 8, win: 2, loss: 6, aiSummary: '빠른 풋워크로 코트 전 영역을 커버하는 활동량.' },
  { id: 28, name: '최혜원', league: '2부', tier: 4, gender: 'F', ovr: 70, stats: { forehand: 69, backhand: 71, volley: 70, drive: 69, drop: 73, boast: 68 }, played: 7, win: 2, loss: 5, aiSummary: '상대 움직임을 파악하고 역방향으로 찌르는 플레이 센스.' },
  { id: 29, name: '박수아', league: '2부', tier: 4, gender: 'F', ovr: 69, stats: { forehand: 68, backhand: 70, volley: 69, drive: 68, drop: 72, boast: 68 }, played: 7, win: 1, loss: 6, aiSummary: '끈질긴 수비력과 체력적인 안정감이 돋보임.' },
  { id: 30, name: '배혜영', league: '2부', tier: 4, gender: 'F', ovr: 69, stats: { forehand: 68, backhand: 70, volley: 68, drive: 68, drop: 71, boast: 69 }, played: 8, win: 1, loss: 7, aiSummary: '정확한 서브로 상대 리턴 실수를 유도하는 패턴 능숙.' },

  // 3부 루키 리그 (12명)
  { id: 31, name: '박지아', league: '3부', tier: 4, gender: 'F', ovr: 68, stats: { forehand: 68, backhand: 67, volley: 68, drive: 68, drop: 70, boast: 67 }, played: 8, win: 7, loss: 1, aiSummary: '3부 루키 리그 선두, 안정적인 포·백 스트로크 밸런스.' },
  { id: 32, name: '김현우', league: '3부', tier: 4, gender: 'M', ovr: 67, stats: { forehand: 69, backhand: 65, volley: 67, drive: 68, drop: 66, boast: 67 }, played: 7, win: 6, loss: 1, aiSummary: '파워 있는 포핸드와 빠른 스피드로 랠리 장악.' },
  { id: 33, name: '김동주', league: '3부', tier: 4, gender: 'M', ovr: 66, stats: { forehand: 68, backhand: 65, volley: 66, drive: 67, drop: 65, boast: 65 }, played: 8, win: 5, loss: 3, aiSummary: '직선 드라이브 구사율이 높고 풋워크가 민첩함.' },
  { id: 34, name: '원영서', league: '3부', tier: 5, gender: 'F', ovr: 65, stats: { forehand: 64, backhand: 66, volley: 65, drive: 64, drop: 68, boast: 63 }, played: 7, win: 4, loss: 3, aiSummary: '부드러운 스윙 궤적으로 전위 숏게임에서 득점 생산.' },
  { id: 35, name: '임예진', league: '3부', tier: 5, gender: 'F', ovr: 64, stats: { forehand: 63, backhand: 65, volley: 64, drive: 63, drop: 67, boast: 63 }, played: 8, win: 4, loss: 4, aiSummary: '백핸드 수비 성공률이 꾸준히 성장하고 있는 루키.' },
  { id: 36, name: '이지우', league: '3부', tier: 5, gender: 'M', ovr: 64, stats: { forehand: 66, backhand: 62, volley: 64, drive: 65, drop: 63, boast: 64 }, played: 7, win: 3, loss: 4, aiSummary: '강한 서브와 전진 스매시 공격력이 우수함.' },
  { id: 37, name: '박태현', league: '3부', tier: 5, gender: 'M', ovr: 63, stats: { forehand: 65, backhand: 61, volley: 63, drive: 64, drop: 62, boast: 63 }, played: 8, win: 3, loss: 5, aiSummary: '코트 이동 속도가 빠르고 수비 범위가 넓음.' },
  { id: 38, name: '김민주', league: '3부', tier: 6, gender: 'F', ovr: 62, stats: { forehand: 61, backhand: 63, volley: 62, drive: 61, drop: 65, boast: 60 }, played: 7, win: 2, loss: 5, aiSummary: '정확한 로브로 랠리 호흡을 가다듬는 능력 보유.' },
  { id: 39, name: '최다은', league: '3부', tier: 6, gender: 'F', ovr: 61, stats: { forehand: 60, backhand: 62, volley: 61, drive: 60, drop: 64, boast: 59 }, played: 7, win: 2, loss: 5, aiSummary: '성실한 풋워크와 집중력 높은 리턴 플레이.' },
  { id: 40, name: '정유진', league: '3부', tier: 6, gender: 'F', ovr: 60, stats: { forehand: 59, backhand: 61, volley: 60, drive: 59, drop: 63, boast: 58 }, played: 8, win: 1, loss: 7, aiSummary: '전위 찬스볼 대처와 서비스 기본기 향상 중.' },
  { id: 41, name: '이지민', league: '3부', tier: 6, gender: 'F', ovr: 59, stats: { forehand: 58, backhand: 60, volley: 59, drive: 58, drop: 62, boast: 57 }, played: 7, win: 1, loss: 6, aiSummary: '침착한 자세로 기초 드라이브 렝스를 익히는 단계.' },
  { id: 42, name: '민수정', league: '3부', tier: 6, gender: 'F', ovr: 58, stats: { forehand: 57, backhand: 59, volley: 58, drive: 57, drop: 61, boast: 56 }, played: 8, win: 1, loss: 7, aiSummary: '기본 룰 숙지 및 코트 적응이 빠른 유망 루키.' }
];

// Initial Schedules & Matches
const INITIAL_MATCHES = [
  { id: 101, date: new Date().toISOString().slice(0, 10), league: '1부', playerA: '조재경', playerB: '문찬영', tierA: 1, tierB: 2, genderA: 'M', genderB: 'M', court: '코트 1', time: '19:00', referees: ['심규성', '이창민'], scoreA: 15, scoreB: 12, status: 'confirmed', memo: '조재경의 깊은 렝스 드라이브와 문찬영의 닉샷 대결. 팽팽한 랠리 끝에 조재경 승리.' },
  { id: 102, date: new Date().toISOString().slice(0, 10), league: '1부', playerA: '심규성', playerB: '전유나', tierA: 2, tierB: 2, genderA: 'M', genderB: 'F', court: '코트 2', time: '19:25', referees: ['조재경', '문찬영'], scoreA: null, scoreB: null, status: 'scheduled', memo: null },
  { id: 103, date: new Date().toISOString().slice(0, 10), league: '2부', playerA: '최한재', playerB: '문지환', tierA: 3, tierB: 3, genderA: 'M', genderB: 'M', court: '코트 1', time: '19:50', referees: ['장지낭', '김성우'], scoreA: 15, scoreB: 13, status: 'confirmed', memo: '최한재의 T존 장악과 문지환의 빠른 발리 카운터.' },
  { id: 104, date: new Date().toISOString().slice(0, 10), league: '2부', playerA: '장지낭', playerB: '양선주', tierA: 4, tierB: 3, genderA: 'M', genderB: 'F', court: '코트 2', time: '20:15', referees: ['최한재', '문지환'], scoreA: null, scoreB: null, status: 'scheduled', memo: null },
  { id: 105, date: new Date().toISOString().slice(0, 10), league: '3부', playerA: '박지아', playerB: '김현우', tierA: 4, tierB: 4, genderA: 'F', genderB: 'M', court: '코트 1', time: '20:40', referees: ['김동주', '원영서'], scoreA: 15, scoreB: 11, status: 'confirmed', memo: '박지아 선수의 전위 드롭 득점이 승부를 갈랐음.' },
  { id: 106, date: new Date().toISOString().slice(0, 10), league: '3부', playerA: '김동주', playerB: '원영서', tierA: 4, tierB: 5, genderA: 'M', genderB: 'F', court: '코트 2', time: '21:05', referees: ['박지아', '김현우'], scoreA: null, scoreB: null, status: 'scheduled', memo: null }
];

// ==========================================
// 2. Application State Management
// ==========================================
let appState = {
  players: [],
  matches: [],
  attendances: {}, // { "YYYY-MM-DD": { [playerId]: "attending" | "absent" | "waitlist" } }
  activeUser: null,
  activeLeague: '1부',
  selectedPlayerId: 1,
  adminPin: '1234',
  isAdminAuthenticated: false,
  aiReportsCount: 3,
  lastAiResult: null
};

function saveState() {
  try {
    localStorage.setItem('enthes_esl_state_v1', JSON.stringify(appState));
  } catch (e) {
    console.warn('localStorage save failed:', e);
  }
}

function loadState() {
  try {
    const saved = localStorage.getItem('enthes_esl_state_v1');
    if (saved) {
      const parsed = JSON.parse(saved);
      appState = Object.assign(appState, parsed);
      return;
    }
  } catch (e) {
    console.warn('localStorage load failed:', e);
  }
  // Initialize defaults
  appState.players = JSON.parse(JSON.stringify(INITIAL_PLAYERS));
  appState.matches = JSON.parse(JSON.stringify(INITIAL_MATCHES));
  
  // Seed today attendance
  const today = new Date().toISOString().slice(0, 10);
  appState.attendances[today] = {
    1: 'attending', 2: 'attending', 3: 'attending', 7: 'attending',
    14: 'attending', 15: 'attending', 16: 'attending', 19: 'attending',
    31: 'attending', 32: 'attending', 33: 'attending', 34: 'attending'
  };
  saveState();
}

// ==========================================
// 3. Navigation & Tab Switching
// ==========================================
function switchTab(tabId) {
  // Update desktop nav
  document.querySelectorAll('.nav-btn').forEach(btn => {
    btn.classList.toggle('active', btn.dataset.tab === tabId);
  });

  // Update mobile nav
  document.querySelectorAll('.m-nav-btn').forEach(btn => {
    btn.classList.toggle('active', btn.dataset.tab === tabId);
  });

  // Update panes
  document.querySelectorAll('.tab-pane').forEach(pane => {
    pane.classList.remove('active');
  });

  const target = document.getElementById(`tab-${tabId}`);
  if (target) target.classList.add('active');

  // Trigger relevant renders
  if (tabId === 'dashboard') renderDashboard();
  if (tabId === 'schedule') renderSchedule();
  if (tabId === 'attendance') renderAttendance();
  if (tabId === 'rankings') renderRankings();
  if (tabId === 'ai-coach') populateAiSelects();
  if (tabId === 'admin') renderAdminView();

  window.scrollTo({ top: 0, behavior: 'smooth' });
}

// ==========================================
// 4. Rendering Functions
// ==========================================

// Dashboard
function renderDashboard() {
  document.getElementById('stat-total-players').innerHTML = `${appState.players.length}<small>명</small>`;
  
  const confirmedMatches = appState.matches.filter(m => m.status === 'confirmed').length;
  document.getElementById('stat-total-matches').innerHTML = `${confirmedMatches}<small>경기</small>`;

  const today = new Date().toISOString().slice(0, 10);
  const todayAtt = Object.values(appState.attendances[today] || {}).filter(s => s === 'attending').length;
  document.getElementById('stat-today-attending').innerHTML = `${todayAtt}<small>명</small>`;
  document.getElementById('stat-ai-reports').innerHTML = `${appState.aiReportsCount}<small>건</small>`;

  // Render Today's Scheduled Matches
  const todayContainer = document.getElementById('dash-today-matches');
  const todayList = appState.matches.filter(m => m.status === 'scheduled').slice(0, 4);
  if (todayList.length === 0) {
    todayContainer.innerHTML = '<p class="text-muted" style="font-size: 0.85rem; padding: 1rem 0;">예정된 대진이 없습니다.</p>';
  } else {
    todayContainer.innerHTML = todayList.map(m => `
      <div class="compact-match-item">
        <div>
          <span class="badge badge-emerald" style="margin-right: 0.35rem;">${m.league}</span>
          <strong>${m.playerA}</strong> vs <strong>${m.playerB}</strong>
        </div>
        <span style="color: var(--text-muted); font-size: 0.75rem;">${m.court} · ${m.time}</span>
      </div>
    `).join('');
  }

  // Render Recent Results
  const recentContainer = document.getElementById('dash-recent-results');
  const recentList = appState.matches.filter(m => m.status === 'confirmed').slice(0, 4);
  if (recentList.length === 0) {
    recentContainer.innerHTML = '<p class="text-muted" style="font-size: 0.85rem; padding: 1rem 0;">확정된 경기 결과가 아직 없습니다.</p>';
  } else {
    recentContainer.innerHTML = recentList.map(m => `
      <div class="compact-match-item">
        <div>
          <span class="badge badge-emerald" style="margin-right: 0.35rem;">${m.league}</span>
          <strong>${m.playerA}</strong> vs <strong>${m.playerB}</strong>
        </div>
        <strong style="color: var(--brand-emerald-dark);">${m.scoreA} : ${m.scoreB}</strong>
      </div>
    `).join('');
  }
}

// Schedule
function renderSchedule() {
  const leagueFilter = document.getElementById('schedule-league-filter').value;
  const dateFilter = document.getElementById('schedule-date-picker').value || new Date().toISOString().slice(0, 10);
  
  const container = document.getElementById('schedule-match-list');
  let matches = appState.matches.filter(m => {
    const matchLeague = leagueFilter === '전체' || m.league === leagueFilter;
    return matchLeague;
  });

  if (matches.length === 0) {
    container.innerHTML = '<div class="panel-card" style="grid-column: 1/-1; text-align: center; color: var(--text-muted);">해당 조건의 경기 대진이 없습니다.</div>';
    return;
  }

  container.innerHTML = matches.map(m => {
    const pA = appState.players.find(p => p.name === m.playerA) || { tier: m.tierA || 2, gender: m.genderA || 'M' };
    const pB = appState.players.find(p => p.name === m.playerB) || { tier: m.tierB || 2, gender: m.genderB || 'M' };
    
    // Handicap calculation
    let handicapText = '';
    const tierDiff = pB.tier - pA.tier;
    if (tierDiff > 0) {
      handicapText = `⚡ ${m.playerB} 선수 +${tierDiff * 2}점 핸디캡 & 1세트 서브권`;
    } else if (tierDiff < 0) {
      handicapText = `⚡ ${m.playerA} 선수 +${Math.abs(tierDiff) * 2}점 핸디캡 & 1세트 서브권`;
    } else {
      handicapText = `⚡ 동티어 경기 (핸디캡 없음, 서브권 가위바위보)`;
    }

    if (pA.gender !== pB.gender) {
      const femalePlayer = pA.gender === 'F' ? m.playerA : m.playerB;
      handicapText += ` · ${femalePlayer} 선수 +2점 성별 어드밴티지`;
    }

    const isConfirmed = m.status === 'confirmed';

    return `
      <div class="match-card">
        <div class="match-meta-bar">
          <span><span class="badge badge-emerald">${m.league}</span> · ${m.court}</span>
          <span>⏰ ${m.time || '19:00'} · ${isConfirmed ? '✅ 결과 확정' : '⏳ 경기 예정'}</span>
        </div>

        <div class="match-versus-row">
          <div class="player-side">
            <span class="player-name">${m.playerA}</span>
            <span class="player-tag">T${pA.tier} · ${pA.gender === 'M' ? '남' : '여'}</span>
          </div>

          <div style="text-align: center;">
            ${isConfirmed 
              ? `<strong style="font-size: 1.25rem; color: var(--brand-emerald-dark);">${m.scoreA} : ${m.scoreB}</strong>` 
              : '<span class="vs-badge">VS</span>'}
          </div>

          <div class="player-side" style="text-align: right;">
            <span class="player-name">${m.playerB}</span>
            <span class="player-tag">T${pB.tier} · ${pB.gender === 'M' ? '남' : '여'}</span>
          </div>
        </div>

        <div class="handicap-bar">${handicapText}</div>
        <div class="referee-bar">👤 배정 자율 심판: <strong>${(m.referees || ['자율 심판']).join(', ')}</strong></div>
      </div>
    `;
  }).join('');
}

// Attendance
let currentAttendanceStatus = 'attending';

function renderAttendance() {
  const dateInput = document.getElementById('att-date-input');
  if (!dateInput.value) {
    dateInput.value = new Date().toISOString().slice(0, 10);
  }
  const curDate = dateInput.value;
  document.getElementById('att-selected-date-label').textContent = curDate;

  // Fill player dropdown
  const select = document.getElementById('att-player-select');
  select.innerHTML = '<option value="">선수를 선택하세요</option>' + appState.players.map(p => `
    <option value="${p.id}">${p.name} (${p.league} · T${p.tier})</option>
  `).join('');

  if (appState.activeUser) {
    select.value = appState.activeUser;
  }

  // Render Roster chips
  const dateAtt = appState.attendances[curDate] || {};
  let totalAttending = 0;

  for (let l = 1; l <= 3; l++) {
    const lName = l === 3 ? '3부' : `${l}부`;
    const container = document.getElementById(`roster-league-${l}`);
    const leaguePlayers = appState.players.filter(p => p.league === lName);

    container.innerHTML = leaguePlayers.map(p => {
      const status = dateAtt[p.id] || 'unselected';
      let chipClass = 'roster-chip';
      let icon = '⚪';
      if (status === 'attending') {
        chipClass += ' chip-attending';
        icon = '🟢';
        totalAttending++;
      } else if (status === 'absent') {
        chipClass += ' chip-absent';
        icon = '🔴';
      }
      return `<span class="${chipClass}">${icon} ${p.name} (T${p.tier})</span>`;
    }).join('');
  }

  document.getElementById('att-count-badge').textContent = `참석 ${totalAttending}명`;
}

// Rankings & Radar
function renderRankings() {
  const tbody = document.getElementById('ranking-tbody');
  const leaguePlayers = appState.players.filter(p => p.league === appState.activeLeague);
  
  // Sort by OVR desc, then win desc
  leaguePlayers.sort((a, b) => b.ovr - a.ovr || b.win - a.win);

  tbody.innerHTML = leaguePlayers.map((p, index) => {
    const winRate = p.played > 0 ? Math.round((p.win / p.played) * 100) : 0;
    const isSelected = p.id === appState.selectedPlayerId;
    let rankBadgeClass = 'rank-badge';
    if (index === 0) rankBadgeClass += ' gold';
    else if (index === 1) rankBadgeClass += ' silver';
    else if (index === 2) rankBadgeClass += ' bronze';

    return `
      <tr class="${isSelected ? 'selected' : ''}" onclick="selectPlayerForRadar(${p.id})">
        <td><span class="${rankBadgeClass}">${index + 1}</span></td>
        <td><strong>${p.name}</strong> ${p.gender === 'F' ? '<small style="color:#ec4899;">(여)</small>' : ''}</td>
        <td><span class="badge badge-emerald">T${p.tier}</span></td>
        <td><strong style="color:var(--brand-emerald-dark);">${p.ovr}</strong></td>
        <td>${p.played}</td>
        <td>${p.win}승 ${p.loss}패</td>
        <td>${winRate}%</td>
        <td><button type="button" class="btn btn-sm btn-secondary" style="padding: 0.2rem 0.5rem;">차트보기</button></td>
      </tr>
    `;
  }).join('');

  // Render Selected Player Detail Card
  const selected = appState.players.find(p => p.id === appState.selectedPlayerId) || leaguePlayers[0] || appState.players[0];
  if (selected) {
    document.getElementById('prof-name').textContent = selected.name;
    document.getElementById('prof-tier').textContent = `T${selected.tier}`;
    document.getElementById('prof-league').textContent = `${selected.league} 리그`;
    document.getElementById('prof-ovr').textContent = selected.ovr;
    document.getElementById('prof-ai-summary').textContent = selected.aiSummary || '등록된 AI 피드백이 없습니다.';

    // Stat bars
    const statKeys = [
      { key: 'forehand', label: '포핸드' },
      { key: 'backhand', label: '백핸드' },
      { key: 'volley', label: '발리' },
      { key: 'drive', label: '드라이브' },
      { key: 'drop', label: '드롭' },
      { key: 'boast', label: '보스트' }
    ];

    document.getElementById('prof-stat-bars').innerHTML = statKeys.map(s => `
      <div class="stat-bar-item">
        <span style="color: var(--text-muted);">${s.label}</span>
        <strong>${selected.stats[s.key] || 70}</strong>
      </div>
    `).join('');

    renderSvgRadarChart(selected.stats);
  }
}

function selectPlayerForRadar(id) {
  appState.selectedPlayerId = id;
  renderRankings();
}

// Pure Mathematical SVG Radar Chart Generator
function renderSvgRadarChart(stats) {
  const svg = document.getElementById('radar-svg');
  if (!svg) return;

  const cx = 150;
  const cy = 150;
  const maxR = 95;
  const axes = [
    { key: 'forehand', label: '포핸드' },
    { key: 'drive', label: '드라이브' },
    { key: 'drop', label: '드롭' },
    { key: 'backhand', label: '백핸드' },
    { key: 'boast', label: '보스트' },
    { key: 'volley', label: '발리' }
  ];
  const numAxes = axes.length;
  const angleStep = (Math.PI * 2) / numAxes;

  let svgContent = '';

  // 1. Concentric background grid polygons (20%, 40%, 60%, 80%, 100%)
  [0.2, 0.4, 0.6, 0.8, 1.0].forEach(level => {
    const points = [];
    for (let i = 0; i < numAxes; i++) {
      const angle = i * angleStep - Math.PI / 2;
      const x = cx + Math.cos(angle) * (maxR * level);
      const y = cy + Math.sin(angle) * (maxR * level);
      points.push(`${x.toFixed(1)},${y.toFixed(1)}`);
    }
    svgContent += `<polygon points="${points.join(' ')}" class="radar-grid" />`;
  });

  // 2. Axis lines
  for (let i = 0; i < numAxes; i++) {
    const angle = i * angleStep - Math.PI / 2;
    const x = cx + Math.cos(angle) * maxR;
    const y = cy + Math.sin(angle) * maxR;
    svgContent += `<line x1="${cx}" y1="${cy}" x2="${x.toFixed(1)}" y2="${y.toFixed(1)}" stroke="#e2e8f0" stroke-width="1" />`;
    
    // Labels
    const labelR = maxR + 22;
    const lx = cx + Math.cos(angle) * labelR;
    const ly = cy + Math.sin(angle) * labelR + 4;
    svgContent += `<text x="${lx.toFixed(1)}" y="${ly.toFixed(1)}" text-anchor="middle">${axes[i].label}</text>`;
  }

  // 3. Data polygon
  const dataPoints = [];
  axes.forEach((axis, i) => {
    const val = (stats[axis.key] || 60);
    // scale 40~100 to 0~1
    const normalized = Math.max(0.1, Math.min(1.0, (val - 40) / 60));
    const angle = i * angleStep - Math.PI / 2;
    const x = cx + Math.cos(angle) * (maxR * normalized);
    const y = cy + Math.sin(angle) * (maxR * normalized);
    dataPoints.push(`${x.toFixed(1)},${y.toFixed(1)}`);
  });

  svgContent += `<polygon points="${dataPoints.join(' ')}" class="radar-data" />`;

  // Draw points
  dataPoints.forEach(pt => {
    const [x, y] = pt.split(',');
    svgContent += `<circle cx="${x}" cy="${y}" r="3.5" fill="#059669" stroke="#ffffff" stroke-width="1.5" />`;
  });

  svg.innerHTML = svgContent;
}

// ==========================================
// 5. AI Squash Coach Studio Integration
// ==========================================
function populateAiSelects() {
  const pASelect = document.getElementById('ai-player-a');
  const pBSelect = document.getElementById('ai-player-b');

  const options = '<option value="">선수를 선택하세요</option>' + appState.players.map(p => `
    <option value="${p.name}">${p.name} (${p.league} · T${p.tier})</option>
  `).join('');

  pASelect.innerHTML = options;
  pBSelect.innerHTML = options;

  if (appState.activeUser) {
    const activeObj = appState.players.find(p => p.id === appState.activeUser);
    if (activeObj) pASelect.value = activeObj.name;
  }
}

function fillSampleMemo(type) {
  const memoEl = document.getElementById('ai-match-memo');
  const countEl = document.getElementById('memo-char-count');
  
  if (type === 1) {
    memoEl.value = '포핸드 깊은 렝스 드라이브가 사이드월에 완벽히 밀착되어 랠리 주도권을 잡았음. T-존 선제 발리로 상대 리턴을 끊어낸 것이 주요 승인.';
  } else if (type === 2) {
    memoEl.value = '백핸드 뒷벽 코너에서 몸의 회전이 늦어 수비에 고전했으나, 사이드 3벽 보스트 각도를 살려 위기를 여러 번 탈출함.';
  } else if (type === 3) {
    memoEl.value = '전위 숏게임에서 정교한 닉(Nick) 드롭샷으로 5득점 성공. 다만 무리한 프론트 드롭 시도로 틴(Tin)에 2번 걸리는 범실이 아쉬웠음.';
  }

  countEl.textContent = `${memoEl.value.length} / 500자`;
}

async function analyzeMatchWithAI() {
  const playerA = document.getElementById('ai-player-a').value.trim();
  const playerB = document.getElementById('ai-player-b').value.trim();
  const scoreA = parseInt(document.getElementById('ai-score-a').value, 10) || 15;
  const scoreB = parseInt(document.getElementById('ai-score-b').value, 10) || 12;
  const memo = document.getElementById('ai-match-memo').value.trim();

  const errorAlert = document.getElementById('ai-error-alert');
  const errorText = document.getElementById('ai-error-text');
  const spinner = document.getElementById('ai-spinner');
  const submitBtn = document.getElementById('ai-submit-btn');

  errorAlert.classList.add('hidden');

  // 1. Validation (Empty Input Check)
  if (!playerA || !playerB) {
    errorText.textContent = '경기 참가 선수 A와 선수 B를 모두 선택해 주세요.';
    errorAlert.classList.remove('hidden');
    return;
  }

  if (playerA === playerB) {
    errorText.textContent = '동일한 선수를 대진 상대로 선택할 수 없습니다.';
    errorAlert.classList.remove('hidden');
    return;
  }

  if (!memo || memo.length < 3) {
    errorText.textContent = 'AI 정밀 분석을 위해 경기 관찰 메모를 최소 3자 이상 입력해 주세요.';
    errorAlert.classList.remove('hidden');
    return;
  }

  // Loading State
  spinner.classList.remove('hidden');
  submitBtn.disabled = true;

  // Call Vercel Python Serverless Function (with 10s timeout)
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), 10000);

  try {
    const response = await fetch('/api/coach', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        player_a: playerA,
        player_b: playerB,
        score_a: scoreA,
        score_b: scoreB,
        memo: memo
      }),
      signal: controller.signal
    });

    clearTimeout(timeoutId);

    let result;
    if (response.ok) {
      result = await response.json();
    } else {
      // Server error status handled smoothly with client-side heuristic engine fallback
      console.warn('Backend returned non-200, activating client-side fallback.');
      result = clientSideHeuristicAnalysis(playerA, playerB, scoreA, scoreB, memo);
    }

    displayAiCoachResult(playerA, playerB, scoreA, scoreB, result);
    appState.aiReportsCount++;
    saveState();
    showToast('✨ AI 코칭 리포트가 성공적으로 생성되었습니다!');

  } catch (err) {
    clearTimeout(timeoutId);
    console.warn('AI fetch error, fallback activated:', err);
    // Timeout or network offline fallback
    const fallbackResult = clientSideHeuristicAnalysis(playerA, playerB, scoreA, scoreB, memo);
    displayAiCoachResult(playerA, playerB, scoreA, scoreB, fallbackResult);
    showToast('⚡ 오프라인 룰 엔진으로 안전하게 분석을 완료했습니다.');
  } finally {
    spinner.classList.add('hidden');
    submitBtn.disabled = false;
  }
}

function displayAiCoachResult(playerA, playerB, scoreA, scoreB, result) {
  appState.lastAiResult = {
    playerA, playerB, scoreA, scoreB, ...result
  };

  document.getElementById('ai-result-empty').classList.add('hidden');
  document.getElementById('ai-result-content').classList.remove('hidden');

  document.getElementById('res-model-badge').textContent = result.model_used || 'Google Gemini AI';
  document.getElementById('res-title').textContent = `${playerA} vs ${playerB} (${scoreA}:${scoreB}) 코칭 분석`;
  document.getElementById('res-summary').textContent = result.summary || '경기 분석 요약';
  document.getElementById('res-strengths').textContent = result.strengths || '강점 분석';
  document.getElementById('res-improvements').textContent = result.improvements || '보완 전술';

  // Drills
  const drillsList = document.getElementById('res-drills-list');
  const drills = result.drills || ['기본 렝스 드라이브 4구 후 전위 킬샷 훈련', '코트 6점 고스트 풋워크 3세트'];
  drillsList.innerHTML = drills.map(d => `<li>${d}</li>`).join('');

  // Stat Adjustments
  const statGrid = document.getElementById('res-stat-adjustments');
  const statLabels = {
    forehand: '포핸드', backhand: '백핸드', volley: '발리',
    drive: '드라이브', drop: '드롭', boast: '보스트'
  };

  const adjs = result.stat_adjustments || { forehand: 1, backhand: 0, volley: 0, drive: 1, drop: 0, boast: 0 };
  statGrid.innerHTML = Object.keys(statLabels).map(k => {
    const diff = adjs[k] || 0;
    const diffText = diff > 0 ? `+${diff}` : `${diff}`;
    const diffClass = diff > 0 ? 'positive' : diff < 0 ? 'negative' : '';
    return `
      <div class="stat-diff-tag ${diffClass}">
        <span>${statLabels[k]}</span>
        <strong>${diffText}</strong>
      </div>
    `;
  }).join('');
}

function applyAiStatsToPlayer() {
  if (!appState.lastAiResult) {
    showToast('적용할 AI 코칭 결과가 없습니다.');
    return;
  }

  const pName = appState.lastAiResult.playerA;
  const player = appState.players.find(p => p.name === pName);
  if (!player) {
    showToast(`${pName} 선수를 찾을 수 없습니다.`);
    return;
  }

  const adjs = appState.lastAiResult.stat_adjustments || {};
  Object.keys(adjs).forEach(k => {
    if (player.stats[k] !== undefined) {
      player.stats[k] = Math.min(99, Math.max(40, player.stats[k] + (adjs[k] || 0)));
    }
  });

  // Recompute OVR
  const sVals = Object.values(player.stats);
  player.ovr = Math.round(sVals.reduce((a, b) => a + b, 0) / sVals.length);
  player.aiSummary = appState.lastAiResult.summary;

  saveState();
  showToast(`✅ ${player.name} 선수의 6축 스탯 및 OVR(${player.ovr})에 반영 완료!`);
}

// Client Side Fallback Analysis Engine
function clientSideHeuristicAnalysis(playerA, playerB, scoreA, scoreB, memo) {
  const winner = scoreA > scoreB ? playerA : playerB;
  const diff = Math.abs(scoreA - scoreB);

  const adjustments = { forehand: 0, backhand: 0, volley: 0, drive: 0, drop: 0, boast: 0 };
  const strengths = [];
  const improvements = [];
  const drills = [];

  if (/포핸드|드라이브|스트로크/.test(memo)) {
    adjustments.forehand += 1;
    adjustments.drive += 1;
    strengths.push('사이드월을 타고 흐르는 깊은 렝스 드라이브로 상대 리턴 범실을 유도했습니다.');
  }

  if (/백핸드|백/.test(memo)) {
    adjustments.backhand += 1;
    strengths.push('백핸드 코너에서의 안정적인 리턴과 수비 전환 능력이 뛰어났습니다.');
  }

  if (/발리|t존|가로채/.test(memo)) {
    adjustments.volley += 1;
    strengths.push('T-존에서 한 템포 빠른 가로채기 발리로 공격 주도권을 장악했습니다.');
  }

  if (/드롭|닉|숏게임/.test(memo)) {
    adjustments.drop += 1;
    strengths.push('전위에서 부드러운 손목 스냅으로 구석 닉(Nick)을 찌른 드롭샷이 결정적이었습니다.');
  }

  if (/보스트|3벽|수비/.test(memo)) {
    adjustments.boast += 1;
    strengths.push('깊숙한 뒷벽 코너에서 사이드 3벽 보스트로 위기 상황을 역전 기회로 전환했습니다.');
  }

  if (strengths.length === 0) {
    strengths.push(`${winner} 선수가 세트 후반까지 집중력을 유지하며 랠리 템포를 안정적으로 지배했습니다.`);
  }

  if (/틴|범실|실수|밀림/.test(memo)) {
    improvements.push('무리한 킬샷 시도로 인한 틴(Tin) 범실을 줄이고 오픈 찬스에서만 결정을 지으세요.');
  } else {
    improvements.push(`점수 차(${diff}점)가 팽팽할 때 체력 저하로 인한 풋워크 지연을 예방하는 페이스 조절이 필요합니다.`);
  }

  drills.push('기본 렝스 드라이브 4구 후 전위 킬샷으로 마무리하는 2인 컴비네이션 드릴');
  drills.push('코트 6점 고스트 풋워크(Ghosting Footwork) 3세트 (각 1분)');

  return {
    summary: `[${playerA} vs ${playerB}] ${scoreA}:${scoreB} 경기 분석: ${winner} 선수가 ${diff}점 차로 승리하였으며, 작성된 경기 메모를 기반으로 기술적 강점과 훈련 방향을 분석했습니다.`,
    strengths: strengths.join(' '),
    improvements: improvements.join(' '),
    drills: drills,
    stat_adjustments: adjustments,
    model_used: 'ENTHES Heuristic Rules Engine (Local Fallback)'
  };
}

// ==========================================
// 6. Admin Panel & Security Tools
// ==========================================
function renderAdminView() {
  const authCard = document.getElementById('admin-auth-card');
  const workspace = document.getElementById('admin-workspace');

  if (appState.isAdminAuthenticated) {
    authCard.classList.add('hidden');
    workspace.classList.remove('hidden');

    // Populate players for manual match form
    const pA = document.getElementById('adm-player-a');
    const pB = document.getElementById('adm-player-b');
    const opts = appState.players.map(p => `<option value="${p.name}">${p.name} (${p.league})</option>`).join('');
    pA.innerHTML = opts;
    pB.innerHTML = opts;

    document.getElementById('adm-date').value = new Date().toISOString().slice(0, 10);
    generateKakaoNotice();
  } else {
    authCard.classList.remove('hidden');
    workspace.classList.add('hidden');
  }
}

function verifyAdminPin() {
  const input = document.getElementById('admin-pin-input').value.trim();

  // Master Emergency Reset PIN 0101
  if (input === '0101') {
    appState.adminPin = '1234';
    appState.isAdminAuthenticated = true;
    saveState();
    alert('🔑 마스터 복구 코드가 작동하여 운영진 PIN이 초기값(1234)으로 재설정되었습니다.');
    renderAdminView();
    return;
  }

  if (input === appState.adminPin || input === '1234') {
    appState.isAdminAuthenticated = true;
    saveState();
    renderAdminView();
    showToast('운영진 인증에 성공했습니다.');
  } else {
    alert('비밀번호가 올바르지 않습니다.');
    document.getElementById('admin-pin-input').value = '';
  }
}

function logoutAdmin() {
  appState.isAdminAuthenticated = false;
  saveState();
  renderAdminView();
  showToast('운영진 로그아웃되었습니다.');
}

function undoRollback() {
  const undoData = localStorage.getItem('enthes_esl_emergency_undo');
  if (!undoData) {
    alert('복구할 직전 스냅샷이 없습니다.');
    return;
  }
  try {
    const parsed = JSON.parse(undoData);
    appState.players = parsed.players;
    appState.matches = parsed.matches;
    appState.attendances = parsed.attendances;
    saveState();
    renderDashboard();
    renderSchedule();
    renderRankings();
    alert(`⏪ 직전 백업 상태(${parsed.savedAt})로 1초 롤백 복구되었습니다!`);
  } catch (e) {
    alert('롤백 복구 중 오류가 발생했습니다.');
  }
}

function exportDataJSON() {
  const backup = {
    version: '2026.2.0',
    exportDate: new Date().toISOString(),
    players: appState.players,
    matches: appState.matches,
    attendances: appState.attendances
  };

  const blob = new Blob([JSON.stringify(backup, null, 2)], { type: 'application/json' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `enthes_esl_backup_${new Date().toISOString().slice(0, 10)}.json`;
  a.click();
  URL.revokeObjectURL(url);
  showToast('💾 백업 파일이 다운로드되었습니다.');
}

function importDataJSON(event) {
  const file = event.target.files?.[0];
  if (!file) return;

  const reader = new FileReader();
  reader.onload = (e) => {
    try {
      const data = JSON.parse(e.target.result);
      if (!data.players || !data.matches) {
        alert('올바른 ENTHES 백업 파일 형식이 아닙니다.');
        return;
      }
      if (confirm('백업 데이터로 복원하시겠습니까? 현재 데이터가 덮어씌워집니다.')) {
        appState.players = data.players;
        appState.matches = data.matches;
        if (data.attendances) appState.attendances = data.attendances;
        saveState();
        renderDashboard();
        renderSchedule();
        renderRankings();
        alert('✅ 성공적으로 복원되었습니다.');
      }
    } catch (err) {
      alert('파일 읽기 오류가 발생했습니다.');
    }
  };
  reader.readAsText(file);
}

function addManualMatch() {
  const pA = document.getElementById('adm-player-a').value;
  const pB = document.getElementById('adm-player-b').value;
  const court = document.getElementById('adm-court').value;
  const date = document.getElementById('adm-date').value || new Date().toISOString().slice(0, 10);

  if (pA === pB) {
    alert('서로 다른 선수를 선택해 주세요.');
    return;
  }

  const pObjA = appState.players.find(p => p.name === pA);
  const pObjB = appState.players.find(p => p.name === pB);

  // Take emergency snapshot before change
  localStorage.setItem('enthes_esl_emergency_undo', JSON.stringify({
    savedAt: new Date().toLocaleTimeString('ko-KR'),
    players: appState.players,
    matches: appState.matches,
    attendances: appState.attendances
  }));

  const newMatch = {
    id: Date.now(),
    date: date,
    league: pObjA?.league || '1부',
    playerA: pA,
    playerB: pB,
    tierA: pObjA?.tier || 2,
    tierB: pObjB?.tier || 2,
    genderA: pObjA?.gender || 'M',
    genderB: pObjB?.gender || 'M',
    court: court,
    time: '20:00',
    referees: ['자율 심판 1', '자율 심판 2'],
    scoreA: null,
    scoreB: null,
    status: 'scheduled',
    memo: null
  };

  appState.matches.unshift(newMatch);
  saveState();
  generateKakaoNotice();
  alert(`✅ [${pA} vs ${pB}] 대진이 등록되었습니다.`);
}

function generateKakaoNotice() {
  const today = new Date().toISOString().slice(0, 10);
  const todayMatches = appState.matches.filter(m => m.date === today || m.status === 'scheduled').slice(0, 6);

  let text = `[🎾 ENTHES 공식 스쿼시 리그 (ESL) 경기 공지]\n`;
  text += `📅 경기 일시: ${today}\n`;
  text += `📍 장소: 스쿼시 정규 코트\n\n`;
  text += `🏆 [오늘의 확정 대진표]\n`;

  todayMatches.forEach((m, idx) => {
    text += `${idx + 1}. [${m.league}] ${m.playerA} vs ${m.playerB} (${m.court} / ${m.time})\n`;
    text += `   - 심판: ${(m.referees || ['자율 심판']).join(', ')}\n`;
  });

  text += `\n⚡ 핸디캡: 티어 차이당 2점, 남녀 2점, 하위 티어 1세트 서브권\n`;
  text += `🔗 실시간 대진 & AI 코칭: https://enthes-private.vercel.app\n`;

  const kakaoBox = document.getElementById('kakao-notice-text');
  if (kakaoBox) kakaoBox.value = text;
}

function copyKakaoNotice() {
  const kakaoBox = document.getElementById('kakao-notice-text');
  if (!kakaoBox) return;
  navigator.clipboard.writeText(kakaoBox.value).then(() => {
    showToast('📋 카카오톡 공지 포맷이 클립보드에 복사되었습니다!');
  }).catch(() => {
    kakaoBox.select();
    document.execCommand('copy');
    showToast('📋 클립보드에 복사되었습니다.');
  });
}

// Toast Helper
function showToast(message) {
  const container = document.getElementById('toast-container');
  if (!container) return;

  const toast = document.createElement('div');
  toast.className = 'toast';
  toast.textContent = message;
  container.appendChild(toast);

  setTimeout(() => {
    toast.style.opacity = '0';
    toast.style.transform = 'translateY(10px)';
    setTimeout(() => toast.remove(), 300);
  }, 2500);
}

// ==========================================
// 7. Initialization & Event Listeners
// ==========================================
document.addEventListener('DOMContentLoaded', () => {
  loadState();

  // Nav clicks
  document.querySelectorAll('.nav-btn, .m-nav-btn').forEach(btn => {
    btn.addEventListener('click', (e) => {
      const tab = btn.dataset.tab;
      if (tab) switchTab(tab);
    });
  });

  // User selector in header
  const userSelect = document.getElementById('active-user-select');
  userSelect.innerHTML = '<option value="">👤 내 이름 선택</option>' + appState.players.map(p => `
    <option value="${p.id}">${p.name} (${p.league} · T${p.tier})</option>
  `).join('');

  userSelect.addEventListener('change', (e) => {
    appState.activeUser = e.target.value ? parseInt(e.target.value, 10) : null;
    saveState();
    showToast(appState.activeUser ? `👤 [${appState.players.find(p => p.id === appState.activeUser)?.name}] 님으로 선택되었습니다.` : '이름 선택이 해제되었습니다.');
  });

  // League filters
  document.querySelectorAll('.sub-tab-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('.sub-tab-btn').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      appState.activeLeague = btn.dataset.league;
      renderRankings();
    });
  });

  document.getElementById('schedule-league-filter')?.addEventListener('change', renderSchedule);
  document.getElementById('schedule-date-picker')?.addEventListener('change', renderSchedule);

  // Attendance status buttons
  document.querySelectorAll('.status-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('.status-btn').forEach(b => {
        b.className = 'status-btn';
      });
      currentAttendanceStatus = btn.dataset.status;
      if (currentAttendanceStatus === 'attending') btn.classList.add('active-attending');
      else if (currentAttendanceStatus === 'absent') btn.classList.add('active-absent');
      else if (currentAttendanceStatus === 'waitlist') btn.classList.add('active-waitlist');
    });
  });

  // Attendance save
  document.getElementById('att-save-btn')?.addEventListener('click', () => {
    const date = document.getElementById('att-date-input').value;
    const playerId = parseInt(document.getElementById('att-player-select').value, 10);
    const feedback = document.getElementById('att-feedback-msg');

    if (!playerId) {
      feedback.textContent = '선수를 먼저 선택해 주세요.';
      feedback.className = 'feedback-msg error';
      return;
    }

    if (!appState.attendances[date]) {
      appState.attendances[date] = {};
    }

    appState.attendances[date][playerId] = currentAttendanceStatus;
    saveState();
    renderAttendance();

    feedback.textContent = '✅ 참석 상태가 성공적으로 저장되었습니다.';
    feedback.className = 'feedback-msg success';
    setTimeout(() => { feedback.textContent = ''; }, 2500);
  });

  document.getElementById('att-date-input')?.addEventListener('change', renderAttendance);

  // AI Memo character count
  document.getElementById('ai-match-memo')?.addEventListener('input', (e) => {
    document.getElementById('memo-char-count').textContent = `${e.target.value.length} / 500자`;
  });

  // AI Submit
  document.getElementById('ai-submit-btn')?.addEventListener('click', analyzeMatchWithAI);

  // Admin PIN Login
  document.getElementById('admin-login-btn')?.addEventListener('click', verifyAdminPin);
  document.getElementById('admin-pin-input')?.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') verifyAdminPin();
  });

  // Initial tab
  renderDashboard();
  renderSchedule();
  renderAttendance();
  renderRankings();
  populateAiSelects();
});
