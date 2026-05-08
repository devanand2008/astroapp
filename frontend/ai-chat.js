/**
 * JYOTISH AI Chat — Enhanced with Full Jathagam & Panchangam Data
 * ================================================================
 * Reads complete horoscope + panchangam data from localStorage
 * and sends structured context to the AI backend.
 */

// Dynamic API base — works when served from backend OR opened as file://
const API_BASE = (window.resolveJyotishApiBase || (() => {
  if (window.location.protocol === 'file:') return 'http://localhost:8080';
  const isLocal = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1';
  if (isLocal && window.location.port !== '8080') return `http://${window.location.hostname}:8080`;
  return window.location.origin;
}))();
const authToken = localStorage.getItem("auth_token");
const userInfo = JSON.parse(localStorage.getItem("user_info") || localStorage.getItem("user_data") || "null");
const chatBox = document.getElementById("chat-messages");
const typingIndicator = document.getElementById("typing-indicator");
const chatInput = document.getElementById("chat-input");

/* ── Collect ALL astrology data from localStorage ── */
function collectAstroData() {
  let cd = null;
  // Try multiple storage keys used by the main app
  const keys = ['astro_cd', 'jyotish_cd', 'CD'];
  for (const k of keys) {
    try { cd = JSON.parse(localStorage.getItem(k)); if (cd) break; } catch(e) {}
  }
  if (!cd) return null;

  // Build a comprehensive astro context object
  const ctx = {};

  // 1. Personal Info
  if (cd.input) {
    ctx.name     = cd.input.name || '';
    ctx.dob      = cd.input.dob  || '';
    ctx.time     = cd.input.time || '';
    ctx.place    = cd.input.place || '';
    ctx.gender   = cd.input.gender || '';
    ctx.father   = cd.input.father || '';
    ctx.mother   = cd.input.mother || '';
    ctx.state    = cd.input.state || '';
    ctx.district = cd.input.district || '';
    ctx.lat      = cd.input.lat;
    ctx.lon      = cd.input.lon;
  }

  // 2. Tamil Date
  if (cd.tamil_birth_date) {
    ctx.tamil_date = cd.tamil_birth_date;
  }

  // 3. Rasi & Lagna
  if (cd.moon_rasi_ta) ctx.rasi = cd.moon_rasi_ta;
  if (cd.moon_rasi_en) ctx.rasi_en = cd.moon_rasi_en;
  if (cd.lagna_ta)     ctx.lagna = cd.lagna_ta;
  if (cd.lagna_en)     ctx.lagna_en = cd.lagna_en;
  if (cd.lagna_lord_ta) ctx.lagna_lord = cd.lagna_lord_ta;

  // 4. Nakshatra
  if (cd.nakshatra) {
    ctx.nakshatra    = cd.nakshatra.ta || cd.nakshatra.en || '';
    ctx.nakshatra_en = cd.nakshatra.en || '';
    ctx.nakshatra_lord = cd.nakshatra.lord_ta || '';
    ctx.pada         = cd.nakshatra.pada || '';
  }

  // 5. All Planets
  if (cd.planets && Array.isArray(cd.planets)) {
    ctx.planets = cd.planets.map(p => ({
      name:   p.ta  || p.name || '',
      rasi:   p.rasi_ta || '',
      degree: p.deg_str || '',
      status: p.status  || '',
      navamsa: p.nav_rasi_ta || ''
    }));
  }

  // 6. Current Dasha & Bhukti
  if (cd.dasa) {
    const cur = cd.dasa.current;
    const buk = cd.dasa.current_bhukti;
    ctx.current_dasa  = cur ? (cur.ta + ' (' + cur.start + ' → ' + cur.end + ')') : '';
    ctx.current_bhukti = buk ? (buk.ta + ' (' + buk.start + ' → ' + buk.end + ')') : '';
    ctx.dasa_remaining = cd.dasa.remaining_yrs || '';
    // All dashas
    if (cd.dasa.all) {
      ctx.all_dashas = cd.dasa.all.map(d => d.ta + ': ' + d.start + '→' + d.end).join(', ');
    }
  }

  // 7. Day-by-day Dasha
  if (cd.dasa_days) {
    const cur = cd.dasa_days.all ? cd.dasa_days.all.find(d => d.is_current) : null;
    if (cur) ctx.dasa_days_remaining = cur.days_remaining + ' நாட்கள் மீதம்';
    if (cd.dasa_days.bhukti_detailed) {
      const curB = cd.dasa_days.bhukti_detailed.find(b => b.is_current);
      if (curB) ctx.bhukti_days_remaining = curB.days_remaining + ' நாட்கள்';
    }
  }

  // 8. Birth Panchangam
  if (cd.birth_panchangam) {
    const pj = cd.birth_panchangam;
    ctx.birth_tithi     = pj.tithi   || '';
    ctx.birth_vara      = pj.vara    || '';
    ctx.birth_nakshatra = pj.nakshatra || '';
    ctx.birth_yoga      = pj.yoga    || '';
    ctx.birth_karana    = pj.karana  || '';
    ctx.birth_rahu_kalam= pj.rahu_kalam || '';
  }

  // 9. Sunrise/Sunset at birth
  if (cd.birth_rise_set) {
    const rs = cd.birth_rise_set;
    ctx.sunrise  = rs.sunrise  || '';
    ctx.sunset   = rs.sunset   || '';
    ctx.moonrise = rs.moonrise || '';
    ctx.moonset  = rs.moonset  || '';
  }

  // 10. Today's Panchangam (if cached)
  try {
    const todayPj = JSON.parse(localStorage.getItem('today_panchangam'));
    if (todayPj) {
      ctx.today_tithi     = todayPj.tithi    || '';
      ctx.today_vara      = todayPj.vara     || '';
      ctx.today_nakshatra = todayPj.nakshatra|| '';
      ctx.today_yoga      = todayPj.yoga     || '';
      ctx.today_rahu_kalam= todayPj.rahu_kalam || '';
      ctx.today_sunrise   = todayPj.sunrise  || '';
      ctx.today_sunset    = todayPj.sunset   || '';
    }
  } catch(e) {}

  return ctx;
}

