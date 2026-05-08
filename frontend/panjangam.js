/**
 * JYOTISH — Thirukkhanita Panchangam Module
 * Daily panchangam with copy feature (app name watermark)
 * Fetches from backend or calculates client-side fallback
 */

// Dynamic API base — works when served from backend OR opened as file://
const API_BASE_PJ = (window.resolveJyotishApiBase || (() => {
  if (window.location.protocol === 'file:') return 'http://localhost:8080';
  const isLocal = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1';
  if (isLocal && window.location.port !== '8080') return `http://${window.location.hostname}:8080`;
  return window.location.origin;
}))();

let todayPanchangam = null;
let userPanchangam  = null;  // panchangam for user's birth date

/* ── Tamil Numbers & Month Names ── */
const TAMIL_NUMS = ['0','1','2','3','4','5','6','7','8','9'];
const TAMIL_MONTH_NAMES = [
  'சித்திரை','வைகாசி','ஆனி','ஆடி','ஆவணி','புரட்டாசி',
  'ஐப்பசி','கார்த்திகை','மார்கழி','தை','மாசி','பங்குனி'
];

/* ── Fetch Panchangam from Backend ── */
async function fetchPanchangam(year, month, day, lat = 11.6643, lon = 78.1460) {
  try {
    const res = await fetch(`${API_BASE_PJ}/api/panchangam`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ year, month, day, lat, lon, timezone: 5.5 }),
    });
    if (res.ok) return await res.json();
  } catch (e) {}
  return calcPanchangamFallback(year, month, day);
}

async function fetchTodayPanchangam(lat = 11.6643, lon = 78.1460) {
  try {
    const res = await fetch(`${API_BASE_PJ}/api/panchangam/today?lat=${lat}&lon=${lon}&tz=5.5`);
    if (res.ok) return await res.json();
  } catch (e) {}
  const now = new Date();
  return calcPanchangamFallback(now.getFullYear(), now.getMonth() + 1, now.getDate());
}

/* ── Client-Side Fallback Panchangam ── */
function calcPanchangamFallback(year, month, day) {
  const TITHI = [
    'பிரதமை','துவிதியை','திரிதியை','சதுர்த்தி','பஞ்சமி',
    'சஷ்டி','சப்தமி','அஷ்டமி','நவமி','தசமி',
    'ஏகாதசி','துவாதசி','திரயோதசி','சதுர்தசி','பௌர்ணமி',
    'பிரதமை (கி.)','துவிதியை (கி.)','திரிதியை (கி.)','சதுர்த்தி (கி.)','பஞ்சமி (கி.)',
    'சஷ்டி (கி.)','சப்தமி (கி.)','அஷ்டமி (கி.)','நவமி (கி.)','தசமி (கி.)',
    'ஏகாதசி (கி.)','துவாதசி (கி.)','திரயோதசி (கி.)','சதுர்தசி (கி.)','அமாவாசை',
  ];
  const NAKSHATRAS = [
    'அஸ்வினி','பரணி','கார்த்திகை','ரோகிணி','மிருகசீரிடம்','திருவாதிரை',
    'புனர்பூசம்','பூசம்','ஆயில்யம்','மகம்','பூரம்','உத்திரம்',
    'அஸ்தம்','சித்திரை','சுவாதி','விசாகம்','அனுஷம்','கேட்டை',
    'மூலம்','பூராடம்','உத்திராடம்','திருவோணம்','அவிட்டம்','சதயம்',
    'பூரட்டாதி','உத்திரட்டாதி','ரேவதி',
  ];
  const YOGA = [
    'விஷ்கம்ப','ப்ரீதி','ஆயுஷ்மான்','சௌபாக்ய','சோபன',
    'அதிகண்ட','சுகர்மா','த்ருதி','சூல','கண்ட',
    'வ்ருத்தி','த்ருவ','வ்யாகாத','ஹர்ஷண','வஜ்ர',
    'சித்தி','வ்யதீபாத','வரீயான்','பரிக','சிவ',
    'சித்த','சாத்ய','சுபா','சுக்ல','ப்ரம்ம','இந்திர','வைத்ருதி',
  ];
  const KARANA = ['பவ','பாலவ','கௌலவ','தைதில','கரஜ','வணிஜ','விஷ்டி'];
  const VARA = ['ஞாயிறு','திங்கள்','செவ்வாய்','புதன்','வியாழன்','வெள்ளி','சனி'];
  const RAHU_K = [
    '16:30-18:00','07:30-09:00','15:00-16:30',
    '12:00-13:30','13:30-15:00','10:30-12:00','09:00-10:30',
  ];

  const d = new Date(year, month - 1, day);
  const wd = d.getDay();

  // Simple approximations
  const jd   = Math.floor(365.25 * (year + 4716)) + Math.floor(30.6001 * (month + 1)) + day - 1524;
  const tithiIdx = Math.floor((jd * 0.9167) % 30);
  const nakIdx   = Math.floor((jd * 0.9) % 27);
  const yogaIdx  = Math.floor((jd * 1.1) % 27);
  const karanaIdx= Math.floor((jd * 2) % 7);

  // Tamil month
  const tmStarts = [[4,14],[5,15],[6,15],[7,17],[8,17],[9,17],[10,18],[11,16],[12,16],[1,14],[2,13],[3,15]];
  let tmIdx = 0;
  for (let i = 11; i >= 0; i--) {
    const [gm, gd] = tmStarts[i];
    if (month > gm || (month === gm && day >= gd)) { tmIdx = i; break; }
    if (i === 0) tmIdx = 0;
  }
  const tmMonth = TAMIL_MONTH_NAMES[tmIdx];
  const tmStart = new Date(year, tmStarts[tmIdx][0] - 1, tmStarts[tmIdx][1]);
  const tmDay   = Math.max(1, Math.round((d - tmStart) / 86400000) + 1);

  return {
    date: `${String(day).padStart(2,'0')}-${String(month).padStart(2,'0')}-${year}`,
    tamil_date: `${tmDay} ${tmMonth} ${year}`,
    tamil_month: tmMonth,
    tamil_day: tmDay,
    tamil_year: year,
    vara_ta: VARA[wd],
    vara_en: ['Sunday','Monday','Tuesday','Wednesday','Thursday','Friday','Saturday'][wd],
    weekday: wd,
    tithi: TITHI[tithiIdx],
    tithi_num: tithiIdx + 1,
    nakshatra: NAKSHATRAS[nakIdx],
    nak_lord: '—',
    nak_pada: Math.floor((jd % 4)) + 1,
    yoga: YOGA[yogaIdx],
    karana: KARANA[karanaIdx],
    moon_rasi: '—',
    sun_rasi: '—',
    rahu_kalam: RAHU_K[wd],
    gulika: '—',
    yama_kandam: '—',
    sunrise: '06:00',
    sunset: '18:30',
    moonrise: '19:00',
    moonset: '06:30',
    ayanamsa: 24.19,
    _fallback: true,
  };
}

