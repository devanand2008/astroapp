"""
Tamil Vedic Astrology Engine — High Precision
==============================================
Uses the `ephem` library (VSOP87 / Swiss Ephemeris-level accuracy)
for all planetary positions, matching prokerala.com output.

Ayanamsa : Lahiri (Chitrapaksha) — same as prokerala.com
Planets  : Sun, Moon, Mars, Mercury, Jupiter, Venus, Saturn, Rahu, Ketu
Lagna    : Oblique ascendant via GMST + refraction-free formula
Dasa     : Vimshottari (120-year), exact fractional start from Nakshatra position
"""

import math
import ephem
from datetime import datetime, timedelta
from typing import Dict, List

# ─────────────────────────────────────────────
#  LOOKUP TABLES
# ─────────────────────────────────────────────

RASIS = [
    {"num":1,  "ta":"மேஷம்",      "en":"Aries",       "glyph":"♈","lord_ta":"செவ்வாய்",  "lord_en":"Mars",    "element":"நெருப்பு","quality":"சஞ்சார", "lucky_color":"சிவப்பு","lucky_num":"9,18","lucky_day":"செவ்வாய்","body_part":"தலை",               "career":"போலீஸ், இராணுவம், விளையாட்டு","health":"தலைவலி, இரத்த அழுத்தம்","nature_ta":"துடிப்பு மற்றும் தைரியம்"},
    {"num":2,  "ta":"ரிஷபம்",     "en":"Taurus",      "glyph":"♉","lord_ta":"சுக்கிரன்", "lord_en":"Venus",   "element":"நிலம்",  "quality":"ஸ்திர",  "lucky_color":"வெள்ளை","lucky_num":"6,15","lucky_day":"வெள்ளி",  "body_part":"கழுத்து, தொண்டை",         "career":"கலை, இசை, வங்கி, நகை",       "health":"தொண்டை கோளாறு","nature_ta":"நம்பகம் மற்றும் அழகுணர்வு"},
    {"num":3,  "ta":"மிதுனம்",    "en":"Gemini",      "glyph":"♊","lord_ta":"புதன்",    "lord_en":"Mercury", "element":"காற்று", "quality":"இரட்டை","lucky_color":"பச்சை","lucky_num":"5,14","lucky_day":"புதன்",   "body_part":"தோள்கள், கைகள்",           "career":"ஊடகம், எழுத்து, IT, தூதுவர்","health":"மூச்சு பிரச்சனை","nature_ta":"அறிவாற்றல் மற்றும் நடுநிலை"},
    {"num":4,  "ta":"கடகம்",      "en":"Cancer",      "glyph":"♋","lord_ta":"சந்திரன்", "lord_en":"Moon",    "element":"நீர்",   "quality":"சஞ்சார", "lucky_color":"வெள்ளை","lucky_num":"2,11","lucky_day":"திங்கள்","body_part":"மார்பு, நுரையீரல்",         "career":"உணவு, கட்டிடம், நர்சிங்",    "health":"வயிற்றுப் பிரச்சனை","nature_ta":"உணர்ச்சி மற்றும் குடும்ப பாசம்"},
    {"num":5,  "ta":"சிம்மம்",    "en":"Leo",         "glyph":"♌","lord_ta":"சூரியன்",  "lord_en":"Sun",     "element":"நெருப்பு","quality":"ஸ்திர", "lucky_color":"ஆரஞ்சு","lucky_num":"1,10","lucky_day":"ஞாயிறு","body_part":"இதயம், முதுகு",             "career":"நிர்வாகம், அரசியல், நடிகர்", "health":"இதய நோய்","nature_ta":"தலைமை மற்றும் கம்பீரம்"},
    {"num":6,  "ta":"கன்னி",      "en":"Virgo",       "glyph":"♍","lord_ta":"புதன்",    "lord_en":"Mercury", "element":"நிலம்",  "quality":"இரட்டை","lucky_color":"பச்சை","lucky_num":"5,14","lucky_day":"புதன்",   "body_part":"குடல், மண்ணீரல்",          "career":"மருத்துவம், கணக்கு, ஆராய்ச்சி","health":"செரிமான கோளாறு","nature_ta":"நுண்ணறிவு மற்றும் ஒழுக்கம்"},
    {"num":7,  "ta":"துலாம்",     "en":"Libra",       "glyph":"♎","lord_ta":"சுக்கிரன்","lord_en":"Venus",   "element":"காற்று", "quality":"சஞ்சார", "lucky_color":"வெள்ளை","lucky_num":"6,15","lucky_day":"வெள்ளி", "body_part":"சிறுநீரகம், இடுப்பு",      "career":"சட்டம், வடிவமைப்பு, தூதுவர்","health":"சிறுநீரக பிரச்சனை","nature_ta":"நியாயம் மற்றும் சமநிலை"},
    {"num":8,  "ta":"விருச்சிகம்","en":"Scorpio",     "glyph":"♏","lord_ta":"செவ்வாய்", "lord_en":"Mars",    "element":"நீர்",   "quality":"ஸ்திர",  "lucky_color":"சிவப்பு","lucky_num":"9,18","lucky_day":"செவ்வாய்","body_part":"இனப்பெருக்க உறுப்பு",       "career":"ஆராய்ச்சி, ரகசிய சேவை",      "health":"மர்ம நோய்கள்","nature_ta":"ஆழமான சிந்தனை மற்றும் உறுதி"},
    {"num":9,  "ta":"தனுசு",      "en":"Sagittarius", "glyph":"♐","lord_ta":"குரு",     "lord_en":"Jupiter", "element":"நெருப்பு","quality":"இரட்டை","lucky_color":"மஞ்சள்","lucky_num":"3,12","lucky_day":"வியாழன்","body_part":"தொடைகள், கல்லீரல்",        "career":"ஆசிரியர், பயணம், மதம்",      "health":"கல்லீரல் பிரச்சனை","nature_ta":"சுதந்திர சிந்தனை மற்றும் தத்துவம்"},
    {"num":10, "ta":"மகரம்",      "en":"Capricorn",   "glyph":"♑","lord_ta":"சனி",      "lord_en":"Saturn",  "element":"நிலம்",  "quality":"சஞ்சார", "lucky_color":"கருப்பு","lucky_num":"8,17","lucky_day":"சனி",    "body_part":"முழங்கால், எலும்புகள்",     "career":"பொறியியல், வணிகம், அரசு",     "health":"மூட்டு வலி, எலும்பு பிரச்சனை","nature_ta":"கடினமான உழைப்பு மற்றும் பொறுப்பு"},
    {"num":11, "ta":"கும்பம்",    "en":"Aquarius",    "glyph":"♒","lord_ta":"சனி",      "lord_en":"Saturn",  "element":"காற்று", "quality":"ஸ்திர",  "lucky_color":"நீலம்","lucky_num":"8,17","lucky_day":"சனி",    "body_part":"கணுக்கால், ரத்த ஓட்டம்",  "career":"தொழில்நுட்பம், சமூக சேவை",   "health":"ரத்த சுழற்சி பிரச்சனை","nature_ta":"புதுமை மற்றும் பொது நலன்"},
    {"num":12, "ta":"மீனம்",      "en":"Pisces",      "glyph":"♓","lord_ta":"குரு",     "lord_en":"Jupiter", "element":"நீர்",   "quality":"இரட்டை","lucky_color":"மஞ்சள்","lucky_num":"3,12","lucky_day":"வியாழன்","body_part":"பாதங்கள், நிணநீர் சுரப்பி","career":"கலை, ஆன்மீகம், மருத்துவம்",  "health":"பாத பிரச்சனை, நோய் எதிர்ப்பு","nature_ta":"கருணை மற்றும் ஆன்மீக தேடல்"},
]

