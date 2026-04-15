import urllib.request
import urllib.parse
import json
import os
import sys
import time

# ==========================================
# THE IMMORTAL SYSTEM - MASTER ARCHITECT (v27.0)
# Multi-Agent System (No Formatting Errors!)
# ==========================================

raw_key = os.environ.get("GEMINI_API_KEY", "")
API_KEY = raw_key.strip()
if not API_KEY: sys.exit(1)

current_year = time.strftime("%Y")
today_date = time.strftime("%d %B %Y")
post_id = int(time.time())

# 1. डेटाबेस लोड
posts_db = []
past_titles = []
if os.path.exists("posts.json"):
    with open("posts.json", "r", encoding="utf-8") as f:
        try:
            posts_db = json.load(f)
            past_titles = [post["title"] for post in posts_db][:20] 
        except: pass

# मॉडल सेटअप
list_url = f"https://generativelanguage.googleapis.com/v1beta/models?key={API_KEY}"
available_model = "models/gemini-1.5-flash"
try:
    req = urllib.request.Request(list_url)
    with urllib.request.urlopen(req, timeout=30) as response:
        res = json.loads(response.read().decode('utf-8'))
        for m in res.get('models', []):
            if 'generateContent' in m.get('supportedGenerationMethods', []) and 'gemini-1.5-flash' in m.get('name', '').lower():
                available_model = m['name']; break
except: pass

api_url = f"https://generativelanguage.googleapis.com/v1beta/{available_model}:generateContent?key={API_KEY}"

# मास्टर AI फंक्शन (ऑटो-रिकवरी के साथ)
def ask_ai(prompt, retries=5):
    for i in range(retries):
        try:
            data = json.dumps({"contents": [{"parts": [{"text": prompt}]}]}).encode('utf-8')
            req = urllib.request.Request(api_url, data=data, headers={'Content-Type': 'application/json'})
            with urllib.request.urlopen(req, timeout=60) as response:
                res = json.loads(response.read().decode('utf-8'))
                return res['candidates'][0]['content']['parts'][0]['text'].strip()
        except Exception as e:
            print(f"⚠️ API लोड एरर, 5 सेकंड बाद फिर कोशिश... ({i+1}/{retries})")
            time.sleep(5)
    return ""

print("🚀 रोबोट चालू हो गया है...")

# ---------------------------------------------------------
# AGENT 1: TOPIC RESEARCH
# ---------------------------------------------------------
print("🧠 एजेंट 1: टॉपिक ढूँढ रहा है...")
topic_prompt = f"तुम एक ट्रेंड एनालिस्ट हो। {current_year} में मेक मनी ऑनलाइन या AI से जुड़ा एक वायरल ब्लॉग टाइटल (हिंदी में) दो। पुराने टाइटल्स: {past_titles} से अलग हो। जवाब में सिर्फ 'टाइटल' लिखना, कोई फालतू शब्द नहीं।"
current_topic = ask_ai(topic_prompt).replace('"', '').replace("'", "").replace("*", "")
if not current_topic: sys.exit(1)
print(f"🎯 टॉपिक: {current_topic}")

# ---------------------------------------------------------
# AGENT 2: SEO & METADATA
# ---------------------------------------------------------
print("📊 एजेंट 2: SEO डेटा बना रहा है...")
seo_prompt = f"विषय: '{current_topic}'। मुझे सिर्फ इस एक लाइन के फॉर्मेट में जवाब दो: MAIN_IMAGE_ENGLISH_KEYWORD | HINDI_SEO_DESCRIPTION | 5_SEO_KEYWORDS_COMMA_SEPARATED. कोई और शब्द मत लिखना।"
seo_raw = ask_ai(seo_prompt)

# डिफ़ॉल्ट SEO (अगर AI ने गड़बड़ की)
main_img_words = "futuristic digital technology"
meta_desc = f"{current_year} का बेस्ट ब्लॉग पोस्ट।"
meta_keywords = f"AI, Make Money, {current_year}"

try:
    if "|" in seo_raw:
        parts = seo_raw.split("|")
        if len(parts) >= 3:
            main_img_words = parts[0].strip()
            meta_desc = parts[1].strip()
            meta_keywords = parts[2].strip()
