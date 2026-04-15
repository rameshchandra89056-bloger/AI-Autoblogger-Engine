import urllib.request
import urllib.parse
import json
import os
import sys
import time

# ==========================================
# THE IMMORTAL SYSTEM - ULTIMATE EDITION (v36.0)
# 1000 Level Pro: Multi-Key, Soft TTS, Premium UI, Auto-Pages
# ==========================================

# 1. SOLAR PANEL (API KEYS LOAD)
raw_keys = os.environ.get("GEMINI_API_KEY", "")
API_KEYS = [k.strip() for k in raw_keys.split(",") if k.strip()]
if not API_KEYS: 
    print("❌ API Key गायब है!")
    sys.exit(1)

current_year = time.strftime("%Y")
today_date = time.strftime("%d %B %Y")
post_id = int(time.time())

# 2. AUTO-CLEANUP (पुराना कबाड़ साफ करना)
posts_db = []
past_titles = []
if os.path.exists("posts.json"):
    with open("posts.json", "r", encoding="utf-8") as f:
        try:
            raw_db = json.load(f)
            posts_db = [p for p in raw_db if "img" in p] # सिर्फ फोटो वाली पोस्ट बचेंगी
            past_titles = [post["title"] for post in posts_db][:10] 
        except: pass

# 3. BLOODHOUND (मॉडल ढूँढना)
available_model = "models/gemini-1.5-flash"
try:
    req = urllib.request.Request(f"https://generativelanguage.googleapis.com/v1beta/models?key={API_KEYS[0]}")
    with urllib.request.urlopen(req, timeout=30) as response:
        res = json.loads(response.read().decode('utf-8'))
        for m in res.get('models', []):
            if 'generateContent' in m.get('supportedGenerationMethods', []) and 'flash' in m.get('name', '').lower():
                available_model = m['name']; break
except: pass

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

# ---------------------------------------------------------
# THE 3 AGENTS IN ACTION
# ---------------------------------------------------------
print("🧠 एजेंट 1: टॉपिक ढूँढ रहा है...")
topic_prompt = f"तुम एक ट्रेंड एनालिस्ट हो। {current_year} में मेक मनी ऑनलाइन या AI पर एक धांसू और वायरल हिंदी ब्लॉग टाइटल दो। पुराने टाइटल्स: {past_titles} से अलग हो। सिर्फ 'टाइटल' लिखना।"
current_topic = ask_ai(topic_prompt).replace('"', '').replace("'", "").replace("*", "")
if not current_topic: sys.exit(1)

print("📊 एजेंट 2: SEO बना रहा है...")
seo_prompt = f"विषय: '{current_topic}'। सिर्फ इस फॉर्मेट में जवाब दो: MAIN_IMG_ENGLISH_KEYWORD | SEO_DESCRIPTION | SEO_KEYWORDS"
seo_raw = ask_ai(seo_prompt)
main_img_words = "futuristic AI technology success"
meta_desc = f"Digital Kamai Hub - {current_year} Best Article"
meta_keywords = "AI, Make Money Online, Freelancing"
try:
    if "|" in seo_raw:
        parts = seo_raw.split("|")
        main_img_words, meta_desc, meta_keywords = parts[0].strip(), parts[1].strip(), parts[2].strip()
except: pass

print("💻 एजेंट 3: 1000 शब्दों का आर्टिकल लिख रहा है (कृपया प्रतीक्षा करें)...")
html_prompt = f"""तुम एक प्रो ब्लॉगर हो। विषय: '{current_topic}'। 
कम से कम 1000 शब्दों का एक बहुत ही शानदार हिंदी ब्लॉग पोस्ट लिखो।
नियम:
1. पोस्ट के बीच-बीच में 2 बार यह कोड लगाओ: <img src="https://image.pollinations.ai/prompt/ENG_KEYWORD?width=800&height=400&nologo=true" class="article-img"> (ENG_KEYWORD की जगह पैराग्राफ से जुड़ा इंग्लिश शब्द डालना)।
2. पोस्ट के अंत में यह बटन लगाओ: <a href="https://www.youtube.com/results?search_query={urllib.parse.quote(current_topic)}" target="_blank" class="yt-btn">📺 यूट्यूब पर इस विषय का वीडियो देखें</a>
3. सिर्फ HTML कोड (h2, p, strong, ul) देना। कोई फालतू बात या ```html मत लिखना।"""

blog_content = ask_ai(html_prompt, retries=20).replace("```html", "").replace("```", "").strip()
if not blog_content or len(blog_content) < 300: 
    print("❌ AI ने कंटेंट नहीं दिया या बहुत छोटा दिया।")
    sys.exit(1)

# ---------------------------------------------------------
# DATABASE & CSS (THE AAJ TAK THEME)
# ---------------------------------------------------------
main_img_url = f"[https://image.pollinations.ai/prompt/](https://image.pollinations.ai/prompt/){urllib.parse.quote(main_img_words)}?width=1200&height=600&nologo=true"
post_filename = f"post_{post_id}.html"