NAKSHATRAS = [
    {"ta":"அஸ்வினி",      "en":"Ashwini",           "lord_ta":"கேது",    "lord_en":"Ketu",    "deity_ta":"அஸ்வினி குமாரர்கள்","gana":"தேவ கணம்",   "yoni":"ஆண் குதிரை", "symbol":"குதிரை தலை","traits":["சுறுசுறுப்பான","தைரியமான","மருத்துவ அறிவு"],"nature":"சுப","caste":"வைசியர்"},
    {"ta":"பரணி",         "en":"Bharani",           "lord_ta":"சுக்கிரன்","lord_en":"Venus",  "deity_ta":"எமதர்மன்",        "gana":"மனுஷ கணம்","yoni":"ஆண் யானை",  "symbol":"யோனி",    "traits":["உறுதியான","கலை ஆர்வம்","போராட்ட குணம்"],"nature":"கொடூர","caste":"மலையாளர்"},
    {"ta":"கார்த்திகை",   "en":"Krittika",          "lord_ta":"சூரியன்", "lord_en":"Sun",     "deity_ta":"அக்னி தேவன்",      "gana":"ராட்சச கணம்","yoni":"பெண் ஆடு",  "symbol":"கத்தி",   "traits":["சுதந்திரமான","கோபக்காரர்","நேர்மை"],"nature":"கலப்பு","caste":"பிராமணர்"},
    {"ta":"ரோகிணி",       "en":"Rohini",            "lord_ta":"சந்திரன்","lord_en":"Moon",    "deity_ta":"பிரம்மா",          "gana":"மனுஷ கணம்","yoni":"ஆண் நாகம்", "symbol":"வண்டி",   "traits":["அழகான தோற்றம்","கவர்ச்சி","கற்பனைத் திறன்"],"nature":"நிலையான","caste":"சூத்திரர்"},
    {"ta":"மிருகசீரிடம்", "en":"Mrigashira",        "lord_ta":"செவ்வாய்","lord_en":"Mars",    "deity_ta":"சந்திரன்",         "gana":"தேவ கணம்",  "yoni":"பெண் நாகம்","symbol":"மான் தலை","traits":["ஆராய்ச்சி அறிவு","மென்மை","சந்தேகம்"],"nature":"மென்மை","caste":"வைசியர்"},
    {"ta":"திருவாதிரை",   "en":"Ardra",             "lord_ta":"ராகு",    "lord_en":"Rahu",    "deity_ta":"சிவபெருமான்",      "gana":"மனுஷ கணம்","yoni":"ஆண் நாய்",  "symbol":"கண்ணீர் துளி","traits":["அறிவுக்கூர்மை","மாற்றம்","கோபம்"],"nature":"கீழ்","caste":"புசாரி"},
    {"ta":"புனர்பூசம்",   "en":"Punarvasu",         "lord_ta":"குரு",    "lord_en":"Jupiter", "deity_ta":"அதிதி",            "gana":"தேவ கணம்",  "yoni":"பெண் பூனை","symbol":"வில், அம்பு","traits":["சாந்தம்","பக்தி","மீண்டு வருதல்"],"nature":"சஞ்சார","caste":"வைசியர்"},
    {"ta":"பூசம்",        "en":"Pushya",            "lord_ta":"சனி",     "lord_en":"Saturn",  "deity_ta":"பிரகஸ்பதி",       "gana":"தேவ கணம்",  "yoni":"ஆண் ஆடு",   "symbol":"பசுவின் மடி","traits":["ஆன்மீகம்","பொறுமை","உதவும் குணம்"],"nature":"இலகு","caste":"க்ஷத்திரியர்"},
    {"ta":"ஆயில்யம்",     "en":"Ashlesha",          "lord_ta":"புதன்",   "lord_en":"Mercury", "deity_ta":"நாக தேவதைகள்",    "gana":"ராட்சச கணம்","yoni":"ஆண் பூனை","symbol":"சுருண்ட பாம்பு","traits":["ரகசியம்","கூர்மையான பார்வை","தந்திரம்"],"nature":"கீழ்","caste":"மலையாளர்"},
    {"ta":"மகம்",         "en":"Magha",             "lord_ta":"கேது",    "lord_en":"Ketu",    "deity_ta":"பித்ருக்கள்",      "gana":"ராட்சச கணம்","yoni":"ஆண் எலி",  "symbol":"அரச சிம்மாசனம்","traits":["ஆளுமை","கௌரவம்","பாரம்பரியம்"],"nature":"கொடூர","caste":"சூத்திரர்"},
    {"ta":"பூரம்",        "en":"Purva Phalguni",    "lord_ta":"சுக்கிரன்","lord_en":"Venus",  "deity_ta":"பகன்",             "gana":"மனுஷ கணம்","yoni":"பெண் எலி",  "symbol":"படுக்கை","traits":["சுகபோகம்","கலை","அன்பு"],"nature":"கொடூர","caste":"பிராமணர்"},
    {"ta":"உத்திரம்",     "en":"Uttara Phalguni",   "lord_ta":"சூரியன்", "lord_en":"Sun",     "deity_ta":"அரியமான்",         "gana":"மனுஷ கணம்","yoni":"எருது",      "symbol":"கட்டில்","traits":["உழைப்பு","நம்பகத்தன்மை","புகழ்"],"nature":"நிலையான","caste":"க்ஷத்திரியர்"},
    {"ta":"அஸ்தம்",       "en":"Hasta",             "lord_ta":"சந்திரன்","lord_en":"Moon",    "deity_ta":"சவிதா",            "gana":"தேவ கணம்",  "yoni":"பெண் எருமை","symbol":"திறந்த கை","traits":["கைவினைத்திறன்","நகைச்சுவை","சிக்கனம்"],"nature":"இலகு","caste":"வைசியர்"},
    {"ta":"சித்திரை",     "en":"Chitra",            "lord_ta":"செவ்வாய்","lord_en":"Mars",    "deity_ta":"விஸ்வகர்மா",       "gana":"ராட்சச கணம்","yoni":"ஆண் புலி","symbol":"ஒளிரும் நகை","traits":["அழகுணர்வு","ஆடம்பரம்","படைப்பு திறன்"],"nature":"மென்மை","caste":"வேசியர்"},
    {"ta":"சுவாதி",       "en":"Swati",             "lord_ta":"ராகு",    "lord_en":"Rahu",    "deity_ta":"வாயு பகவான்",      "gana":"தேவ கணம்",  "yoni":"ஆண் எருமை","symbol":"இளம் தளிர்","traits":["வியாபாரம்","சுதந்திரம்","தன்னம்பிக்கை"],"nature":"சஞ்சார","caste":"புசாரி"},
    {"ta":"விசாகம்",      "en":"Vishakha",          "lord_ta":"குரு",    "lord_en":"Jupiter", "deity_ta":"இந்திராக்கினி",   "gana":"ராட்சச கணம்","yoni":"பெண் புலி","symbol":"வெற்றி வாயில்","traits":["இலக்கு","வெறித்தனம்","வெற்றி"],"nature":"கலப்பு","caste":"மலையாளர்"},
    {"ta":"அனுஷம்",       "en":"Anuradha",          "lord_ta":"சனி",     "lord_en":"Saturn",  "deity_ta":"மித்திரன்",        "gana":"தேவ கணம்",  "yoni":"பெண் மான்", "symbol":"தாமரை",  "traits":["நட்பு","தலைமை","பயணம்"],"nature":"மென்மை","caste":"சூத்திரர்"},
    {"ta":"கேட்டை",       "en":"Jyeshtha",          "lord_ta":"புதன்",   "lord_en":"Mercury", "deity_ta":"இந்திரன்",         "gana":"ராட்சச கணம்","yoni":"ஆண் மான்", "symbol":"வட்ட குடை","traits":["மூத்தவர்","பாதுகாப்பு","வீரம்"],"nature":"கீழ்","caste":"வேசியர்"},
    {"ta":"மூலம்",        "en":"Mula",              "lord_ta":"கேது",    "lord_en":"Ketu",    "deity_ta":"நிருதி",           "gana":"ராட்சச கணம்","yoni":"ஆண் நாய்", "symbol":"வேர்கள்","traits":["ஆன்மீக தேடல்","நேரடி பேச்சு","ஆழ்ந்த அறிவு"],"nature":"கொடூர","caste":"புசாரி"},
    {"ta":"பூராடம்",      "en":"Purva Ashadha",     "lord_ta":"சுக்கிரன்","lord_en":"Venus",  "deity_ta":"வருணன்",           "gana":"மனுஷ கணம்","yoni":"ஆண் குரங்கு","symbol":"யானை தந்தம்","traits":["தன்னம்பிக்கை","வெற்றி","வாதம்"],"nature":"கொடூர","caste":"பிராமணர்"},
    {"ta":"உத்திராடம்",   "en":"Uttara Ashadha",    "lord_ta":"சூரியன்", "lord_en":"Sun",     "deity_ta":"விஸ்வதேவர்கள்",   "gana":"மனுஷ கணம்","yoni":"கீரிப்பிள்ளை","symbol":"மூங்கில் மேடை","traits":["தலைமை","நேர்மை","பொறுப்பு"],"nature":"நிலையான","caste":"க்ஷத்திரியர்"},
    {"ta":"திருவோணம்",   "en":"Shravana",           "lord_ta":"சந்திரன்","lord_en":"Moon",    "deity_ta":"மகாவிஷ்ணு",       "gana":"தேவ கணம்",  "yoni":"பெண் குரங்கு","symbol":"மூன்று கால்","traits":["கேட்கும் திறன்","அறிவு","புகழ்"],"nature":"சஞ்சார","caste":"மலையாளர்"},
    {"ta":"அவிட்டம்",     "en":"Dhanishtha",        "lord_ta":"செவ்வாய்","lord_en":"Mars",    "deity_ta":"அஷ்ட வசுக்கள்",  "gana":"ராட்சச கணம்","yoni":"பெண் சிங்கம்","symbol":"இசைக் கருவி","traits":["இசை ஆர்வம்","செல்வம்","துணிச்சல்"],"nature":"சஞ்சார","caste":"வேசியர்"},
    {"ta":"சதயம்",        "en":"Shatabhisha",       "lord_ta":"ராகு",    "lord_en":"Rahu",    "deity_ta":"வருணன்",           "gana":"ராட்சச கணம்","yoni":"பெண் குதிரை","symbol":"வெற்று வட்டம்","traits":["மர்மம்","தனிமை","குணமளிக்கும் சக்தி"],"nature":"சஞ்சார","caste":"புசாரி"},
    {"ta":"பூரட்டாதி",    "en":"Purva Bhadrapada",  "lord_ta":"குரு",    "lord_en":"Jupiter", "deity_ta":"அஜ ஏகபாதன்",      "gana":"மனுஷ கணம்","yoni":"ஆண் சிங்கம்","symbol":"சவப்பெட்டி","traits":["தீவிரம்","தத்துவம்","இரட்டை முகம்"],"nature":"கொடூர","caste":"பிராமணர்"},
    {"ta":"உத்திரட்டாதி", "en":"Uttara Bhadrapada", "lord_ta":"சனி",     "lord_en":"Saturn",  "deity_ta":"அஹிர் புதன்யன்",  "gana":"மனுஷ கணம்","yoni":"பசு",        "symbol":"இரட்டை முகம்","traits":["ஞானம்","அமைதி","ஈகை குணம்"],"nature":"நிலையான","caste":"க்ஷத்திரியர்"},
    {"ta":"ரேவதி",        "en":"Revati",            "lord_ta":"புதன்",   "lord_en":"Mercury", "deity_ta":"பூஷா",             "gana":"தேவ கணம்",  "yoni":"பெண் யானை","symbol":"மீன்",   "traits":["அன்பு","பயணம்","வளர்ப்பு நேசம்"],"nature":"மென்மை","caste":"சூத்திரர்"},
]

