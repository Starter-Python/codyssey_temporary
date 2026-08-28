/* Design reminder: 조용한 회복의 편집실 — 사용자는 AI의 처방을 받지 않고, 자신의 루틴 초안을 편집한다. */
const form = document.querySelector('#routine-form');
const message = document.querySelector('#form-message');
const submitButton = document.querySelector('#submit-button');
const note = document.querySelector('#note');
const charCount = document.querySelector('#char-count');
const resultEmpty = document.querySelector('#result-empty');
const resultContent = document.querySelector('#result-content');
const themeToggle = document.querySelector('.theme-toggle');
const menuToggle = document.querySelector('.menu-toggle');
const mainNav = document.querySelector('.main-nav');

const escapeText = (value) => String(value || '').replace(/[<>]/g, '');

function setMessage(text, type = '') {
  message.textContent = text;
  message.className = `form-message ${type}`;
}

function showResult(data) {
  document.querySelector('#result-kicker').textContent = escapeText(data.kicker || '오늘의 작은 계획');
  document.querySelector('#result-title').textContent = escapeText(data.title || '당신의 회복 루틴');
  document.querySelector('#result-opening').textContent = escapeText(data.opening || '지금 가능한 만큼만 시작해 보세요.');
  document.querySelector('#result-note').textContent = escapeText(data.note || '가장 쉬운 단계 하나만 골라도 충분합니다.');
  const steps = document.querySelector('#result-steps');
  steps.replaceChildren();
  (Array.isArray(data.steps) ? data.steps.slice(0, 3) : []).forEach((step) => {
    const item = document.createElement('li');
    item.textContent = escapeText(step);
    steps.appendChild(item);
  });
  if (!steps.children.length) {
    ['창가에서 숨을 천천히 세 번 고릅니다.', '지금 할 수 있는 가장 작은 행동을 하나만 적습니다.', '다음 10분에는 그 행동만 해봅니다.'].forEach((step) => {
      const item = document.createElement('li'); item.textContent = step; steps.appendChild(item);
    });
  }
  resultEmpty.hidden = true;
  resultContent.hidden = false;
  resultContent.focus?.();
}

async function requestRoutine(payload) {
  const controller = new AbortController();
  const timeout = window.setTimeout(() => controller.abort(), 12000);
  try {
    const response = await fetch('/api/recommend', {
      method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload), signal: controller.signal,
    });
    const body = await response.json().catch(() => ({}));
    if (!response.ok) {
      const previewNotice = response.status === 404
        ? 'AI 서버를 찾지 못했습니다. Vercel에서 `AI 활용 학습 A1-3`을 Root Directory로 설정한 뒤 다시 배포해 주세요.'
        : '루틴을 만드는 중 문제가 발생했습니다.';
      throw new Error(body.error || previewNotice);
    }
    return body;
  } finally { window.clearTimeout(timeout); }
}

form.addEventListener('submit', async (event) => {
  event.preventDefault();
  const values = Object.fromEntries(new FormData(form).entries());
  if (!values.feeling || !values.minutes || !values.focus) {
    setMessage('현재 상태, 시간, 원하는 감각을 모두 골라주세요.');
    const firstMissing = !values.feeling ? document.querySelector('#feeling') : (!values.minutes ? document.querySelector('#time-5') : document.querySelector('#focus'));
    firstMissing.focus();
    return;
  }
  setMessage('당신의 오늘을 천천히 읽고 있습니다…', 'success');
  submitButton.disabled = true;
  submitButton.innerHTML = '루틴을 정리하는 중 <span class="loading-dots" aria-hidden="true">···</span>';
  try {
    const response = await requestRoutine(values);
    showResult(response);
    setMessage('오늘의 루틴 초안을 만들었습니다. 필요한 만큼만 가져가세요.', 'success');
    document.querySelector('.result-panel').scrollIntoView({ behavior: 'smooth', block: 'nearest' });
  } catch (error) {
    const isTimeout = error.name === 'AbortError';
    setMessage(isTimeout ? '응답이 조금 늦어지고 있습니다. 잠시 후 다시 시도해 주세요.' : (error.message || '연결에 문제가 있습니다. 잠시 후 다시 시도해 주세요.'));
  } finally {
    submitButton.disabled = false;
    submitButton.innerHTML = '오늘의 루틴 초안 받기 <span aria-hidden="true">↘</span>';
  }
});

note.addEventListener('input', () => { charCount.textContent = note.value.length; });
document.querySelector('#reset-button').addEventListener('click', () => { form.reset(); charCount.textContent = '0'; resultContent.hidden = true; resultEmpty.hidden = false; setMessage(''); document.querySelector('#feeling').focus(); });

themeToggle.addEventListener('click', () => {
  const enabled = document.body.classList.toggle('dark-mode');
  themeToggle.setAttribute('aria-pressed', String(enabled));
  themeToggle.setAttribute('aria-label', enabled ? '밝은 화면으로 전환' : '어두운 화면으로 전환');
  localStorage.setItem('ongirok-dark-mode', enabled ? 'true' : 'false');
});
if (localStorage.getItem('ongirok-dark-mode') === 'true') themeToggle.click();

menuToggle.addEventListener('click', () => { const open = mainNav.classList.toggle('is-open'); menuToggle.setAttribute('aria-expanded', String(open)); menuToggle.setAttribute('aria-label', open ? '메뉴 닫기' : '메뉴 열기'); });
mainNav.querySelectorAll('a').forEach((link) => link.addEventListener('click', () => { mainNav.classList.remove('is-open'); menuToggle.setAttribute('aria-expanded', 'false'); }));

const revealObserver = new IntersectionObserver((entries) => { entries.forEach((entry) => { if (entry.isIntersecting) { entry.target.classList.add('is-visible'); revealObserver.unobserve(entry.target); } }); }, { threshold: .12 });
document.querySelectorAll('.reveal').forEach((element) => revealObserver.observe(element));