posts_db.insert(0, {"title": current_topic, "file": post_filename, "date": today_date, "img": main_img_url})
with open("posts.json", "w", encoding="utf-8") as f: json.dump(posts_db, f, ensure_ascii=False, indent=4)

premium_css = """
<style>
    :root { --main-red: #da251c; --dark-bg: #111; --text-gray: #444; }
    * { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Segoe UI', Tahoma, sans-serif; }
    body { background: #f0f2f5; color: #111; line-height: 1.7; }
    .top-bar { background: var(--main-red); color: white; padding: 5px 0; text-align: center; font-size: 13px; font-weight: bold; letter-spacing: 1px; }
    header { background: white; border-bottom: 2px solid #eee; box-shadow: 0 4px 10px rgba(0,0,0,0.05); position: sticky; top: 0; z-index: 1000; }
    .nav-container { max-width: 1100px; margin: 0 auto; padding: 15px 20px; display: flex; justify-content: space-between; align-items: center; }
    .logo { font-size: 28px; font-weight: 900; color: var(--main-red); text-decoration: none; text-transform: uppercase; }
    .nav-links a { margin-left: 20px; text-decoration: none; color: #111; font-weight: bold; font-size: 16px; }
    
    .container { max-width: 850px; margin: 40px auto; background: white; padding: 40px; border-radius: 8px; box-shadow: 0 5px 20px rgba(0,0,0,0.05); }
    h1 { font-size: 38px; line-height: 1.3; margin-bottom: 15px; color: #000; }
    .meta { font-size: 14px; color: #888; border-bottom: 1px solid #eee; padding-bottom: 15px; margin-bottom: 25px; }
    .hero-img { width: 100%; border-radius: 8px; margin-bottom: 30px; box-shadow: 0 5px 15px rgba(0,0,0,0.1); }
    .article-img { width: 100%; border-radius: 8px; margin: 25px 0; border: 1px solid #eee; }
    #article-body { font-size: 20px; color: var(--text-gray); }
    #article-body h2 { color: #000; margin: 35px 0 15px 0; border-left: 4px solid var(--main-red); padding-left: 15px; }
    
    .yt-btn { display: block; background: #ff0000; color: white; text-align: center; padding: 18px; border-radius: 8px; text-decoration: none; font-weight: bold; font-size: 18px; margin: 40px 0; transition: 0.3s; box-shadow: 0 5px 15px rgba(255,0,0,0.3); }
    .yt-btn:hover { background: #cc0000; transform: scale(1.02); }
    
    .tts-btn { position: fixed; bottom: 30px; right: 30px; background: var(--main-red); color: white; border: none; padding: 15px 25px; border-radius: 50px; font-weight: bold; font-size: 16px; cursor: pointer; box-shadow: 0 10px 25px rgba(218, 37, 28, 0.4); z-index: 1000; transition: 0.3s; display: flex; align-items: center; gap: 10px; }
    .tts-btn:hover { transform: translateY(-5px); background: #000; }
    
    footer { background: var(--dark-bg); color: #888; padding: 60px 20px 30px; margin-top: 60px; text-align: center; }
    .footer-links a { color: #ccc; text-decoration: none; margin: 0 15px; font-size: 15px; }
    .footer-links a:hover { color: white; }
    
    .grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); gap: 30px; margin-top: 30px; }
    .card { background: white; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 15px rgba(0,0,0,0.05); transition: 0.3s; }
    .card:hover { transform: translateY(-5px); box-shadow: 0 8px 25px rgba(0,0,0,0.1); }
    .card img { width: 100%; height: 220px; object-fit: cover; }
    .card-content { padding: 25px; }
    .card-content h3 { font-size: 22px; margin: 0 0 15px 0; line-height: 1.4; }
    .card-content a { color: var(--main-red); font-weight: bold; text-decoration: none; }
</style>
"""

# ---------------------------------------------------------
# GENERATE POST HTML
# ---------------------------------------------------------
header_html = f"""
    <div class="top-bar">🔥 TRENDING: {current_year} Best Tech, AI Income, Future Jobs</div>
    <header>
        <div class="nav-container">
            <a href="index.html" class="logo">Digital Kamai Hub</a>
            <div class="nav-links"><a href="index.html">Home</a><a href="about.html">About</a></div>
        </div>
    </header>
"""

footer_html = f"""
    <footer>
        <div class="footer-links"><a href="about.html">About Us</a> | <a href="privacy.html">Privacy Policy</a> | <a href="disclaimer.html">Disclaimer</a></div>
        <p style="margin-top:20px; font-size:13px;">&copy; {current_year} Digital Kamai Hub. All Rights Reserved.</p>
    </footer>
"""