/* ── Quick answer from local data without API ── */
function quickLocalAnswer(question) {
  const cd = collectAstroData();
  if (!cd) return null;
  const q = question.toLowerCase();

  // Rasi questions
  if (q.includes('ராசி') || q.includes('rasi') || q.includes('moon sign')) {
    return `🌙 உங்கள் **ராசி**: ${cd.rasi || '—'} (${cd.rasi_en || ''})\n👑 ராசி அதிபதி: ${cd.lagna_lord || '—'}`;
  }

  // Lagna
  if (q.includes('லக்னம்') || q.includes('lagna') || q.includes('ascendant')) {
    return `⬆ உங்கள் **லக்னம்**: ${cd.lagna || '—'} (${cd.lagna_en || ''})\n👑 லக்னாதிபதி: ${cd.lagna_lord || '—'}`;
  }

  // Nakshatra
  if (q.includes('நட்சத்திரம்') || q.includes('nakshatra') || q.includes('star')) {
    return `⭐ உங்கள் **நட்சத்திரம்**: ${cd.nakshatra || '—'} (${cd.nakshatra_en || ''})\n📍 பாதம்: ${cd.pada || '—'} · நட்சத்திர அதிபதி: ${cd.nakshatra_lord || '—'}`;
  }

  // Dasha
  if (q.includes('தசை') || q.includes('தசா') || q.includes('dasa') || q.includes('dasha')) {
    let ans = `⏳ தற்போதைய **தசை**: ${cd.current_dasa || '—'}\n🔸 புக்தி: ${cd.current_bhukti || '—'}`;
    if (cd.dasa_days_remaining) ans += `\n📅 மீதமுள்ள நாட்கள்: ${cd.dasa_days_remaining}`;
    if (cd.dasa_remaining) ans += `\n⌛ மொத்த மீதம்: ${cd.dasa_remaining} வருடங்கள்`;
    return ans;
  }

  // Panchangam today
  if (q.includes('பஞ்சாங்கம்') || q.includes('panchangam') || q.includes('இன்று') || q.includes('today')) {
    if (cd.today_tithi) {
      return `📅 **இன்றைய பஞ்சாங்கம்**:\n🌙 திதி: ${cd.today_tithi}\n📆 வாரம்: ${cd.today_vara}\n⭐ நட்சத்திரம்: ${cd.today_nakshatra}\n🪐 யோகம்: ${cd.today_yoga}\n⛔ ராகு காலம்: ${cd.today_rahu_kalam}\n☀ சூரிய உதயம்: ${cd.today_sunrise} · அஸ்தமனம்: ${cd.today_sunset}`;
    }
  }

  // Sunrise
  if (q.includes('சூரிய') || q.includes('sunrise') || q.includes('sunset')) {
    return `☀ **பிறந்த நாள் சூரிய நிலை**:\n🌅 உதயம்: ${cd.sunrise || '—'}\n🌇 அஸ்தமனம்: ${cd.sunset || '—'}\n🌙 சந்திர உதயம்: ${cd.moonrise || '—'}\n🌑 சந்திர அஸ்தமனம்: ${cd.moonset || '—'}`;
  }

  // Planets
  if (q.includes('கிரகம்') || q.includes('planet') || q.includes('கோள்')) {
    if (cd.planets && cd.planets.length) {
      const lines = cd.planets.map(p => `${p.name}: ${p.rasi} (${p.degree})${p.status?' · '+p.status:''}`);
      return `🪐 **கிரக நிலைகள்**:\n${lines.join('\n')}`;
    }
  }

  // Birth panchangam
  if (q.includes('பிறந்த') || q.includes('birth') || q.includes('திதி')) {
    if (cd.birth_tithi) {
      return `📜 **பிறப்பு பஞ்சாங்கம்**:\n🌙 திதி: ${cd.birth_tithi}\n📆 வாரம்: ${cd.birth_vara}\n⭐ நட்சத்திரம்: ${cd.birth_nakshatra}\n🪐 யோகம்: ${cd.birth_yoga}\n🔸 கரணம்: ${cd.birth_karana}`;
    }
  }

  return null; // Let API handle
}

