"""Quick test script for the astro engine and all key API functions."""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.path.insert(0, 'd:/astro app 3.0 web/backend')

from astro_engine import (
    tamil_date_from_gregorian, generate_horoscope,
    calc_panchangam, calc_rise_set, calc_dasa_with_days
)

PASS = 0
FAIL = 0

def check(label, got, expected):
    global PASS, FAIL
    if got == expected:
        print(f"  [OK]   {label}: {got}")
        PASS += 1
    else:
        print(f"  [FAIL] {label}: got={got!r}  expected={expected!r}")
        FAIL += 1

# ── Tamil Date Edge Cases ────────────────────────────────────────────
print("\n=== Tamil Date Tests ===")
td_tests = [
    (2026,  1,  5, "மார்கழி"),   # Jan  5  → before தை (Jan 14)
    (2026,  1, 14, "தை"),         # Jan 14  → first day of தை
    (2026,  2, 12, "தை"),         # Feb 12  → still தை (மாசி starts Feb 13)
    (2026,  2, 13, "மாசி"),       # Feb 13  → first day of மாசி
    (2026,  3, 14, "மாசி"),       # Mar 14  → still மாசி (பங்குனி starts Mar 15)
    (2026,  3, 15, "பங்குனி"),    # Mar 15  → first day of பங்குனி
    (2026,  4, 13, "பங்குனி"),    # Apr 13  → still பங்குனி (new year Apr 14)
    (2026,  4, 14, "சித்திரை"),   # Apr 14  → Tamil New Year
    (2026,  4, 15, "சித்திரை"),   # Apr 15
    (2026,  6, 20, "ஆனி"),        # Jun 20
    (2026, 12, 25, "மார்கழி"),    # Dec 25
]
for y, m, d, expected in td_tests:
    r = tamil_date_from_gregorian(y, m, d)
    check(f"{y}-{m:02d}-{d:02d}", r["tamil_month"], expected)

# ── Horoscope Generation ─────────────────────────────────────────────
print("\n=== Horoscope Test (1995-06-15 10:30 Salem) ===")
try:
    h = generate_horoscope(1995, 6, 15, 10, 30, 11.6643, 78.1460, 5.5)
    print(f"  Rasi      : {h['rasi']['ta']} ({h['rasi']['en']})")
    print(f"  Lagna     : {h['lagna']['ta']}")
    print(f"  Nakshatra : {h['nakshatra']['ta']} pada {h['nakshatra']['pada']}")
    print(f"  Cur Dasa  : {h['dasa']['current']['ta']} → {h['dasa']['current_bhukti']['ta']}")
    print(f"  Moon deg  : {h['meta']['moon_deg']:.4f}")
    print(f"  Planets   : {len(h['planets'])} planets")
    print(f"  Rasi grid : {sum(1 for row in h['rasi_grid'] for c in row if c['type']=='rasi')} cells")
    assert len(h['planets']) == 9, "Should have 9 planets"
    assert 'nav_lagna_ta' in h, "Missing nav_lagna_ta"
    print("  [OK] Horoscope generation PASSED")
    PASS += 1
except Exception as e:
    print(f"  [FAIL] Horoscope: {e}")
    FAIL += 1

# ── Panchangam ───────────────────────────────────────────────────────
print("\n=== Panchangam Test (today) ===")
try:
    from datetime import date
    today = date.today()
    pj = calc_panchangam(today.year, today.month, today.day, 11.6643, 78.1460, 5.5)
    required = ['tithi','vara_ta','nakshatra','yoga','karana','rahu_kalam','sunrise','sunset','tamil_date']
    for key in required:
        if key in pj:
            print(f"  {key}: {pj[key]}")
        else:
            print(f"  [MISS] {key} not in panchangam!")
            FAIL += 1
    PASS += 1
except Exception as e:
    print(f"  [FAIL] Panchangam: {e}")
    FAIL += 1

# ── Dasa with Days ───────────────────────────────────────────────────
print("\n=== Dasa-Days Test ===")
try:
    dd = calc_dasa_with_days("1995-06-15", 3, 55.2)
    assert 'all' in dd and 'bhukti_detailed' in dd
    assert len(dd['all']) == 9, "Should have 9 dasas"
    cur = next((x for x in dd['all'] if x['is_current']), None)
    print(f"  Current dasa: {dd['current_ta']} | {dd['current_start']} - {dd['current_end']}")
    print(f"  Bhukti count: {len(dd['bhukti_detailed'])}")
    print("  [OK] Dasa-days PASSED")
    PASS += 1
except Exception as e:
    print(f"  [FAIL] Dasa: {e}")
    FAIL += 1

# ── Summary ──────────────────────────────────────────────────────────
print(f"\n{'='*40}")
print(f"  PASSED: {PASS}   FAILED: {FAIL}")
print(f"{'='*40}")
if FAIL == 0:
    print("  ALL TESTS PASSED - Backend is healthy!")
else:
    print("  SOME TESTS FAILED - check output above.")