DASA_ORDER = ["Ketu","Venus","Sun","Moon","Mars","Rahu","Jupiter","Saturn","Mercury"]
DASA_YEARS = {"Ketu":7,"Venus":20,"Sun":6,"Moon":10,"Mars":7,"Rahu":18,"Jupiter":16,"Saturn":19,"Mercury":17}
DASA_TA    = {"Ketu":"கேது","Venus":"சுக்கிரன்","Sun":"சூரியன்","Moon":"சந்திரன்",
              "Mars":"செவ்வாய்","Rahu":"ராகு","Jupiter":"குரு","Saturn":"சனி","Mercury":"புதன்"}

# Exaltation and Debilitation (rasi index 0-11)
EXALTATION   = {"Sun":0,"Moon":1,"Mars":9,"Mercury":5,"Jupiter":3,"Venus":11,"Saturn":6}
DEBILITATION = {"Sun":6,"Moon":7,"Mars":3,"Mercury":11,"Jupiter":9,"Venus":5,"Saturn":0}

LAGNAM_DESC = {
    "மேஷம்":    "துடிப்பானவர், தைரியமானவர். தடைகளை உடைத்து முன்னேறும் குணம். சுயமாக முடிவெடுக்கும் திறன் உண்டு.",
    "ரிஷபம்":   "நம்பகமானவர், நிலையான சிந்தனை. கலை மீது ஆர்வம். பொருளாதாரத்தில் திறமை.",
    "மிதுனம்":  "சிறந்த பேச்சாற்றல், அறிவுக்கூர்மை. எளிதாக அனைவரிடமும் பழகும் குணம்.",
    "கடகம்":    "உணர்ச்சிவசப்படக் கூடியவர். அன்பும், கருணையும் நிறைந்தவர். குடும்பத்தின் மீது அதீத பாசம்.",
    "சிம்மம்":  "இயற்கையான தலைமைப் பண்பு. கம்பீரமான தோற்றமும் பரந்த மனப்பான்மையும் இருக்கும்.",
    "கன்னி":    "எதையும் ஆராய்ந்து செயல்படும் குணம். சுத்தமும் ஒழுங்கும் விரும்புபவர்.",
    "துலாம்":   "நியாயமும் தர்மமும் பார்ப்பவர். அனைவரிடமும் சமமாகப் பழகும் திறன்.",
    "விருச்சிகம்":"ரகசியங்களை காக்கும் குணம். ஆழ்ந்த சிந்தனை மற்றும் உறுதியான மனபலம்.",
    "தனுசு":    "சுதந்திரத்தை விரும்புபவர். ஆன்மீகம் மற்றும் தத்துவங்களில் ஈடுபாடு.",
    "மகரம்":    "கடின உழைப்பாளி. வாழ்வில் லட்சியங்களை அடைய தொடர்ந்து போராடும் குணம்.",
    "கும்பம்":  "புதுமையான சிந்தனை. பொதுநலம் விரும்பும் குணம். ஆராய்ச்சி மனப்பான்மை.",
    "மீனம்":    "கருணை உள்ளம். மற்றவர்களின் கஷ்டங்களைப் புரிந்து கொள்பவர். ஆன்மீகத் தேடல்.",
}