/* ── Format astro_data for API call ── */
function buildApiPayload(question) {
  const cd = collectAstroData();
  return {
    message: question,
    astro_data: cd || {}
  };
}

/* ── History ── */
let aiHistory = [];
try {
  aiHistory = JSON.parse(localStorage.getItem('ai_chat_history_page') || '[]');
} catch(e) { aiHistory = []; }

function renderHistory() {
  if (aiHistory.length > 0) {
    document.getElementById("welcome-card").style.display = "none";
    aiHistory.forEach(msg => appendMessage(msg, false));
    scrollToBottom();
  }
  // Show jathagam loaded badge
  const cd = collectAstroData();
  if (cd && cd.name) showDataBadge(cd);
}

function showDataBadge(cd) {
  const badge = document.createElement('div');
  badge.style.cssText = 'background:rgba(29,140,104,.1);border:1px solid rgba(29,140,104,.25);border-radius:10px;padding:8px 12px;text-align:center;font-size:11px;color:#1D8C68;margin-bottom:8px;';
  badge.innerHTML = `📋 <strong>${cd.name}</strong> இன் ஜாதகம் ஏற்றப்பட்டது · ராசி: ${cd.rasi||'—'} · நட்சத்திரம்: ${cd.nakshatra||'—'}`;
  chatBox.insertBefore(badge, typingIndicator);
}

function appendMessage(msg, scroll=true) {
  const isUser = msg.sender_id !== 'AI';
  const bubble = document.createElement("div");
  bubble.className = `msg-bubble ${isUser ? 'sent' : 'recv'}`;
  const timeStr = new Date(msg.timestamp).toLocaleTimeString([], {hour:'2-digit',minute:'2-digit'});
  // Render markdown-like bold
  const content = (msg.content || '').replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>').replace(/\n/g,'<br>');
  bubble.innerHTML = `<div class="msg-content">${isUser ? escapeHTML(msg.content) : content}</div><div class="msg-time">${timeStr}</div>`;
  chatBox.insertBefore(bubble, typingIndicator);
  if (scroll) scrollToBottom();
}

function escapeHTML(str) {
  return (str||'').replace(/[&<>'"]/g, tag => ({'&':'&amp;','<':'&lt;','>':'&gt;',"'":'&#39;','"':'&quot;'}[tag]));
}

function scrollToBottom() { chatBox.scrollTop = chatBox.scrollHeight; }

function handleKey(e) {
  if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); sendMessage(); }
}