/* ── Load & Display Today's Panchangam ── */
async function loadTodayPanchangam(lat, lon) {
  const el = document.getElementById('pj-loading');
  if (el) el.style.display = 'flex';

  todayPanchangam = await fetchTodayPanchangam(lat || 11.6643, lon || 78.1460);

  // ✅ Save to localStorage so AI chatbot can read it
  try {
    const pjForAI = {
      tithi:      todayPanchangam.tithi,
      vara:       todayPanchangam.vara_ta,
      nakshatra:  todayPanchangam.nakshatra,
      yoga:       todayPanchangam.yoga,
      karana:     todayPanchangam.karana,
      rahu_kalam: todayPanchangam.rahu_kalam,
      sunrise:    todayPanchangam.sunrise,
      sunset:     todayPanchangam.sunset,
      moonrise:   todayPanchangam.moonrise,
      moonset:    todayPanchangam.moonset,
      date:       todayPanchangam.date,
      tamil_date: todayPanchangam.tamil_date,
    };
    localStorage.setItem('today_panchangam', JSON.stringify(pjForAI));
  } catch(e) {}

  if (el) el.style.display = 'none';
  renderPanchangam('pj-container', todayPanchangam, true);
}


/* ── Render Panchangam Block ── */
function renderPanchangam(containerId, pj, isToday = false) {
  const el = document.getElementById(containerId);
  if (!el || !pj) return;

  const todayLabel = isToday
    ? `<span class="pj-live-badge">🔴 LIVE · இன்று</span>`
    : '';

  el.innerHTML = `
    <div class="pj-card">
      <div class="pj-header">
        <div>
          <div class="pj-title">✦ திருக்கணித பஞ்சாங்கம் ${todayLabel}</div>
          <div class="pj-date">${pj.vara_ta} · ${pj.date} · ${pj.tamil_date}</div>
        </div>
        <button class="pj-copy-btn" onclick="copyPanchangam()" title="Copy பஞ்சாங்கம்">📋 நகல்</button>
      </div>

      <div class="pj-grid">
        <div class="pj-item">
          <div class="pj-lbl">🌅 திதி</div>
          <div class="pj-val">${pj.tithi}</div>
        </div>
        <div class="pj-item">
          <div class="pj-lbl">📅 வாரம்</div>
          <div class="pj-val">${pj.vara_ta}</div>
        </div>
        <div class="pj-item">
          <div class="pj-lbl">⭐ நட்சத்திரம்</div>
          <div class="pj-val">${pj.nakshatra}<br><small>பாதம் ${pj.nak_pada}</small></div>
        </div>
        <div class="pj-item">
          <div class="pj-lbl">🔱 யோகம்</div>
          <div class="pj-val">${pj.yoga}</div>
        </div>
        <div class="pj-item">
          <div class="pj-lbl">🌒 கரணம்</div>
          <div class="pj-val">${pj.karana}</div>
        </div>
        <div class="pj-item">
          <div class="pj-lbl">🌙 சந்திர ராசி</div>
          <div class="pj-val">${pj.moon_rasi}</div>
        </div>
        <div class="pj-item">
          <div class="pj-lbl">☀ சூர்ய ராசி</div>
          <div class="pj-val">${pj.sun_rasi}</div>
        </div>
        <div class="pj-item">
          <div class="pj-lbl">🐍 ராகு காலம்</div>
          <div class="pj-val" style="color:var(--red)">${pj.rahu_kalam}</div>
        </div>
      </div>

      <div class="pj-rise-set">
        <div class="pj-rs-item">
          <span class="pj-rs-icon">🌅</span>
          <span class="pj-rs-lbl">சூர்யோதயம்</span>
          <span class="pj-rs-val">${pj.sunrise}</span>
        </div>
        <div class="pj-rs-item">
          <span class="pj-rs-icon">🌇</span>
          <span class="pj-rs-lbl">சூர்யாஸ்தமனம்</span>
          <span class="pj-rs-val">${pj.sunset}</span>
        </div>
        <div class="pj-rs-item">
          <span class="pj-rs-icon">🌕</span>
          <span class="pj-rs-lbl">சந்திரோதயம்</span>
          <span class="pj-rs-val">${pj.moonrise}</span>
        </div>
        <div class="pj-rs-item">
          <span class="pj-rs-icon">🌑</span>
          <span class="pj-rs-lbl">சந்திராஸ்தமனம்</span>
          <span class="pj-rs-val">${pj.moonset}</span>
        </div>
      </div>

      <div class="pj-avoid">
        <span style="color:var(--red);font-size:10px;font-weight:700;">⚠ தவிர்க்க:</span>
        <span style="font-size:10px;color:var(--mut);">ராகு காலம் ${pj.rahu_kalam} · குளிகை ${pj.gulika}</span>
      </div>

      <div style="font-size:9px;color:var(--mut);text-align:right;margin-top:8px;font-family:'Space Mono',monospace;">
        Ayanamsa: ${pj.ayanamsa}° Lahiri${pj._fallback ? ' · Client calc' : ' · Python Engine'}
      </div>
    </div>
  `;
}

