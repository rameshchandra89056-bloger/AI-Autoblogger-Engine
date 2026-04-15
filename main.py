import urllib.request
import urllib.parse
import json
import os
import sys
import time

# ==========================================
# THE IMMORTAL SYSTEM - THE PERFECTIONIST (v33.0)
# Ultra-Soft TTS + Auto-Cleanup + Multi-Key Solar
# ==========================================

raw_keys = os.environ.get("GEMINI_API_KEY", "")
API_KEYS = [k.strip() for k in raw_keys.split(",") if k.strip()]
if not API_KEYS: sys.exit(1)

current_year = time.strftime("%Y")
today_date = time.strftime("%d %B %Y")
post_id = int(time.time())

# 1. डेटाबेस लोड (पुरानी बिना फोटो वाली पोस्ट्स की छुट्टी)
posts_db = []
past_titles = []
if os.path.exists("posts.json"):
    with open("posts.json", "r", encoding="utf-8") as f:
        try:
            raw_db = json.load(f)
            # सिर्फ वही पोस्ट दिखाओ जिनमें फोटो (img) है!
            posts_db = [p for p in raw_db if "img" in p]
            past_titles = [post["title"] for post in posts_db][:20] 
        except: pass

# मॉडल हंटर
available_model = "models/gemini-1.5-flash"
list_url = f"https://generativelanguage.googleapis.com/v1beta/models?key={API_KEYS[0]}"
try:
    req = urllib.request.Request(list_url)
    with urllib.request.urlopen(req, timeout=30) as response:
        res = json.loads(response.read().decode('utf-8'))
        for m in res.get('models', []):
            if 'generateContent' in m.get('supportedGenerationMethods', []) and 'flash' in m.get('name', '').lower():
                available_model = m['name']; break
except: pass

def ask_ai(prompt, retries=10):
    for i in range(retries):
        current_key = API_KEYS[i % len(API_KEYS)]
        api_url = f"https://generativelanguage.googleapis.com/v1beta/{available_model}:generateContent?key={current_key}"
        try:
            data = json.dumps({"contents": [{"parts": [{"text": prompt}]}]}).encode('utf-8')
            req = urllib.request.Request(api_url, data=data, headers={'Content-Type': 'application/json'})
            with urllib.request.urlopen(req, timeout=60) as response:
                res = json.loads(response.read().decode('utf-8'))
                return res['candidates'][0]['content']['parts'][0]['text'].strip()
        except: time.sleep(5)
    return ""

# --- AGENT 1: TOPIC ---
topic_prompt = f"तुम एक ट्रेंड एनालिस्ट हो। {current_year} में ऑनलाइन कमाई या AI पर एक नया वायरल ब्लॉग टाइटल (हिंदी में) दो। पुराने टाइटल्स: {past_titles} से अलग हो। सिर्फ 'टाइटल' लिखना।"
current_topic = ask_ai(topic_prompt).replace('"', '').replace("'", "").replace("*", "")
if not current_topic: sys.exit(1)

# --- AGENT 2: SEO ---
seo_prompt = f"विषय: '{current_topic}'। सिर्फ इस फॉर्मेट में जवाब दो: MAIN_IMG_KEYWORD | SEO_DESC | SEO_KEYWORDS. कोई और शब्द मत लिखना।"
seo_raw = ask_ai(seo_prompt)
main_img_words = "futuristic AI"
meta_desc = "Digital Kamai Hub Post"
meta_keywords = "AI, Make Money"
try:
    if "|" in seo_raw:
        parts = seo_raw.split("|")
        main_img_words, meta_desc, meta_keywords = parts[0].strip(), parts[1].strip(), parts[2].strip()
except: pass

# --- AGENT 3: HTML CODER ---
html_prompt = f"""विषय: '{current_topic}'। एक विस्तृत हिंदी ब्लॉग पोस्ट लिखो।
नियम:
1. लेख के बीच में 2 जगह फोटो: <img src="https://image.pollinations.ai/prompt/ENG_KEYWORD?width=800&height=400&nologo=true" class="article-img">
2. 1 जगह यूट्यूब बटन: <a href="https://www.youtube.com/results?search_query={urllib.parse.quote(current_topic)}" target="_blank" class="yt-btn">📺 यूट्यूब पर इस विषय का वीडियो देखें</a>
3. सिर्फ HTML कोड (h2, p, ul) देना।"""

blog_content = ask_ai(html_prompt, retries=15).replace("```html", "").replace("```", "").strip()
if not blog_content or len(blog_content) < 200: sys.exit(1)

# --- PUBLISHING ---
main_img_url = f"https://image.pollinations.ai/prompt/{urllib.parse.quote(main_img_words)}?width=1200&height=600&nologo=true"
post_filename = f"post_{post_id}.html"
posts_db.insert(0, {"title": current_topic, "file": post_filename, "date": today_date, "img": main_img_url})
with open("posts.json", "w", encoding="utf-8") as f: json.dump(posts_db, f, ensure_ascii=False, indent=4)