except: pass

# ---------------------------------------------------------
# AGENT 3: HTML CODER (Video + Images)
# ---------------------------------------------------------
print("💻 एजेंट 3: HTML कोडिंग और मल्टीमीडिया लगा रहा है...")
html_prompt = f"""तुम एक वेब डेवलपर और ब्लॉगर हो। विषय: '{current_topic}'।
एक विस्तृत हिंदी ब्लॉग पोस्ट लिखो।
नियम:
1. लेख के बीच में कम से कम 2 जगह ये फोटो कोड लगाओ: <img src="https://image.pollinations.ai/prompt/ENG_KEYWORD?width=800&height=400&nologo=true" class="article-img"> (ENG_KEYWORD की जगह पैराग्राफ से जुड़ा इंग्लिश शब्द डालना)।
2. लेख के बीच में 1 जगह यूट्यूब वीडियो लगाओ: <iframe class="article-video" src="https://www.youtube.com/embed?listType=search&list=ENG_SEARCH_TERM" frameborder="0" allowfullscreen></iframe> (ENG_SEARCH_TERM की जगह इंग्लिश सर्च कीवर्ड डालना)।
3. मुझे जवाब में सिर्फ और सिर्फ HTML कोड (h2, p, ul) देना। कोई ```html या markdown मत लगाना। कोई Introduction मत देना।"""

blog_content = ask_ai(html_prompt, retries=10)
if not blog_content or len(blog_content) < 200:
    print("❌ HTML कोडिंग फेल हो गई।")
    sys.exit(1)

blog_content = blog_content.replace("```html", "").replace("```", "").strip()

# ---------------------------------------------------------
# STEP 4: PUBLISHING & TEXT-TO-SPEECH
# ---------------------------------------------------------
print("✅ पोस्ट तैयार है! पब्लिश हो रही है...")
main_img_safe = urllib.parse.quote(main_img_words)
main_img_url = f"[https://image.pollinations.ai/prompt/](https://image.pollinations.ai/prompt/){main_img_safe}?width=800&height=400&nologo=true"

post_filename = f"post_{post_id}.html"
posts_db.insert(0, {"title": current_topic, "file": post_filename, "date": today_date})

with open("posts.json", "w", encoding="utf-8") as f:
    json.dump(posts_db, f, ensure_ascii=False, indent=4)

header_menu = """
    <nav style="background: white; padding: 15px; text-align: center; position: sticky; top: 0; box-shadow: 0 2px 10px rgba(0,0,0,0.05); z-index: 100;">
        <a href="index.html" style="color: #203a43; text-decoration: none; margin: 0 15px; font-weight: bold; font-size: 18px;">🏠 होम</a>
        <a href="index.html" style="color: #203a43; text-decoration: none; margin: 0 15px; font-weight: bold; font-size: 18px;">🔥 लेटेस्ट न्यूज़</a>
    </nav>
"""

footer_html = """
    <footer style="text-align: center; padding: 40px 20px; background: #111; color: #aaa; margin-top: 50px; font-size: 14px;">
        <div style="margin-bottom: 20px;">
            <a href="about.html" style="color: #aaa; text-decoration: none; margin: 0 15px;">About Us</a> |
            <a href="privacy.html" style="color: #aaa; text-decoration: none; margin: 0 15px;">Privacy Policy</a> |
            <a href="disclaimer.html" style="color: #aaa; text-decoration: none; margin: 0 15px;">Disclaimer</a>
        </div>
        <p>&copy; 2026 Digital Kamai Hub</p>
    </footer>
"""

