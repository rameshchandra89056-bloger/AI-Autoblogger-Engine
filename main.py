import urllib.request
import urllib.parse
import json
import os
import sys
import time
import re

# ==========================================
# THE IMMORTAL SYSTEM - NATURAL VOICE EDITION
# ==========================================

raw_keys = os.environ.get("GEMINI_API_KEY", "")
API_KEYS = [k.strip() for k in raw_keys.split(",") if k.strip()]
if not API_KEYS: sys.exit(1)

current_year = time.strftime("%Y")
today_date = time.strftime("%d %B %Y")
post_id = int(time.time())

posts_db = []
if os.path.exists("posts.json"):
    with open("posts.json", "r", encoding="utf-8") as f:
        try:
            raw_db = json.load(f)
            posts_db = [p for p in raw_db if "img" in p]
        except: pass

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
# TOPIC & SEO AGENTS
# ---------------------------------------------------------
topic_prompt = f"तुम एक ट्रेंड एनालिस्ट हो। {current_year} में मेक मनी ऑनलाइन या AI पर एक धांसू और वायरल हिंदी ब्लॉग टाइटल दो। पुराने टाइटल्स: {[p['title'] for p in posts_db[:5]]} से अलग हो। सिर्फ 'टाइटल' लिखना।"
current_topic = ask_ai(topic_prompt).replace('"', '').replace("'", "").replace("*", "")
if not current_topic: sys.exit(1)

seo_prompt = f"विषय: '{current_topic}'। सिर्फ इस फॉर्मेट में जवाब दो: MAIN_IMG_ENGLISH_KEYWORD | SEO_DESCRIPTION | SEO_KEYWORDS. (ध्यान दें: MAIN_IMG_ENGLISH_KEYWORD में 'Robot' या 'Cyborg' मत लिखना, कुछ अलग जैसे 'laptop workspace', 'financial growth' लिखना)"
seo_raw = ask_ai(seo_prompt)

main_img_words = "modern business workspace"
meta_desc = f"Digital Kamai Hub - {current_year}"
meta_keywords = "AI, Online Income"
try:
    if "|" in seo_raw:
        parts = seo_raw.split("|")
        clean_words = re.sub(r'[^a-zA-Z0-9\s]', '', parts[0]).strip()
        if clean_words: main_img_words = clean_words
        meta_desc, meta_keywords = parts[1].strip(), parts[2].strip()
except: pass

html_prompt = f"""तुम एक प्रो ब्लॉगर हो। विषय: '{current_topic}'। 
कम से कम 1000 शब्दों का एक बहुत शानदार हिंदी ब्लॉग पोस्ट लिखो।
नियम:
1. पोस्ट के बीच-बीच में 3 अलग-अलग जगह बिलकुल ऐसे ही लिख दो: [PHOTO]
2. सिर्फ HTML कोड (h2, p, strong, ul) देना।"""

blog_content = ask_ai(html_prompt, retries=20).replace("```html", "").replace("```", "").strip()
if not blog_content or len(blog_content) < 300: sys.exit(1)

# 🎨 IMAGE GENERATOR
modifiers = ["creative_workspace", "success_chart", "modern_office"]
for mod in modifiers:
    if "[PHOTO]" in blog_content:
        dynamic_keyword = urllib.parse.quote(f"{main_img_words} {mod}")
        img_html = f"<img src='https://image.pollinations.ai/prompt/{dynamic_keyword}?width=800&height=400&nologo=true' class='article-img'>"
        blog_content = blog_content.replace("[PHOTO]", img_html, 1)

main_img_url = f"https://image.pollinations.ai/prompt/{urllib.parse.quote(main_img_words)}?width=1200&height=600&nologo=true"
post_filename = f"post_{post_id}.html"

# SAVE TO DB
posts_db.insert(0, {"title": current_topic, "file": post_filename, "date": today_date, "img": main_img_url})
with open("posts.json", "w", encoding="utf-8") as f: json.dump(posts_db, f, ensure_ascii=False, indent=4)