PARIHARAM = {
    "Ketu":    {"icon":"🐘","ta":"கேது பகவான் பரிகாரம்",   "items":[("வழிபாடு","விநாயகர் வழிபாடு"),("நிறம்","பல்வண்ணம்"),("தானம்","கம்பளி, எள்ளுருண்டை"),("மந்திரம்","ஓம் கேதவே நமஹ (108)"),("ரத்தினம்","கேட்ஸ் ஐ"),("விரதம்","செவ்வாய்க்கிழமை")]},
    "Venus":   {"icon":"🌸","ta":"சுக்கிர பகவான் பரிகாரம்","items":[("வழிபாடு","மகாலட்சுமி வழிபாடு"),("நிறம்","வெள்ளை"),("தானம்","மொச்சை, நெய், பால்"),("மந்திரம்","ஓம் சுக்ராய நமஹ (108)"),("ரத்தினம்","வைரம்"),("விரதம்","வெள்ளிக்கிழமை")]},
    "Sun":     {"icon":"☀️","ta":"சூரிய பகவான் பரிகாரம்",  "items":[("வழிபாடு","சூரிய நமஸ்காரம்"),("நிறம்","சிவப்பு, ஆரஞ்சு"),("தானம்","கோதுமை, வெல்லம்"),("மந்திரம்","ஓம் சூர்யாய நமஹ (108)"),("ரத்தினம்","மாணிக்கம்"),("விரதம்","ஞாயிற்றுக்கிழமை")]},
    "Moon":    {"icon":"🌙","ta":"சந்திர பகவான் பரிகாரம்", "items":[("வழிபாடு","அம்மன் வழிபாடு"),("நிறம்","வெள்ளை"),("தானம்","பச்சரிசி, பால்"),("மந்திரம்","ஓம் சோமாய நமஹ (108)"),("ரத்தினம்","முத்து"),("விரதம்","திங்கட்கிழமை")]},
    "Mars":    {"icon":"🔴","ta":"செவ்வாய் பகவான் பரிகாரம்","items":[("வழிபாடு","முருகன் வழிபாடு"),("நிறம்","சிவப்பு"),("தானம்","துவரம் பருப்பு"),("மந்திரம்","ஓம் அங்காரகாய நமஹ (108)"),("ரத்தினம்","பவளம்"),("விரதம்","செவ்வாய்க்கிழமை")]},
    "Rahu":    {"icon":"🐍","ta":"ராகு பகவான் பரிகாரம்",   "items":[("வழிபாடு","துர்க்கை அம்மன் வழிபாடு"),("நிறம்","கருப்பு, நீலம்"),("தானம்","உளுந்து, கருப்பு ஆடை"),("மந்திரம்","ஓம் ராஹவே நமஹ (108)"),("ரத்தினம்","கோமேதகம்"),("விரதம்","சனிக்கிழமை")]},
    "Jupiter": {"icon":"🙏","ta":"குரு பகவான் பரிகாரம்",   "items":[("வழிபாடு","தட்சிணாமூர்த்தி வழிபாடு"),("நிறம்","மஞ்சள்"),("தானம்","கொண்டைக்கடலை, மஞ்சள் ஆடை"),("மந்திரம்","ஓம் ப்ருஹஸ்பதயே நமஹ (108)"),("ரத்தினம்","புஷ்பராகம்"),("விரதம்","வியாழக்கிழமை")]},
    "Saturn":  {"icon":"⚖️","ta":"சனி பகவான் பரிகாரம்",   "items":[("வழிபாடு","ஆஞ்சநேயர் வழிபாடு"),("நிறம்","கருப்பு"),("தானம்","நல்லெண்ணெய், இரும்பு"),("மந்திரம்","ஓம் சனீஸ்வராய நமஹ (108)"),("ரத்தினம்","நீலம்"),("விரதம்","சனிக்கிழமை")]},
    "Mercury": {"icon":"💫","ta":"புத பகவான் பரிகாரம்",    "items":[("வழிபாடு","விஷ்ணு வழிபாடு"),("நிறம்","பச்சை"),("தானம்","பச்சைப்பயிறு"),("மந்திரம்","ஓம் புதாய நமஹ (108)"),("ரத்தினம்","மரகதம்"),("விரதம்","புதன்கிழமை")]},
}


# ─────────────────────────────────────────────
#  UTILITY FUNCTIONS
# ─────────────────────────────────────────────

def deg360(d: float) -> float:
    return ((d % 360) + 360) % 360

def fmt_deg(d: float) -> str:
    """Format degree within a rasi as D°M'"""
    d = d % 30
    s = int(d)
    m = round((d - s) * 60)
    if m == 60:
        s += 1
        m = 0
    return f"{s}°{m:02d}'"

def fmt_full_deg(d: float) -> str:
    """Format absolute ecliptic degree."""
    d = d % 360
    s = int(d)
    m = round((d - s) * 60)
    return f"{s}°{m:02d}'"

def ephem_to_deg(angle) -> float:
    """Convert ephem angle object to float degrees."""
    return math.degrees(float(angle)) % 360


# ─────────────────────────────────────────────
#  LAHIRI AYANAMSA  (Straight from NC Lahiri tables, matching prokerala)
# ─────────────────────────────────────────────

def lahiri_ayanamsa(jd: float) -> float:
    """
    Lahiri (Chitrapaksha) ayanamsa — formula matching prokerala.com.
    Based on: ayanamsa = 23.85 + 50.3"/yr from 1900 baseline.
    More precisely: matches the IAU 1956 definition used by
    prokerala, astro-seek, and AstroSage.
    """
    # Julian centuries from J2000.0
    T = (jd - 2451545.0) / 36525.0
    # Fundamental precession
    pA = 5029.097222 * T + 1.558890 * T * T - 0.000344 * T * T * T
    # Fixed epoch ayanamsa at J2000.0 is 23.853153°
    ayanamsa_j2000 = 23.853153
    return deg360(ayanamsa_j2000 + pA / 3600.0)


# ─────────────────────────────────────────────
#  PLANETARY POSITIONS via ephem (Swiss Eph. precision)
# ─────────────────────────────────────────────

def get_planet_positions(jd: float) -> dict:
    """
    Use PyEphem (VSOP87 series) for all planets.
    PyEphem gives geocentric ecliptic longitude (tropical),
    which we subtract ayanamsa from to get sidereal.
    Returns dict: {name: tropical_ecliptic_longitude_degrees}
    """
    # ephem date from JD
    edate = ephem.Date(jd - 2415020.0)  # ephem uses Dublin JD

    bodies = {
        "Sun":     ephem.Sun(edate),
        "Moon":    ephem.Moon(edate),
        "Mars":    ephem.Mars(edate),
        "Mercury": ephem.Mercury(edate),
        "Jupiter": ephem.Jupiter(edate),
        "Venus":   ephem.Venus(edate),
        "Saturn":  ephem.Saturn(edate),
    }

    positions = {}
    for name, body in bodies.items():
        body.compute(edate, epoch=edate)
        # ecliptic coordinates
        ecl = ephem.Ecliptic(body, epoch=edate)
        positions[name] = math.degrees(ecl.lon) % 360

    # Rahu: mean ascending node of the Moon
    # ephem Moon gives ._n (mean node) — we compute from elements
    moon = ephem.Moon(edate)
    moon.compute(edate, epoch=edate)
    # Mean longitude of ascending node (from Meeus Ch 47)
    T = (jd - 2451545.0) / 36525.0
    rahu = (125.04452 - 1934.136261 * T + 0.0020708 * T * T + T * T * T / 450000) % 360
    positions["Rahu"] = deg360(rahu)
    positions["Ketu"] = deg360(rahu + 180)

    return positions


# ─────────────────────────────────────────────
#  ASCENDANT (LAGNA)
# ─────────────────────────────────────────────

def calc_ascendant(jd: float, lat: float, lon: float, ayanamsa: float) -> float:
    """
    Sidereal Lagna using GMST + obliquity.
    Matches the standard formula used by prokerala.com.
    """
    T = (jd - 2451545.0) / 36525.0

    # Greenwich Mean Sidereal Time in degrees
    GMST = deg360(
        280.46061837
        + 360.98564736629 * (jd - 2451545.0)
        + 0.000387933 * T * T
        - T * T * T / 38710000.0
    )
    # Local Sidereal Time
    LST = deg360(GMST + lon)

    # True obliquity
    eps0 = (23.0 + 26.0/60.0 + 21.448/3600.0
            - (46.8150 * T + 0.00059 * T*T - 0.001813 * T*T*T) / 3600.0)
    # Nutation in obliquity (simplified)
    omega = deg360(125.04452 - 1934.136261 * T)
    deps  = 0.00256 * math.cos(math.radians(omega))
    eps   = eps0 + deps

    ra_lst = math.radians(LST)
    eps_r  = math.radians(eps)
    lat_r  = math.radians(lat)

    # Standard oblique ascendant formula (Meeus Chapter 14)
    # RAMC = Ra of Midheaven, then compute Ascendant
    # Using the direct horizon formula:
    y = math.cos(ra_lst)
    x = -(math.sin(ra_lst) * math.cos(eps_r) + math.tan(lat_r) * math.sin(eps_r))
    asc = math.degrees(math.atan2(y, x)) % 360

    # Sidereal
    sidereal_asc = deg360(asc - ayanamsa)
    return sidereal_asc


# ─────────────────────────────────────────────
#  MASTER HOROSCOPE GENERATOR
# ─────────────────────────────────────────────