full_html = f"""<!DOCTYPE html>
<html lang="hi">
<head>
    <meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{current_topic} | Digital Kamai Hub</title>
    <meta name="description" content="{meta_desc}">
    <meta name="keywords" content="{meta_keywords}">
    <style>
        body {{ font-family: 'Segoe UI', Tahoma, sans-serif; background: #f4f7f9; margin: 0; color: #333; }}
        header {{ background: #1a2a3a; color: white; padding: 40px 20px; text-align: center; }}
        nav {{ background: white; padding: 15px; text-align: center; position: sticky; top: 0; box-shadow: 0 2px 5px rgba(0,0,0,0.1); z-index: 100; }}
        nav a {{ color: #1a2a3a; text-decoration: none; margin: 0 15px; font-weight: bold; }}
        .container {{ max-width: 850px; margin: 30px auto; background: white; padding: 40px; border-radius: 10px; box-shadow: 0 5px 20px rgba(0,0,0,0.05); }}
        .article-img, .article-video {{ width: 100%; border-radius: 10px; margin: 25px 0; box-shadow: 0 4px 12px rgba(0,0,0,0.1); }}
        .article-video {{ height: 400px; }}
        h1 {{ color: #1a2a3a; font-size: 34px; line-height: 1.4; }}
        h2 {{ color: #2c3e50; border-left: 5px solid #3498db; padding-left: 15px; margin-top: 35px; }}
        p {{ line-height: 1.8; font-size: 18px; color: #444; }}
        .tts-btn {{ background: linear-gradient(135deg, #3498db, #2980b9); color: white; border: none; padding: 12px 25px; border-radius: 50px; cursor: pointer; font-size: 16px; font-weight: bold; display: inline-flex; align-items: center; gap: 10px; box-shadow: 0 4px 10px rgba(52, 152, 219, 0.3); transition: 0.3s; margin-bottom: 20px; }}
        .tts-btn:hover {{ transform: scale(1.05); }}
        @media (max-width: 600px) {{ .article-video {{ height: 250px; }} }}
    </style>
</head>
<body>
    <header><h1>🚀 Digital Kamai Hub</h1><p>The Future of AI Automation</p></header>
    {header_menu}
    <div class="container">
        <h1>{current_topic}</h1>
        <p style="color:#999;">📅 {today_date}</p>
        
        <button class="tts-btn" onclick="speakArticle()" id="speakBtn">🔊 लेख सुनें (Listen)</button>
        <img src="{main_img_url}" class="article-img" alt="Main Header">
        
        <div id="article-content">
            {blog_content}
        </div>
    </div>
    {footer_html}

    <script>
        let isPlaying = false;
        let speech = new SpeechSynthesisUtterance();
        
        function speakArticle() {{
            if (isPlaying) {{
                window.speechSynthesis.cancel();
                document.getElementById("speakBtn").innerHTML = "🔊 लेख सुनें (Listen)";
                isPlaying = false;
            }} else {{
                let textToRead = document.getElementById("article-content").innerText;
                speech.text = textToRead;
                speech.lang = 'hi-IN';
                speech.rate = 0.9;
                window.speechSynthesis.speak(speech);
                document.getElementById("speakBtn").innerHTML = "⏹️ सुनना बंद करें (Stop)";
                isPlaying = true;

                speech.onend = function() {{
                    document.getElementById("speakBtn").innerHTML = "🔊 लेख सुनें (Listen)";
                    isPlaying = false;
                }};
            }}
        }}
    </script>
</body>
</html>"""

with open(post_filename, "w", encoding="utf-8") as f:
    f.write(full_html)

post_links = "".join([f'<div style="background:white; padding:20px; margin-bottom:20px; border-radius:10px; border:1px solid #eee;"><h3><a href="{p["file"]}" style="color:#1a2a3a; text-decoration:none;">{p["title"]}</a></h3><p style="color:#666;">📅 {p["date"]}</p></div>' for p in posts_db])
with open("index.html", "w", encoding="utf-8") as f:
    f.write(f'<!DOCTYPE html><html lang="hi"><head><meta charset="UTF-8"><title>Digital Kamai Hub</title><style>body{{font-family:sans-serif; background:#f4f7f9; margin:0;}} header{{background:#1a2a3a; color:white; padding:50px; text-align:center;}} .container{{max-width:800px; margin:30px auto; padding:20px;}}</style></head><body><header><h1>🚀 Digital Kamai Hub</h1></header>{header_menu}<div class="container"><h2>ताज़ा लेख</h2>{post_links}</div>{footer_html}</body></html>')