/* ── Quick suggestion chips ── */
function injectQuickChips() {
  const cd = collectAstroData();
  const chips = cd ? [
    `என் ராசி என்ன?`,
    `தற்போது என் தசை?`,
    `இன்றைய பஞ்சாங்கம்`,
    `கிரக நிலைகள்`,
    `திருமண யோகம்`,
    `பணம் வருமா?`,
    `உடல் நலம் எப்படி?`,
    `பிறந்த நட்சத்திரம்`
  ] : [`ஜாதகம் கணக்கிட செல்ல`, `AI பற்றி`];

  const wrap = document.createElement('div');
  wrap.id = 'quick-chips';
  wrap.style.cssText = 'display:flex;flex-wrap:wrap;gap:8px;padding:8px 16px;border-top:1px solid var(--bdr,#322C58);background:var(--surf,#16132A);';
  chips.forEach(chip => {
    const btn = document.createElement('button');
    btn.textContent = chip;
    btn.style.cssText = 'padding:6px 12px;background:rgba(139,111,224,.12);border:1px solid rgba(139,111,224,.3);border-radius:20px;color:#EAE6FC;font-size:11px;cursor:pointer;font-family:inherit;transition:.2s;';
    btn.onmouseenter = ()=>{ btn.style.background='rgba(139,111,224,.25)'; };
    btn.onmouseleave = ()=>{ btn.style.background='rgba(139,111,224,.12)'; };
    btn.onclick = () => {
      chatInput.value = chip;
      sendMessage();
    };
    wrap.appendChild(btn);
  });
  document.querySelector('.input-area').before(wrap);
}

/* ── Main send function ── */
async function sendMessage() {
  const text = chatInput.value.trim();
  if (!text) return;

  document.getElementById("welcome-card").style.display = "none";
  document.getElementById("quick-chips")?.remove();

  const userMsg = {
    sender_id: userInfo ? userInfo.id : 'User',
    receiver_id: 'AI',
    content: text,
    timestamp: new Date().toISOString()
  };
  appendMessage(userMsg);
  aiHistory.push(userMsg);
  localStorage.setItem('ai_chat_history_page', JSON.stringify(aiHistory.slice(-100)));
  chatInput.value = '';
  chatInput.style.height = 'auto';

  typingIndicator.style.display = 'flex';
  scrollToBottom();

  // 1. Try quick local answer first (instant, no API call needed)
  const localAnswer = quickLocalAnswer(text);
  if (localAnswer) {
    await new Promise(r => setTimeout(r, 600)); // natural delay
    typingIndicator.style.display = 'none';
    const aiMsg = { sender_id:'AI', receiver_id: userInfo?.id||'User', content:localAnswer, timestamp:new Date().toISOString() };
    appendMessage(aiMsg);
    aiHistory.push(aiMsg);
    localStorage.setItem('ai_chat_history_page', JSON.stringify(aiHistory.slice(-100)));
    return;
  }

  // 2. Full API call with complete astro context
  try {
    const payload = buildApiPayload(text);
    const aiUrl = authToken
      ? `${API_BASE}/api/chat/ai?token=${encodeURIComponent(authToken)}`
      : `${API_BASE}/api/chat/ai-public`;
    const res = await fetch(aiUrl, {
      method: 'POST',
      headers: {'Content-Type':'application/json'},
      body: JSON.stringify(payload)
    });
    if (!res.ok) throw new Error("API Error " + res.status);
    const data = await res.json();
    typingIndicator.style.display = 'none';
    const aiMsg = { sender_id:'AI', receiver_id:userInfo?.id||'User', content:data.reply, timestamp:new Date().toISOString() };
    appendMessage(aiMsg);
    aiHistory.push(aiMsg);
    localStorage.setItem('ai_chat_history_page', JSON.stringify(aiHistory.slice(-100)));
  } catch(err) {
    typingIndicator.style.display = 'none';
    // Fallback with data we have
    const cd = collectAstroData();
    let fallback = '⚠ AI Server-உடன் இணைய முடியவில்லை. உங்கள் ஜாதக விவரங்கள்:\n';
    if (cd) {
      if (cd.rasi)      fallback += `\n🌙 ராசி: ${cd.rasi}`;
      if (cd.nakshatra) fallback += `\n⭐ நட்சத்திரம்: ${cd.nakshatra}`;
      if (cd.current_dasa) fallback += `\n⏳ தசை: ${cd.current_dasa}`;
    }
    fallback += '\n\n(Backend சர்வர் இயங்குகிறதா என சரிபாருங்கள்)';
    const aiMsg = { sender_id:'AI', receiver_id:userInfo?.id||'User', content:fallback, timestamp:new Date().toISOString() };
    appendMessage(aiMsg);
  }
}

// Check token
if (!authToken) {
  location.href = 'login.html';
}

// Init
renderHistory();
injectQuickChips();