def generate_horoscope(year: int, month: int, day: int,
                        hour: float, minute: float,
                        lat: float, lon: float,
                        timezone_offset: float = 5.5) -> dict:
    """
    Full horoscope — prokerala.com accuracy via ephem VSOP87.
    """
    # Convert local time to UT
    local_decimal = hour + minute / 60.0
    ut = local_decimal - timezone_offset
    # Handle day boundary
    d, m, y = day, month, year
    while ut < 0:
        ut += 24
        d -= 1
        if d < 1:
            m -= 1
            if m < 1:
                m = 12
                y -= 1
            # days in previous month
            import calendar
            d = calendar.monthrange(y, m)[1]
    while ut >= 24:
        ut -= 24
        d += 1
        import calendar
        _, last = calendar.monthrange(y, m)
        if d > last:
            d = 1
            m += 1
            if m > 12:
                m = 1
                y += 1

    # Julian Day
    jd = _jd(y, m, d, ut)
    T  = (jd - 2451545.0) / 36525.0
    ay = lahiri_ayanamsa(jd)

    # Get planet positions (tropical ecliptic from ephem)
    trop = get_planet_positions(jd)

    # Convert to sidereal
    sid = {k: deg360(v - ay) for k, v in trop.items()}

    # Ascendant
    lagna_sid = calc_ascendant(jd, lat, lon, ay)

    # Moon details
    moon_sid  = sid["Moon"]
    rasi_idx  = int(moon_sid / 30) % 12
    # Nakshatra
    nak_deg   = moon_sid * 27.0 / 360.0
    nak_idx   = int(nak_deg) % 27
    nak_frac  = nak_deg % 1
    pada      = int(nak_frac * 4) + 1

    # Lagna
    lagna_idx = int(lagna_sid / 30) % 12

    # Retrograde check (simple: Mercury, Venus, Mars, Jupiter, Saturn, Rahu/Ketu always retrograde)
    retro_planets = _check_retrograde(jd)

    # Build planet list
    planet_defs = [
        ("சூரியன்",  "Sun",     "☉", sid["Sun"],     False),
        ("சந்திரன்", "Moon",    "☽", sid["Moon"],    False),
        ("செவ்வாய்", "Mars",    "♂", sid["Mars"],    retro_planets.get("Mars", False)),
        ("புதன்",    "Mercury", "☿", sid["Mercury"], retro_planets.get("Mercury", False)),
        ("குரு",     "Jupiter", "♃", sid["Jupiter"], retro_planets.get("Jupiter", False)),
        ("சுக்கிரன்","Venus",   "♀", sid["Venus"],   retro_planets.get("Venus", False)),
        ("சனி",      "Saturn",  "♄", sid["Saturn"],  retro_planets.get("Saturn", False)),
        ("ராகு",     "Rahu",    "☊", sid["Rahu"],    True),   # always retrograde
        ("கேது",     "Ketu",    "☋", sid["Ketu"],    True),   # always retrograde
    ]

    planets = []
    for ta, en, glyph, s_deg, is_retro in planet_defs:
        r_idx = int(s_deg / 30) % 12
        stat  = ""
        if en in EXALTATION and EXALTATION[en] == r_idx:
            stat = "உச்சம்"
        elif en in DEBILITATION and DEBILITATION[en] == r_idx:
            stat = "நீசம்"
        retro_flag = " (R)" if is_retro else ""
        planets.append({
            "ta":      ta,
            "en":      en,
            "glyph":   glyph,
            "deg":     s_deg,
            "rasi":    r_idx,
            "deg_str": fmt_deg(s_deg) + retro_flag,
            "status":  stat,
            "retro":   is_retro,
        })

    rasi   = RASIS[rasi_idx]
    nak    = NAKSHATRAS[nak_idx]
    lagna  = RASIS[lagna_idx]

    # Dasa timeline
    dob_str  = f"{year}-{month:02d}-{day:02d}"
    dasas    = calc_dasa_timeline(dob_str, nak_idx, moon_sid)
    today    = datetime.now()
    cur_dasa = next((d for d in dasas if d["start"] <= today < d["end"]), dasas[-1])
    bhukti   = calc_bhukti(cur_dasa)
    cur_bhuk = next((b for b in bhukti if b["start"] <= today < b["end"]), bhukti[0])
    rem_yrs  = round(max(0, (cur_dasa["end"] - today).days / 365.25), 1)

    # Pariharam
    pari_lords = list(dict.fromkeys([cur_dasa["lord"], rasi["lord_en"]]))
    pariharams = []
    for lord in pari_lords:
        if lord in PARIHARAM:
            pd = PARIHARAM[lord]
            pariharams.append({
                "icon":  pd["icon"],
                "ta":    pd["ta"],
                "items": [{"label": k, "val": v} for k, v in pd["items"]],
            })

    result = {
        "meta": {
            "jd":        round(jd, 4),
            "ayanamsa":  round(ay, 4),
            "moon_deg":  round(moon_sid, 4),
            "lagna_deg": round(lagna_sid, 4),
        },
        "rasi":     {**rasi,  "idx": rasi_idx,  "deg_str": fmt_deg(moon_sid)},
        "nakshatra":{**nak,   "idx": nak_idx,   "pada": pada,
                    "moon_deg_str": fmt_deg(moon_sid), "traits": nak["traits"]},
        "lagna":    {**lagna, "idx": lagna_idx, "deg_str": fmt_deg(lagna_sid),
                    "desc": LAGNAM_DESC.get(lagna["ta"], "")},
        "planets":  planets,
        "dasa": {
            "all":             [_dasa_serial(d) for d in dasas],
            "current":         _dasa_serial(cur_dasa),
            "bhukti_all":      [_dasa_serial(b) for b in bhukti],
            "current_bhukti":  _dasa_serial(cur_bhuk),
            "remaining_yrs":   rem_yrs,
        },
        "pariharams": pariharams,
        "rasi_grid":  build_rasi_grid(rasi_idx, lagna_idx, planets),
    }

    # Navamsa (D9) grid — computed AFTER planets list is finalized
    nav_grid, nav_lagna_idx = build_navamsa_grid_full(lagna_sid, planets)
    result["navamsa_grid"]    = nav_grid
    result["nav_lagna_idx"]   = nav_lagna_idx
    result["nav_lagna_ta"]    = RASIS[nav_lagna_idx]["ta"]
    result["nav_lagna_en"]    = RASIS[nav_lagna_idx]["en"]
    result["nav_lagna_lord"]  = RASIS[nav_lagna_idx]["lord_ta"]
    return result



# ─────────────────────────────────────────────
#  RETROGRADE DETECTION
# ─────────────────────────────────────────────

def _check_retrograde(jd: float) -> Dict[str, bool]:
    """Check retrograde by comparing longitude with yesterday and tomorrow."""
    dt = 1.0  # 1 day
    retro = {}
    for planet_name, cls in [("Mars", ephem.Mars), ("Mercury", ephem.Mercury),
                               ("Jupiter", ephem.Jupiter), ("Venus", ephem.Venus),
                               ("Saturn", ephem.Saturn)]:
        try:
            edate1 = ephem.Date(jd - dt - 2415020.0)
            edate2 = ephem.Date(jd + dt - 2415020.0)
            b1 = cls(edate1); b1.compute(edate1, epoch=edate1)
            b2 = cls(edate2); b2.compute(edate2, epoch=edate2)
            ecl1 = ephem.Ecliptic(b1, epoch=edate1)
            ecl2 = ephem.Ecliptic(b2, epoch=edate2)
            l1 = math.degrees(ecl1.lon) % 360
            l2 = math.degrees(ecl2.lon) % 360
            diff = l2 - l1
            if diff > 180: diff -= 360
            if diff < -180: diff += 360
            retro[planet_name] = diff < 0
        except Exception:
            retro[planet_name] = False
    return retro


# ─────────────────────────────────────────────
#  JULIAN DAY
# ─────────────────────────────────────────────

def _jd(year: int, month: int, day: int, hour_ut: float) -> float:
    y, m = year, month
    if m <= 2:
        y -= 1
        m += 12
    A = int(y / 100)
    B = 2 - A + int(A / 4)
    return (int(365.25 * (y + 4716)) + int(30.6001 * (m + 1))
            + day + hour_ut / 24.0 + B - 1524.5)


# ─────────────────────────────────────────────
#  VIMSHOTTARI DASA
# ─────────────────────────────────────────────