# ---------------------------------------------------------
# PREMIUM CSS & HTML
# ---------------------------------------------------------
premium_css = """
<style>
    :root { --main-red: #da251c; --dark-bg: #111; }
    * { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Segoe UI', sans-serif; }
    body { background: #f0f2f5; line-height: 1.8; }
    .container { max-width: 850px; margin: 40px auto; background: white; padding: 40px; border-radius: 12px; box-shadow: 0 5px 20px rgba(0,0,0,0.05); }
    h1 { font-size: 36px; margin-bottom: 20px; color: #000; text-align: center; }
    .hero-img { width: 100%; border-radius: 12px; margin-bottom: 30px; }
    .article-img { width: 100%; border-radius: 10px; margin: 30px 0; }
    #article-body { font-size: 19px; color: #333; }
    #article-body h2 { margin-top: 30px; color: var(--main-red); border-left: 5px solid #000; padding-left: 15px; }
    .tts-btn { position: fixed; bottom: 30px; right: 30px; background: #000; color: white; border: none; padding: 15px 30px; border-radius: 50px; font-weight: bold; cursor: pointer; box-shadow: 0 5px 15px rgba(0,0,0,0.3); z-index: 1000; display: flex; align-items: center; gap: 10px; }
    .yt-btn { display: block; background: #ff0000; color: white; text-align: center; padding: 15px; border-radius: 8px; text-decoration: none; font-weight: bold; margin-top: 30px; }
    header { background: white; padding: 15px; text-align: center; border-bottom: 2px solid #eee; position: sticky; top: 0; z-index: 100; }
    .logo { color: var(--main-red); font-size: 24px; font-weight: 900; text-decoration: none; }
</style>
"""

# ---------------------------------------------------------
# THE NATURAL VOICE JAVASCRIPT (THE CORE FIX)
# ---------------------------------------------------------
tts_script = """
<script>
    let synth = window.speechSynthesis;
    let isReading = false;
    let currentUtterance = null;

    function toggleTTS() {
        if (isReading) {
            synth.cancel();
            isReading = false;
            document.getElementById('ttsBtn').innerHTML = '🔊 लेख सुनें';
            return;
        }

        let container = document.getElementById('article-body');
        let text = container.innerText;
        
        currentUtterance = new SpeechSynthesisUtterance(text);
        
        // 🛠 NATURAL VOICE SELECTION LOGIC
        let voices = synth.getVoices();
        
        // Priority: Google Hindi, Microsoft Hemant, then any Hindi
        let bestVoice = voices.find(v => v.name.includes('Google') && v.lang.includes('hi')) || 
                        voices.find(v => v.name.includes('Natural') && v.lang.includes('hi')) ||
                        voices.find(v => v.lang.includes('hi'));
        
        if (bestVoice) currentUtterance.voice = bestVoice;
        
        currentUtterance.lang = 'hi-IN';
        currentUtterance.rate = 0.9;  // थोड़ी धीमी रफ़्तार = ज़्यादा नेचुरल
        currentUtterance.pitch = 1.0; // नॉर्मल आवाज़

        currentUtterance.onstart = () => {
            isReading = true;
            document.getElementById('ttsBtn').innerHTML = '⏹️ आवाज़ बंद करें';
        };

        currentUtterance.onend = () => {
            isReading = false;
            document.getElementById('ttsBtn').innerHTML = '🔊 लेख सुनें';
        };

        synth.speak(currentUtterance);
    }
    
    // ब्राउज़र आवाज़ों को लोड होने में समय लेता है
    window.speechSynthesis.onvoiceschanged = () => { console.log("Voices Loaded"); };
</script>
"""

# HTML GENERATION
article_page = f"""<!DOCTYPE html>
<html lang="hi">
<head>
    <meta charset="UTF-8"><title>{current_topic}</title>
    {premium_css}
</head>
<body>
    <header><a href="index.html" class="logo">Digital Kamai Hub</a></header>
    <div class="container">
        <h1>{current_topic}</h1>
        <img src="{main_img_url}" class="hero-img">
        <div id="article-body">{blog_content}</div>
        <a href="https://www.youtube.com/results?search_query={urllib.parse.quote(current_topic)}" class="yt-btn">📺 यूट्यूब वीडियो देखें</a>
    </div>
    <button class="tts-btn" onclick="toggleTTS()" id="ttsBtn">🔊 लेख सुनें</button>
    {tts_script}
</body>
</html>"""

with open(post_filename, "w", encoding="utf-8") as f: f.write(article_page)
print(f"✅ Success: {post_filename} created with Natural Voice!")