article_page = f"""<!DOCTYPE html>
<html lang="hi">
<head>
    <meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{current_topic}</title>
    <meta name="description" content="{meta_desc}">
    <meta name="keywords" content="{meta_keywords}">
    {premium_css}
</head>
<body>
    {header_html}
    <div class="container">
        <h1>{current_topic}</h1>
        <div class="meta">📅 प्रकाशित: {today_date} | ✍️ लेखक: AI Expert</div>
        <img src="{main_img_url}" class="hero-img" alt="Hero Image">
        <div id="article-body">{blog_content}</div>
    </div>
    
    <button class="tts-btn" onclick="toggleTTS()" id="ttsBtn">🔊 लेख सुनें</button>
    {footer_html}

    <script>
        let synth = window.speechSynthesis;
        let isReading = false;
        function toggleTTS() {{
            if (isReading) {{
                synth.cancel();
                document.getElementById('ttsBtn').innerHTML = '🔊 लेख सुनें';
                isReading = false;
            }} else {{
                let text = document.getElementById('article-body').innerText;
                let utter = new SpeechSynthesisUtterance(text);
                utter.lang = 'hi-IN'; 
                utter.rate = 0.85; // बहुत सॉफ्ट और आराम से पढ़ने के लिए
                utter.pitch = 1.0;
                
                // बेहतरीन हिंदी आवाज़ ढूँढना
                let voices = synth.getVoices();
                let hiVoice = voices.find(v => v.lang === 'hi-IN' || v.lang.includes('hi'));
                if(hiVoice) utter.voice = hiVoice;

                synth.speak(utter);
                document.getElementById('ttsBtn').innerHTML = '⏹️ आवाज़ बंद करें';
                isReading = true;
                utter.onend = () => {{ document.getElementById('ttsBtn').innerHTML = '🔊 लेख सुनें'; isReading = false; }};
            }}
        }}
        // ब्राउज़र को आवाज़ें लोड करने का टाइम देना
        window.speechSynthesis.onvoiceschanged = function() {{ window.speechSynthesis.getVoices(); }};
    </script>
</body>
</html>"""

with open(post_filename, "w", encoding="utf-8") as f: f.write(article_page)

# ---------------------------------------------------------
# GENERATE HOME PAGE
# ---------------------------------------------------------
home_cards = "".join([f"""
    <div class="card">
        <img src="{p['img']}" alt="Thumbnail">
        <div class="card-content">
            <h3><a href="{p['file']}" style="color:#000; text-decoration:none;">{p['title']}</a></h3>
            <p style="color:#888; font-size:14px; margin-bottom:15px;">🗓 {p['date']}</p>
            <a href="{p['file']}">पूरा लेख पढ़ें →</a>
        </div>
    </div>
""" for p in posts_db])

with open("index.html", "w", encoding="utf-8") as f:
    f.write(f"<!DOCTYPE html><html lang='hi'><head><meta charset='UTF-8'><meta name="viewport" content="width=device-width, initial-scale=1.0"><title>Digital Kamai Hub</title>{premium_css}</head><body>{header_html}<div style='max-width:1100px; margin:40px auto; padding:0 20px;'><h2 style='font-size:32px; border-bottom:3px solid #da251c; padding-bottom:10px; display:inline-block;'>🔥 ताज़ा ख़बरें</h2><div class='grid'>{home_cards}</div></div>{footer_html}</body></html>")

# ---------------------------------------------------------
# GENERATE STATIC PAGES (About, Privacy, Disclaimer)
# ---------------------------------------------------------
pages = {
    "about": ("About Us", "Digital Kamai Hub भारत का नंबर 1 AI और टेक्नोलॉजी ब्लॉग है। हम आपको भविष्य की तकनीक से पैसे कमाने के तरीके सिखाते हैं।"),
    "privacy": ("Privacy Policy", "आपकी प्राइवेसी हमारे लिए महत्वपूर्ण है। हम आपकी कोई भी व्यक्तिगत जानकारी बिना अनुमति के किसी तीसरे पक्ष (Third Party) को नहीं बेचते।"),
    "disclaimer": ("Disclaimer", "इस वेबसाइट पर दी गई सभी जानकारी केवल शिक्षा और जागरूकता के लिए है। कृपया कोई भी वित्तीय निर्णय (Financial Decision) लेने से पहले अपने सलाहकार से बात करें।")
}

for p_file, (p_title, p_content) in pages.items():
    with open(f"{p_file}.html", "w", encoding="utf-8") as f:
        f.write(f"<!DOCTYPE html><html lang='hi'><head><meta charset='UTF-8'><meta name="viewport" content="width=device-width, initial-scale=1.0"><title>{p_title} | Digital Kamai Hub</title>{premium_css}</head><body>{header_html}<div class='container'><h1>{p_title}</h1><p style='font-size:18px; color:#555;'>{p_content}</p></div>{footer_html}</body></html>")