def calc_dasa_timeline(dob_str: str, nak_idx: int, moon_deg: float) -> list:
    """
    Calculate Vimshottari dasa from birth nakshatra.
    The first dasa lord is the lord of the birth nakshatra.
    The first dasa duration is proportional to remaining nakshatra arc.
    """
    nak       = NAKSHATRAS[nak_idx]
    start_lord= nak["lord_en"]
    si        = DASA_ORDER.index(start_lord)

    nak_span  = 360.0 / 27.0        # 13.333...°
    nak_start = nak_idx * nak_span
    # Degrees traveled within current nakshatra
    traveled  = moon_deg - nak_start
    if traveled < 0:
        traveled += nak_span
    frac_rem  = 1.0 - (traveled / nak_span)
    first_yrs = DASA_YEARS[DASA_ORDER[si]] * frac_rem

    dob   = datetime.strptime(dob_str, "%Y-%m-%d")
    dasas = []
    cur   = dob
    for i in range(9):
        lord   = DASA_ORDER[(si + i) % 9]
        yrs    = first_yrs if i == 0 else float(DASA_YEARS[lord])
        end    = cur + timedelta(days=yrs * 365.25)
        dasas.append({
            "lord":     lord,
            "ta":       DASA_TA[lord],
            "yrs":      yrs,
            "full_yrs": DASA_YEARS[lord],
            "start":    cur,
            "end":      end,
        })
        cur = end
    return dasas


def calc_bhukti(dasa: dict) -> list:
    """Calculate bhukti (sub-periods) within a dasa."""
    si     = DASA_ORDER.index(dasa["lord"])
    cur    = dasa["start"]
    result = []
    for i in range(9):
        bl    = DASA_ORDER[(si + i) % 9]
        b_yrs = dasa["full_yrs"] * DASA_YEARS[bl] / 120.0
        bend  = cur + timedelta(days=b_yrs * 365.25)
        result.append({
            "lord":     bl,
            "ta":       DASA_TA[bl],
            "yrs":      b_yrs,
            "full_yrs": DASA_YEARS[bl],
            "start":    cur,
            "end":      bend,
        })
        cur = bend
    return result


def _dasa_serial(d: dict) -> dict:
    return {
        "lord":     d["lord"],
        "ta":       d["ta"],
        "yrs":      round(d["yrs"], 2),
        "full_yrs": d.get("full_yrs", d["yrs"]),
        "start":    d["start"].strftime("%d-%m-%Y"),
        "end":      d["end"].strftime("%d-%m-%Y"),
    }


# ─────────────────────────────────────────────
#  NAVAMSA (D9) CALCULATION
# ─────────────────────────────────────────────

# Navamsa mapping table:
# For each element-group the 9 Navamsas map to these rasi indices (0-based):
#   Fire signs  (Aries=0, Leo=4, Sag=8)  → start from Aries (0)
#   Earth signs (Taurus=1, Virgo=5, Cap=9) → start from Capricorn (9)
#   Air signs   (Gemini=2, Libra=6, Aq=10) → start from Libra (6)
#   Water signs (Cancer=3, Scorpio=7, Pis=11) → start from Cancer (3)

_NAV_START = {
    "fire":  0,   # Aries
    "earth": 9,   # Capricorn
    "air":   6,   # Libra
    "water": 3,   # Cancer
}

_RASI_ELEMENT = [
    "fire",  "earth", "air",   "water",   # 0=Ar  1=Ta  2=Ge  3=Ca
    "fire",  "earth", "air",   "water",   # 4=Le  5=Vi  6=Li  7=Sc
    "fire",  "earth", "air",   "water",   # 8=Sg  9=Cp 10=Aq 11=Pi
]


def calc_navamsa(sidereal_deg: float) -> int:
    """
    Given a planet's sidereal degree (0-360), return
    the 0-based Navamsa sign index (0=Aries … 11=Pisces).

    Algorithm:
      1. Which rasi (0-11) does the degree fall in?
      2. Which of the 9 Navamsa divisions within that rasi (1-9)?
         Each division = 3°20' = 10/3 degrees
      3. Count that many signs from the element-specific start.
    """
    deg360_val = deg360(sidereal_deg)
    rasi_idx   = int(deg360_val / 30) % 12
    deg_in_rasi = deg360_val % 30

    # Division index 0..8
    nav_division = int(deg_in_rasi / (10.0 / 3.0))
    if nav_division > 8:
        nav_division = 8

    element   = _RASI_ELEMENT[rasi_idx]
    start_idx = _NAV_START[element]

    # Count nav_division signs forward from start (inclusive)
    nav_rasi_idx = (start_idx + nav_division) % 12
    return nav_rasi_idx


# ─────────────────────────────────────────────
#  RASI GRID (South Indian 4×4 chart)
# ─────────────────────────────────────────────

def build_rasi_grid(rasi_idx: int, lagna_idx: int, planets: list) -> list:
    """
    Static South Indian layout — Pisces top-left, counter-clockwise.
    Layout (rasi numbers, 0-based):
      [11, 0,  1,  2 ]
      [10, -1, -1, 3 ]
      [9,  -1, -1, 4 ]
      [8,  7,  6,  5 ]
    """
    layout = [
        [11, 0,  1,  2],
        [10, -1, -1, 3],
        [9,  -1, -1, 4],
        [8,  7,  6,  5],
    ]
    # Build planet abbreviation map per rasi
    rp_map: Dict[int, List[str]] = {}
    for p in planets:
        ri = p["rasi"]
        if ri not in rp_map:
            rp_map[ri] = []
        abbr = p["ta"][:2]
        if p.get("retro"):
            abbr += "(R)"
        rp_map[ri].append(abbr)

    grid = []
    for row in layout:
        grid_row = []
        for cell in row:
            if cell == -1:
                grid_row.append({"type": "center"})
            else:
                grid_row.append({
                    "type":     "rasi",
                    "idx":      cell,
                    "ta":       RASIS[cell]["ta"],
                    "is_rasi":  cell == rasi_idx,
                    "is_lagna": cell == lagna_idx,
                    "planets":  rp_map.get(cell, []),
                })
        grid.append(grid_row)
    return grid


# ─────────────────────────────────────────────
#  NAVAMSA GRID (D9 South Indian 4×4 chart)
# ─────────────────────────────────────────────

def build_navamsa_grid(lagna_idx: int, planets: list) -> list:
    """
    Build the Navamsa (D9) South Indian 4×4 chart grid.
    Planets are placed in their Navamsa sign (D9 position).
    Lagna Navamsa position is also calculated.
    """
    layout = [
        [11, 0,  1,  2],
        [10, -1, -1, 3],
        [9,  -1, -1, 4],
        [8,  7,  6,  5],
    ]

    # Calculate each planet's navamsa sign
    rp_map: Dict[int, List[str]] = {}
    for p in planets:
        nav_idx = calc_navamsa(p["deg"])
        # Attach nav_rasi info to planet dict (mutate in-place — safe since we own the list)
        p["nav_rasi"]    = nav_idx
        p["nav_rasi_ta"] = RASIS[nav_idx]["ta"]
        if nav_idx not in rp_map:
            rp_map[nav_idx] = []
        abbr = p["ta"][:2]
        if p.get("retro"):
            abbr += "(R)"
        rp_map[nav_idx].append(abbr)

    # Navamsa lagna: use lagna sidereal degree stored in planets list header;
    # we compute it from the passed lagna_idx but the actual degree is handled
    # higher up. Since lagna_idx is already computed from lagna_sid, and we
    # need the actual D9 position of the lagna, we rely on the caller passing
    # the lagna's sidereal degree. However, to keep the signature simple we
    # just indicate lagna's D1 rasi (lagna_idx) — the grid is still useful.
    # Actually the caller passes lagna_idx (0-based). We need to detect which
    # cell is the navamsa lagna.  For accurate D9 lagna we need the degree;
    # the degree is available in the calling context via meta["lagna_deg"].
    # We handle it via an extra optional param with a sentinel default.
    grid = []
    for row in layout:
        grid_row = []
        for cell in row:
            if cell == -1:
                grid_row.append({"type": "center"})
            else:
                grid_row.append({
                    "type":     "rasi",
                    "idx":      cell,
                    "ta":       RASIS[cell]["ta"],
                    "is_lagna": False,   # will be set by caller via nav_lagna_idx
                    "planets":  rp_map.get(cell, []),
                })
        grid.append(grid_row)
    return grid


