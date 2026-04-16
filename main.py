import urllib.request, urllib.parse, json, os, sys, time, re

# ==========================================
# THE IMMORTAL SYSTEM - FULL PRO EDITION (v44.0)
# (Gemini Agents + Natural TTS + Dynamic Photos)
# ==========================================

# 1. API KEY & ENVIRONMENT SETUP
raw_keys = os.environ.get("GEMINI_API_KEY", "")
API_KEYS = [k.strip() for k in raw_keys.split(",") if k.strip()]

# अगर Environment में Keys नहीं हैं, तो ये बैकअप Keys इस्तेमाल होंगी
if not API_KEYS:
    API_KEYS = [
        "AIzaSyBsr9sYpFc9evX4yDFBCM1WAkYhzz6F2fU", 
        "AIzaSyBzy0HTMgJMa_64QI4XcCjXO2pmTlMX8Pw", 
        "AIzaSyBxcY9nBb0m6WtjhtMdsYRNGd98q1kDpxo"
    ]

current_year = time.strftime("%Y")
today_date = time.strftime("%d %B %Y")
post_id = int(time.time())

# 2. DATABASE (posts.json)
posts_db = []
if os.path.exists("posts.json"):
    with open("posts.json", "r", encoding="utf-8") as f:
        try:
            raw_db = json.load(f)
            posts_db = [p for p in raw_db if "img" in p]
        except: pass

# 3. AUTO MODEL DETECTION
available_model = "models/gemini-1.5-flash"
try:
    req = urllib.request.Request(f"https://generativelanguage.googleapis.com/v1beta/models?key={API_KEYS[0]}")
    with urllib.request.urlopen(req, timeout=30) as response:
        res = json.loads(response.read().decode('utf-8'))
        for m in res.get('models', []):
            if 'generateContent' in m.get('supportedGenerationMethods', []) and 'flash' in m.get('name', '').lower():
                available_model = m['name']; break
except: pass

# 4. THE TRIPLE-ENGINE AI AGENT
def ask_ai(prompt, retries=15):
    for i in range(retries):
        current_key = API_KEYS[i % len(API_KEYS)]
        api_url = f"https://generativelanguage.googleapis.com/v1beta/{available_model}:generateContent?key={current_key}"
        try:
            data = json.dumps({"contents": [{"parts": [{"text": prompt}]}]}).encode('utf-8')
            req = urllib.request.Request(api_url, data=data, headers={'Content-Type': 'application/json'})
            with urllib.request.urlopen(req, timeout=90) as response:
                res = json.loads(response.read().decode('utf-8'))
                text = res['candidates'][0]['content']['parts'][0]['text'].strip()
                if len(text) > 10: return text
        except: time.sleep(5)
    return ""

# 5. GENERATING CONTENT (TOPIC, SEO, BODY)
topic_prompt = f"तुम एक ट्रेंड एनालिस्ट हो। {current_year} में मेक मनी ऑनलाइन या AI पर एक धांसू और वायरल हिंदी ब्लॉग टाइटल दो। पुराने टाइटल्स: {[p['title'] for p in posts_db[:5]]} से अलग हो। सिर्फ 'टाइटल' लिखना।"
current_topic = ask_ai(topic_prompt).replace('"', '').replace("'", "").replace("*", "")
if not current_topic: sys.exit(1)

seo_prompt = f"विषय: '{current_topic}'। सिर्फ इस फॉर्मेट में जवाब दो: MAIN_IMG_ENGLISH_KEYWORD | SEO_DESCRIPTION | SEO_KEYWORDS. (No Robot/Cyborg words)"
seo_raw = ask_ai(seo_prompt)

main_img_words = "modern business laptop workspace"
meta_desc, meta_keywords = f"Digital Kamai Hub - {current_year}", "AI, Money"
try:
    if "|" in seo_raw:
        parts = seo_raw.split("|")
        main_img_words = re.sub(r'[^a-zA-Z0-9\s]', '', parts[0]).strip()
        meta_desc, meta_keywords = parts[1].strip(), parts[2].strip()
except: pass

html_prompt = f"विषय: '{current_topic}'। 1000 शब्दों का शानदार हिंदी ब्लॉग लिखो। HTML (h2, p, strong, ul) यूज़ करो और [PHOTO] 3 बार लिखो।"
blog_content = ask_ai(html_prompt, retries=20).replace("```html", "").replace("```", "").strip()

# 6. DYNAMIC IMAGES
modifiers = ["creative_workspace", "financial_growth", "modern_minimalist"]
for mod in modifiers:
    if "[PHOTO]" in blog_content:
        dynamic_keyword = urllib.parse.quote(f"{main_img_words} {mod}")
        img_html = f"<img src='https://image.pollinations.ai/prompt/{dynamic_keyword}?width=800&height=400&nologo=true' class='article-img'>"
        blog_content = blog_content.replace("[PHOTO]", img_html, 1)

main_img_url = f"https://image.pollinations.ai/prompt/{urllib.parse.quote(main_img_words)}?width=1200&height=600&nologo=true"
post_filename = f"post_{post_id}.html"