# PREMIUM CSS
premium_css = """
    <style>
        :root { --primary: #2563eb; --bg: #f8fafc; --text: #0f172a; }
        body { font-family: 'Segoe UI', sans-serif; background: var(--bg); color: var(--text); line-height: 1.8; margin: 0; }
        header { background: white; padding: 15px 20px; position: sticky; top: 0; box-shadow: 0 2px 10px rgba(0,0,0,0.05); z-index: 100; text-align: center; }
        .logo { font-size: 24px; font-weight: 800; color: var(--primary); text-decoration: none; }
        .main-container { max-width: 800px; margin: 40px auto; padding: 0 20px; background: white; border-radius: 15px; padding: 30px; }
        .hero-img, .article-img { width: 100%; border-radius: 12px; margin: 20px 0; box-shadow: 0 5px 15px rgba(0,0,0,0.1); }
        .yt-btn { display: block; background: #ff0000; color: white; text-align: center; padding: 15px; border-radius: 8px; text-decoration: none; font-weight: bold; margin: 30px 0; box-shadow: 0 4px 10px rgba(255,0,0,0.2); }
        .tts-btn { position: fixed; bottom: 20px; right: 20px; background: var(--primary); color: white; border: none; padding: 15px 25px; border-radius: 50px; font-weight: bold; cursor: pointer; box-shadow: 0 5px 15px rgba(37, 99, 235, 0.4); z-index: 1000; transition: 0.3s; }
        footer { text-align: center; padding: 40px; background: #0f172a; color: white; margin-top: 50px; }
    </style>
"""

article_html = f"""<!DOCTYPE html>
<html lang="hi">
<head>
    <meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{current_topic}</title>
    <meta name="description" content="{meta_desc}">
    {premium_css}
</head>
<body>
    <header><a href="index.html" class="logo">🚀 Digital Kamai Hub</a></header>
    <div class="main-container">
        <h1>{current_topic}</h1>
        <p style="color:#64748b;">🗓️ {today_date}</p>
        <img src="{main_img_url}" class="hero-img">
        <div id="article-content">{blog_content}</div>
    </div>
    <button class="tts-btn" onclick="speakArticle()" id="speakBtn">🔊 लेख सुनें (Soft Voice)</button>
    <footer><p>&copy; {current_year} Digital Kamai Hub</p></footer>
    
    <script>
        let isPlaying = false;
        let speech = new SpeechSynthesisUtterance();

        function speakArticle() {{
            if (isPlaying) {{
                window.speechSynthesis.cancel();
                document.getElementById("speakBtn").innerHTML = "🔊 लेख सुनें";
                isPlaying = false;
            }} else {{
                let text = document.getElementById("article-content").innerText;
                speech.text = text;
                speech.lang = 'hi-IN';
                speech.rate = 0.85; // सॉफ्ट और धीरे पढ़ने के लिए
                speech.pitch = 1.1; // मीठी आवाज़ के लिए
                
                // बेहतरीन आवाज़ ढूँढना
                let voices = window.speechSynthesis.getVoices();
                let hindiVoice = voices.find(v => v.lang.includes('hi'));
                if(hindiVoice) speech.voice = hindiVoice;

                window.speechSynthesis.speak(speech);
                document.getElementById("speakBtn").innerHTML = "⏹️ आवाज़ बंद करें";
                isPlaying = true;
                speech.onend = () => {{ document.getElementById("speakBtn").innerHTML = "🔊 लेख सुनें"; isPlaying = false; }};
            }}
        }}
    </script>
</body>
</html>"""

with open(post_filename, "w", encoding="utf-8") as f: f.write(article_html)

# HOME PAGE
post_links = "".join([f'<div style="background:white; border-radius:12px; overflow:hidden; box-shadow:0 4px 6px rgba(0,0,0,0.05); border:1px solid #e2e8f0; margin-bottom:20px;"><img src="{p["img"]}" style="width:100%; height:200px; object-fit:cover;"><div style="padding:20px;"><h3><a href="{p["file"]}" style="color:var(--text); text-decoration:none;">{p["title"]}</a></h3><p style="color:#64748b;">{p["date"]}</p></div></div>' for p in posts_db])

home_html = f"""<!DOCTYPE html><html lang="hi"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"><title>Digital Kamai Hub</title>{premium_css}</head><body><header><a href="index.html" class="logo">🚀 Digital Kamai Hub</a></header><div class="main-container"><h2>🔥 ताज़ा लेख</h2>{post_links}</div><footer><p>&copy; {current_year} Digital Kamai Hub</p></footer></body></html>"""
with open("index.html", "w", encoding="utf-8") as f: f.write(home_html)