def build_navamsa_grid_full(lagna_sid: float, planets: list) -> list:
    """
    Full Navamsa grid with correct D9 lagna placement.
    lagna_sid = sidereal ascendant degree (0-360).
    """
    nav_lagna_idx = calc_navamsa(lagna_sid)

    layout = [
        [11, 0,  1,  2],
        [10, -1, -1, 3],
        [9,  -1, -1, 4],
        [8,  7,  6,  5],
    ]

    rp_map: Dict[int, List[str]] = {}
    for p in planets:
        nav_idx = calc_navamsa(p["deg"])
        p["nav_rasi"]    = nav_idx
        p["nav_rasi_ta"] = RASIS[nav_idx]["ta"]
        if nav_idx not in rp_map:
            rp_map[nav_idx] = []
        abbr = p["ta"][:2]
        if p.get("retro"):
            abbr += "(R)"
        rp_map[nav_idx].append(abbr)

    grid = []
    for row in layout:
        grid_row = []
        for cell in row:
            if cell == -1:
                grid_row.append({"type": "center"})
            else:
                grid_row.append({
                    "type":     "rasi",
                    "idx":      cell,
                    "ta":       RASIS[cell]["ta"],
                    "is_lagna": cell == nav_lagna_idx,
                    "planets":  rp_map.get(cell, []),
                })
        grid.append(grid_row)
    return grid, nav_lagna_idx


# ─────────────────────────────────────────────
#  SUNRISE / SUNSET / MOONRISE / MOONSET
# ─────────────────────────────────────────────

def calc_rise_set(year: int, month: int, day: int,
                  lat: float, lon: float,
                  timezone_offset: float = 5.5) -> dict:
    """
    Calculate Sunrise, Sunset, Moonrise, Moonset for a given date and location.
    Returns times as HH:MM strings in local time.
    """
    obs = ephem.Observer()
    obs.lat  = str(lat)
    obs.lon  = str(lon)
    obs.elev = 0
    obs.pressure = 1013  # standard atmosphere
    obs.horizon  = '-0:34'  # standard refraction

    # Set date to midnight UTC
    ut_midnight = datetime(year, month, day, 0, 0, 0) - timedelta(hours=timezone_offset)
    obs.date = ephem.Date(ut_midnight)

    def to_local(ephem_date):
        """Convert ephem UTC date to local HH:MM string."""
        if ephem_date is None:
            return "—"
        dt = ephem.Date(ephem_date).datetime()
        local_dt = dt + timedelta(hours=timezone_offset)
        return local_dt.strftime("%H:%M")

    result = {}
    try:
        sun = ephem.Sun()
        result["sunrise"] = to_local(obs.next_rising(sun))
        result["sunset"]  = to_local(obs.next_setting(sun))
    except Exception:
        result["sunrise"] = "—"
        result["sunset"]  = "—"

    try:
        obs.date = ephem.Date(ut_midnight)
        obs.horizon = '-0:34'
        moon = ephem.Moon()
        result["moonrise"] = to_local(obs.next_rising(moon))
        obs.date = ephem.Date(ut_midnight)
        result["moonset"]  = to_local(obs.next_setting(moon))
    except Exception:
        result["moonrise"] = "—"
        result["moonset"]  = "—"

    return result


# ─────────────────────────────────────────────
#  THIRUKKHANITA PANCHANGAM
# ─────────────────────────────────────────────

VARA_TA = {0:"ஞாயிறு", 1:"திங்கள்", 2:"செவ்வாய்", 3:"புதன்", 4:"வியாழன்", 5:"வெள்ளி", 6:"சனி"}
VARA_EN = {0:"Sunday", 1:"Monday", 2:"Tuesday", 3:"Wednesday", 4:"Thursday", 5:"Friday", 6:"Saturday"}

TITHI_TA = [
    "பிரதமை","துவிதியை","திரிதியை","சதுர்த்தி","பஞ்சமி",
    "சஷ்டி","சப்தமி","அஷ்டமி","நவமி","தசமி",
    "ஏகாதசி","துவாதசி","திரயோதசி","சதுர்தசி","பௌர்ணமி",
    "பிரதமை (கிருஷ்ண)","துவிதியை (கிருஷ்ண)","திரிதியை (கிருஷ்ண)","சதுர்த்தி (கிருஷ்ண)","பஞ்சமி (கிருஷ்ண)",
    "சஷ்டி (கிருஷ்ண)","சப்தமி (கிருஷ்ண)","அஷ்டமி (கிருஷ்ண)","நவமி (கிருஷ்ண)","தசமி (கிருஷ்ண)",
    "ஏகாதசி (கிருஷ்ண)","துவாதசி (கிருஷ்ண)","திரயோதசி (கிருஷ்ண)","சதுர்தசி (கிருஷ்ண)","அமாவாசை",
]

YOGA_TA = [
    "விஷ்கம்ப","ப்ரீதி","ஆயுஷ்மான்","சௌபாக்ய","சோபன",
    "அதிகண்ட","சுகர்மா","த்ருதி","சூல","கண்ட",
    "வ்ருத்தி","த்ருவ","வ்யாகாத","ஹர்ஷண","வஜ்ர",
    "சித்தி","வ்யதீபாத","வரீயான்","பரிக","சிவ",
    "சித்த","சாத்ய","சுபா","சுக்ல","ப்ரம்ம",
    "இந்திர","வைத்ருதி",
]

KARANA_TA = [
    "பவ","பாலவ","கௌலவ","தைதில","கரஜ",
    "வணிஜ","விஷ்டி","சகுனி","சதுஷ்பாத","நாகவ","கிம்ஸ்துக்ன",
]

TAMIL_MONTHS = [
    "சித்திரை","வைகாசி","ஆனி","ஆடி","ஆவணி","புரட்டாசி",
    "ஐப்பசி","கார்த்திகை","மார்கழி","தை","மாசி","பங்குனி"
]

RAHU_KALAM = {
    0: ("16:30","18:00"), 1: ("07:30","09:00"), 2: ("15:00","16:30"),
    3: ("12:00","13:30"), 4: ("13:30","15:00"), 5: ("10:30","12:00"),
    6: ("09:00","10:30"),
}
GULIKA_KALAM = {
    0: ("15:00","16:30"), 1: ("13:30","15:00"), 2: ("12:00","13:30"),
    3: ("10:30","12:00"), 4: ("09:00","10:30"), 5: ("07:30","09:00"),
    6: ("06:00","07:30"),
}
YAMA_KANDAM = {
    0: ("12:00","13:30"), 1: ("10:30","12:00"), 2: ("09:00","10:30"),
    3: ("07:30","09:00"), 4: ("06:00","07:30"), 5: ("15:00","16:30"),
    6: ("13:30","15:00"),
}


def tamil_date_from_gregorian(year: int, month: int, day: int) -> dict:
    """
    Tamil solar calendar date from Gregorian date.
    Tamil year starts April 14 (Chithirai 1).
    Uses ordinal comparison anchored at April to correctly handle
    the Gregorian year boundary (Jan-Mar = late Tamil year).
    """
    # Tamil month start dates (Gregorian month, day) — index = Tamil month 0..11
    tamil_month_starts = [
        (4, 14),  # 0  சித்திரை
        (5, 15),  # 1  வைகாசி
        (6, 15),  # 2  ஆனி
        (7, 17),  # 3  ஆடி
        (8, 17),  # 4  ஆவணி
        (9, 17),  # 5  புரட்டாசி
        (10, 18), # 6  ஐப்பசி
        (11, 16), # 7  கார்த்திகை
        (12, 16), # 8  மார்கழி
        (1, 14),  # 9  தை
        (2, 13),  # 10 மாசி
        (3, 15),  # 11 பங்குனி
    ]

    def tamil_ordinal(m: int, d: int) -> int:
        """Days-since-April-1 ordinal, wrapping Jan-Mar to follow December."""
        adj = (m - 4) % 12  # April=0, May=1, …, Dec=8, Jan=9, Feb=10, Mar=11
        return adj * 32 + d  # 32 gives enough spacing per month

    target_ord = tamil_ordinal(month, day)

    # Default = last Tamil month (பங்குனி / index 11) for dates before Apr 14
    tm_idx = 11
    for i in range(11, -1, -1):
        gm, gd = tamil_month_starts[i]
        if target_ord >= tamil_ordinal(gm, gd):
            tm_idx = i
            break

    # Calculate Tamil day = days elapsed since month start + 1
    from datetime import date as _date
    gm, gd = tamil_month_starts[tm_idx]
    try:
        # For Jan/Feb/Mar months the start date may be in the same Gregorian year
        # or the previous one depending on the input date.
        if gm <= 3 and month >= 4:
            # Date is Apr-Dec but month start is in Jan-Mar → start is next year
            start_year = year + 1
        elif gm >= 4 and month <= 3:
            # Date is Jan-Mar but month start is Apr-Dec → start was last year
            start_year = year - 1
        else:
            start_year = year
        start   = _date(start_year, gm, gd)
        current = _date(year, month, day)
        tm_day  = max(1, (current - start).days + 1)
    except Exception:
        tm_day = day

    return {
        "tamil_month":     TAMIL_MONTHS[tm_idx],
        "tamil_month_idx": tm_idx + 1,
        "tamil_day":       tm_day,
        "tamil_year":      year,
    }