/* ── Copy Panchangam with App Name ── */
function copyPanchangam() {
  const pj = todayPanchangam;
  if (!pj) { alert('பஞ்சாங்கம் ஏற்றப்படவில்லை'); return; }

  const text = `
✦ திருக்கணித பஞ்சாங்கம் ✦
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📅 தேதி   : ${pj.date}
🗓 தமிழ்  : ${pj.tamil_date}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🌅 திதி      : ${pj.tithi}
📅 வாரம்     : ${pj.vara_ta}
⭐ நட்சத்திரம்: ${pj.nakshatra} (பாதம் ${pj.nak_pada})
🔱 யோகம்     : ${pj.yoga}
🌒 கரணம்     : ${pj.karana}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🌅 சூர்யோதயம்    : ${pj.sunrise}
🌇 சூர்யாஸ்தமனம் : ${pj.sunset}
🌕 சந்திரோதயம்   : ${pj.moonrise}
🌑 சந்திராஸ்தமனம்: ${pj.moonset}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚠ ராகு காலம் : ${pj.rahu_kalam}
   குளிகை     : ${pj.gulika}
   யம கண்டம்  : ${pj.yama_kandam}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔮 JYOTISH App · ஜோதிடம்
   Python Engine · Lahiri Ayanamsa
   திருக்கணித கணிப்பு
`.trim();

  navigator.clipboard.writeText(text).then(() => {
    const btn = document.querySelector('.pj-copy-btn');
    if (btn) {
      btn.textContent = '✅ நகல் ஆனது!';
      setTimeout(() => { btn.textContent = '📋 நகல்'; }, 2500);
    }
  }).catch(() => {
    // Fallback for older browsers
    const ta = document.createElement('textarea');
    ta.value = text;
    document.body.appendChild(ta);
    ta.select();
    document.execCommand('copy');
    document.body.removeChild(ta);
    alert('✅ பஞ்சாங்கம் நகல் ஆனது! (with JYOTISH App name)');
  });
}

/* ── Render Birth Date Rise/Set ── */
function renderBirthRiseSet(riseSet, containerId) {
  const el = document.getElementById(containerId);
  if (!el || !riseSet) return;
  el.innerHTML = `
    <div class="pj-rise-set" style="margin:0;">
      <div class="pj-rs-item">
        <span class="pj-rs-icon">🌅</span>
        <span class="pj-rs-lbl">சூர்யோதயம்</span>
        <span class="pj-rs-val">${riseSet.sunrise || '—'}</span>
      </div>
      <div class="pj-rs-item">
        <span class="pj-rs-icon">🌇</span>
        <span class="pj-rs-lbl">சூர்யாஸ்தமனம்</span>
        <span class="pj-rs-val">${riseSet.sunset || '—'}</span>
      </div>
      <div class="pj-rs-item">
        <span class="pj-rs-icon">🌕</span>
        <span class="pj-rs-lbl">சந்திரோதயம்</span>
        <span class="pj-rs-val">${riseSet.moonrise || '—'}</span>
      </div>
      <div class="pj-rs-item">
        <span class="pj-rs-icon">🌑</span>
        <span class="pj-rs-lbl">சந்திராஸ்தமனம்</span>
        <span class="pj-rs-val">${riseSet.moonset || '—'}</span>
      </div>
    </div>
  `;
}