# 7. PREMIUM CSS & NATURAL VOICE JS
premium_css = f"""
<style>
    :root {{ --main-red: #da251c; --dark: #111; }}
    * {{ box-sizing: border-box; margin: 0; padding: 0; font-family: 'Segoe UI', sans-serif; }}
    body {{ background: #f0f2f5; color: #111; line-height: 1.8; }}
    header {{ background: #fff; padding: 20px; text-align: center; border-bottom: 3px solid var(--main-red); position: sticky; top: 0; z-index: 1000; }}
    .logo {{ font-size: 28px; font-weight: 900; color: var(--main-red); text-decoration: none; text-transform: uppercase; }}
    .container {{ max-width: 850px; margin: 40px auto; background: white; padding: 40px; border-radius: 12px; box-shadow: 0 5px 20px rgba(0,0,0,0.05); }}
    h1 {{ font-size: 38px; line-height: 1.3; margin-bottom: 20px; }}
    .hero-img, .article-img {{ width: 100%; border-radius: 10px; margin-bottom: 30px; object-fit: cover; }}
    #article-body {{ font-size: 20px; color: #444; }}
    #article-body h2 {{ color: #000; border-left: 5px solid var(--main-red); padding-left: 15px; margin: 35px 0 15px; }}
    .tts-btn {{ position: fixed; bottom: 30px; right: 30px; background: #000; color: #fff; border: none; padding: 15px 30px; border-radius: 50px; font-weight: bold; cursor: pointer; z-index: 1000; box-shadow: 0 10px 20px rgba(0,0,0,0.2); }}
    .yt-btn {{ display: block; background: #ff0000; color: white; text-align: center; padding: 18px; border-radius: 8px; text-decoration: none; font-weight: bold; margin-top: 30px; }}
    .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(320px, 1fr)); gap: 25px; }}
    .card {{ background: white; padding: 15px; border-radius: 10px; box-shadow: 0 4px 15px rgba(0,0,0,0.05); }}
    .card img {{ width: 100%; border-radius: 8px; }}
</style>
"""

natural_voice_js = """
<script>
    let s = window.speechSynthesis, isR = false;
    function toggleTTS() {
        if (isR) { s.cancel(); isR = false; document.getElementById('ttsBtn').innerText = '🔊 लेख सुनें'; return; }
        let text = document.getElementById('article-body').innerText;
        let utter = new SpeechSynthesisUtterance(text);
        let v = s.getVoices();
        let bestV = v.find(v => v.name.includes('Google') && v.lang.includes('hi')) || v.find(v => v.lang.includes('hi'));
        if (bestV) utter.voice = bestV;
        utter.lang = 'hi-IN'; utter.rate = 0.9;
        utter.onstart = () => { isR = true; document.getElementById('ttsBtn').innerText = '⏹️ बंद करें'; };
        utter.onend = () => { isR = false; document.getElementById('ttsBtn').innerText = '🔊 लेख सुनें'; };
        s.speak(utter);
    }
</script>
"""

# 8. FINAL PAGE GENERATION
header = f"<header><a href='index.html' class='logo'>Digital Kamai Hub</a></header>"
footer = f"<footer style='background:#111;color:#888;padding:40px;text-align:center;margin-top:40px;'><p>&copy; {current_year} Digital Kamai Hub</p></footer>"

# Article Page
with open(post_filename, "w", encoding="utf-8") as f:
    f.write(f"<html><head><meta charset='UTF-8'><meta name='viewport' content='width=device-width, initial-scale=1.0'><title>{current_topic}</title>{premium_css}</head><body>{header}<div class='container'><h1>{current_topic}</h1><div style='color:#888; margin-bottom:20px;'>📅 प्रकाशित: {today_date}</div><img src='{main_img_url}' class='hero-img'><div id='article-body'>{blog_content}</div><a href='https://www.youtube.com/results?search_query={urllib.parse.quote(current_topic)}' target='_blank' class='yt-btn'>📺 यूट्यूब वीडियो देखें</a></div><button class='tts-btn' id='ttsBtn' onclick='toggleTTS()'>🔊 लेख सुनें</button>{natural_voice_js}{footer}</body></html>")

# Index Page
posts_db.insert(0, {"title": current_topic, "file": post_filename, "date": today_date, "img": main_img_url})
with open("posts.json", "w", encoding="utf-8") as f: json.dump(posts_db, f, ensure_ascii=False, indent=4)

cards = "".join([f"<div class='card'><img src='{p['img']}'><div style='padding:15px;'><h3><a href='{p['file']}' style='color:#000;text-decoration:none;'>{p['title']}</a></h3><p style='color:#888;'>🗓 {p['date']}</p><a href='{p['file']}' style='color:red;font-weight:bold;text-decoration:none;'>पढ़ें →</a></div></div>" for p in posts_db])
with open("index.html", "w", encoding="utf-8") as f:
    f.write(f"<html><head><meta charset='UTF-8'><meta name='viewport' content='width=device-width, initial-scale=1.0'><title>Digital Kamai Hub</title>{premium_css}</head><body>{header}<div style='max-width:1100px;margin:40px auto;padding:0 20px;'><h2>🔥 ताज़ा लेख</h2><div class='grid'>{cards}</div></div>{footer}</body></html>")

# Static Pages (About, Privacy, Disclaimer)
pages = [("about", "About Us"), ("privacy", "Privacy Policy"), ("disclaimer", "Disclaimer")]
for p_f, p_t in pages:
    with open(f"{p_f}.html", "w", encoding="utf-8") as f:
        f.write(f"<html><head><meta charset='UTF-8'>{premium_css}</head><body>{header}<div class='container'><h1>{p_t}</h1><p>Digital Kamai Hub में आपका स्वागत है।</p></div>{footer}</body></html>")

print(f"✅ Success: {current_topic} Published!")
        