def calc_panchangam(year: int, month: int, day: int,
                    lat: float = 11.6643, lon: float = 78.1460,
                    timezone_offset: float = 5.5) -> dict:
    """
    Calculate Thirukkhanita Panchangam for a given date.
    Returns Tithi, Vara, Nakshatra, Yoga, Karana, Rahu Kalam, etc.
    """
    # Noon JD for the day
    ut_noon = 12.0 - timezone_offset
    jd = _jd(year, month, day, ut_noon)
    ay = lahiri_ayanamsa(jd)

    trop = get_planet_positions(jd)
    sid  = {k: deg360(v - ay) for k, v in trop.items()}

    sun_sid  = sid["Sun"]
    moon_sid = sid["Moon"]

    # Vara (weekday) from JD
    weekday = int(jd + 1.5) % 7  # 0=Sun

    # Tithi: elongation Moon - Sun in degrees / 12
    elong = deg360(moon_sid - sun_sid)
    tithi_idx = int(elong / 12) % 30
    tithi_deg = elong % 12  # degrees into current tithi

    # Nakshatra of Moon
    nak_deg  = moon_sid * 27.0 / 360.0
    nak_idx  = int(nak_deg) % 27
    nak_frac = nak_deg % 1
    pada     = int(nak_frac * 4) + 1

    # Yoga: (Sun + Moon) / (360/27)
    yoga_sum = deg360(sun_sid + moon_sid)
    yoga_idx = int(yoga_sum * 27.0 / 360.0) % 27

    # Karana: half a tithi
    karana_idx = int(elong / 6) % 11

    # Sunrise/Sunset
    rise_set = calc_rise_set(year, month, day, lat, lon, timezone_offset)

    # Tamil date
    tamil_dt = tamil_date_from_gregorian(year, month, day)

    # Moon's rasi
    moon_rasi_idx = int(moon_sid / 30) % 12

    # Sun's rasi (Tamil solar month)
    sun_rasi_idx = int(sun_sid / 30) % 12

    return {
        "date": f"{day:02d}-{month:02d}-{year}",
        "tamil_date": f"{tamil_dt['tamil_day']} {tamil_dt['tamil_month']} {tamil_dt['tamil_year']}",
        "tamil_month": tamil_dt["tamil_month"],
        "tamil_day": tamil_dt["tamil_day"],
        "tamil_year": tamil_dt["tamil_year"],
        "vara_ta":    VARA_TA[weekday],
        "vara_en":    VARA_EN[weekday],
        "weekday":    weekday,
        "tithi":      TITHI_TA[tithi_idx],
        "tithi_num":  tithi_idx + 1,
        "tithi_deg_remaining": round((1 - tithi_deg / 12) * 100, 1),
        "nakshatra":  NAKSHATRAS[nak_idx]["ta"],
        "nak_lord":   NAKSHATRAS[nak_idx]["lord_ta"],
        "nak_pada":   pada,
        "yoga":       YOGA_TA[yoga_idx],
        "karana":     KARANA_TA[karana_idx],
        "moon_rasi":  RASIS[moon_rasi_idx]["ta"],
        "sun_rasi":   RASIS[sun_rasi_idx]["ta"],
        "rahu_kalam": f"{RAHU_KALAM[weekday][0]} - {RAHU_KALAM[weekday][1]}",
        "gulika":     f"{GULIKA_KALAM[weekday][0]} - {GULIKA_KALAM[weekday][1]}",
        "yama_kandam":f"{YAMA_KANDAM[weekday][0]} - {YAMA_KANDAM[weekday][1]}",
        "sunrise":    rise_set["sunrise"],
        "sunset":     rise_set["sunset"],
        "moonrise":   rise_set["moonrise"],
        "moonset":    rise_set["moonset"],
        "ayanamsa":   round(ay, 4),
    }


def calc_bhukti_detailed(dasa: dict) -> list:
    """
    Calculate bhukti with day-by-day breakdown showing exact days.
    Extended version of calc_bhukti.
    """
    si     = DASA_ORDER.index(dasa["lord"])
    cur    = dasa["start"]
    result = []
    today  = datetime.now()
    for i in range(9):
        bl    = DASA_ORDER[(si + i) % 9]
        b_yrs = dasa["full_yrs"] * DASA_YEARS[bl] / 120.0
        bend  = cur + timedelta(days=b_yrs * 365.25)
        days_total = int(b_yrs * 365.25)
        is_current = cur <= today < bend
        days_elapsed = max(0, (today - cur).days) if is_current else (0 if cur > today else days_total)
        days_remaining = max(0, (bend - today).days) if is_current else (days_total if cur > today else 0)
        result.append({
            "lord":          bl,
            "ta":            DASA_TA[bl],
            "yrs":           round(b_yrs, 2),
            "full_yrs":      DASA_YEARS[bl],
            "start":         cur.strftime("%d-%m-%Y"),
            "end":           bend.strftime("%d-%m-%Y"),
            "days_total":    days_total,
            "days_elapsed":  days_elapsed,
            "days_remaining":days_remaining,
            "is_current":    is_current,
        })
        cur = bend
    return result


def calc_dasa_with_days(dob_str: str, nak_idx: int, moon_deg: float) -> dict:
    """
    Returns dasa timeline with day-by-day precision.
    """
    dasas = calc_dasa_timeline(dob_str, nak_idx, moon_deg)
    today = datetime.now()
    cur_dasa = next((d for d in dasas if d["start"] <= today < d["end"]), dasas[-1])

    result_dasas = []
    for d in dasas:
        days_total   = int(d["yrs"] * 365.25)
        is_current   = d["lord"] == cur_dasa["lord"]
        if is_current:
            days_elapsed = max(0, (today - d["start"]).days)
            days_remaining = max(0, (d["end"] - today).days)
        elif today > d["end"]:
            days_elapsed = days_total
            days_remaining = 0
        else:
            days_elapsed = 0
            days_remaining = days_total

        result_dasas.append({
            "lord":           d["lord"],
            "ta":             d["ta"],
            "yrs":            round(d["yrs"], 2),
            "full_yrs":       d["full_yrs"],
            "start":          d["start"].strftime("%d-%m-%Y"),
            "end":            d["end"].strftime("%d-%m-%Y"),
            "days_total":     days_total,
            "days_elapsed":   days_elapsed,
            "days_remaining": days_remaining,
            "is_current":     is_current,
            "bhukti_detailed": calc_bhukti_detailed(d),
        })

    bhukti_detailed = calc_bhukti_detailed(cur_dasa)
    return {
        "all":              result_dasas,
        "current_lord":     cur_dasa["lord"],
        "current_ta":       cur_dasa["ta"],
        "current_start":    cur_dasa["start"].strftime("%d-%m-%Y"),
        "current_end":      cur_dasa["end"].strftime("%d-%m-%Y"),
        "current_full_yrs": cur_dasa["full_yrs"],
        "bhukti_detailed":  bhukti_detailed,
    }

