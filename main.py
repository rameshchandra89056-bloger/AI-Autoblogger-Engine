import urllib.request
import urllib.parse
import json
import os
import sys
import time

# ==========================================
# THE IMMORTAL SYSTEM - NEWS PORTAL ELITE (v34.0)
# Aaj Tak Level Design + Ultra-Soft TTS + Professional Footer
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
api_url = f"https://generativelanguage.googleapis.com/v1beta/{available_model}:generateContent?key={API_KEYS[0]}"

def ask_ai(prompt, retries=10):
    for i in range(retries):
        current_key = API_KEYS[i % len(API_KEYS)]
        url = f"https://generativelanguage.googleapis.com/v1beta/{available_model}:generateContent?key={current_key}"
        try:
            data = json.dumps({"contents": [{"parts": [{"text": prompt}]}]}).encode('utf-8')
            req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'})
            with urllib.request.urlopen(req, timeout=60) as response:
                res = json.loads(response.read().decode('utf-8'))
                return res['candidates'][0]['content']['parts'][0]['text'].strip()
        except: time.sleep(5)
    return ""

# --- AGENTS WORK ---
topic_prompt = f"मेक मनी ऑनलाइन पर आज का सबसे ट्रेंडिंग वायरल हिंदी टाइटल दो। पुराने: {[p['title'] for p in posts_db[:5]]} से अलग हो।"
current_topic = ask_ai(topic_prompt).replace('"', '').replace("'", "")

seo_prompt = f"विषय: '{current_topic}'। फॉर्मेट: KEYWORD | DESC | KEYWORDS"
seo_raw = ask_ai(seo_prompt)
img_k = "business technology"
m_desc = "Trending News"
if "|" in seo_raw:
    parts = seo_raw.split("|")
    img_k, m_desc = parts[0].strip(), parts[1].strip()

html_prompt = f"विषय: '{current_topic}' पर 1500 शब्दों का प्रीमियम न्यूज़ लेख लिखो। इसमें 2 फोटो <img src='https://image.pollinations.ai/prompt/ENG_KEYWORD?width=800&height=400&nologo=true' class='post-img'> और 1 यूट्यूब बटन <a href='https://www.youtube.com/results?search_query={urllib.parse.quote(current_topic)}' target='_blank' class='news-yt-btn'>📺 वीडियो देखें</a> जरूर डालें।"
blog_content = ask_ai(html_prompt, retries=15).replace("```html", "").replace("```", "").strip()

# --- DATABASE UPDATE ---
main_img_url = f"https://image.pollinations.ai/prompt/{urllib.parse.quote(img_k)}?width=1200&height=600&nologo=true"
post_filename = f"post_{post_id}.html"
posts_db.insert(0, {"title": current_topic, "file": post_filename, "date": today_date, "img": main_img_url})
with open("posts.json", "w", encoding="utf-8") as f: json.dump(posts_db, f, ensure_ascii=False, indent=4)

# --- PREMIUM NEWS CSS (Aaj Tak Level) ---
news_css = """
<style>
    :root { --main-red: #da251c; --dark-bg: #1a1a1a; --text-gray: #555; }
    * { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Poppins', sans-serif; }
    body { background: #f4f4f4; color: #333; }
    
    /* Aaj Tak Style Header */
    header { background: white; border-top: 4px solid var(--main-red); box-shadow: 0 2px 10px rgba(0,0,0,0.1); position: sticky; top: 0; z-index: 1000; }
    .nav-top { max-width: 1200px; margin: 0 auto; padding: 15px 20px; display: flex; justify-content: space-between; align-items: center; }
    .logo { font-size: 28px; font-weight: 900; color: var(--main-red); text-decoration: none; text-transform: uppercase; }
    .trending-bar { background: var(--main-red); color: white; padding: 5px 0; font-size: 13px; text-align: center; }

    /* Article UI */
    .container { max-width: 900px; margin: 30px auto; background: white; padding: 40px; border-radius: 4px; box-shadow: 0 0 20px rgba(0,0,0,0.05); }
    h1 { font-size: 38px; line-height: 1.3; color: #000; margin-bottom: 20px; font-weight: 800; }
    .meta { border-top: 1px solid #eee; border-bottom: 1px solid #eee; padding: 10px 0; margin-bottom: 25px; color: var(--text-gray); font-size: 14px; }
    .hero-img { width: 100%; border-radius: 8px; margin-bottom: 30px; }
    .post-img { width: 100%; border-radius: 5px; margin: 25px 0; border: 1px solid #ddd; }
    
    /* TTS Floating Button */
    .tts-player { position: fixed; bottom: 30px; right: 30px; background: var(--main-red); color: white; border: none; padding: 15px 25px; border-radius: 50px; font-weight: bold; cursor: pointer; box-shadow: 0 10px 20px rgba(218, 37, 28, 0.4); z-index: 1000; display: flex; align-items: center; gap: 10px; transition: 0.3s; }
    .tts-player:hover { transform: scale(1.05); background: #000; }

    /* News Button */
    .news-yt-btn { display: inline-block; background: #FF0000; color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px; font-weight: bold; margin: 20px 0; }

    /* Footer - Professional */
    footer { background: var(--dark-bg); color: white; padding: 60px 20px 30px; margin-top: 50px; }
    .footer-grid { max-width: 1200px; margin: 0 auto; display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 40px; }
    .footer-section h4 { border-left: 4px solid var(--main-red); padding-left: 10px; margin-bottom: 20px; }
    .footer-links a { display: block; color: #ccc; text-decoration: none; margin-bottom: 10px; font-size: 14px; }
    .footer-bottom { border-top: 1px solid #333; margin-top: 40px; padding-top: 20px; text-align: center; font-size: 12px; color: #777; }

    @media (max-width: 768px) { .container { padding: 20px; } h1 { font-size: 28px; } }
</style>
"""

# --- PAGE GENERATOR ---
article_html = f"""
<!DOCTYPE html>
<html lang="hi">
<head>
    <meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{current_topic}</title>
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;700;900&display=swap" rel="stylesheet">
    {news_css}
</head>
<body>
    <div class="trending-bar">🔥 Trending: AI Automation, 24/7 Digital Income, Passive Wealth 2026</div>
    <header>
        <div class="nav-top">
            <a href="index.html" class="logo">Digital Kamai Hub</a>
            <nav><a href="index.html" style="text-decoration:none; color:black; font-weight:bold;">Home</a></nav>
        </div>
    </header>

    <div class="container">
        <h1>{current_topic}</h1>
        <div class="meta">प्रकाशित: {today_date} | लेखक: AI Expert | 5 मिनट रीडिंग</div>
        <img src="{main_img_url}" class="hero-img" alt="Headline Image">
        <div id="read-area">{blog_content}</div>
    </div>

    <button class="tts-player" onclick="toggleTTS()" id="ttsBtn">🔊 लेख सुनें</button>

    <footer>
        <div class="footer-grid">
            <div class="footer-section">
                <h4>About Hub</h4>
                <p style="font-size:14px; color:#ccc;">हम भारत के नंबर 1 ऑटोमेशन ब्लॉग हैं जो आपको भविष्य की तकनीक से अमीर बनाना सिखाते हैं।</p>
            </div>
            <div class="footer-section">
                <h4>Quick Links</h4>
                <div class="footer-links">
                    <a href="about.html">About Us</a><a href="privacy.html">Privacy Policy</a><a href="disclaimer.html">Disclaimer</a>
                </div>
            </div>
            <div class="footer-section">
                <h4>Contact</h4>
                <div class="footer-links"><a href="#">Support: help@digitalkamai.com</a></div>
            </div>
        </div>
        <div class="footer-bottom">&copy; {current_year} Digital Kamai Hub | All Rights Reserved.</div>
    </footer>

    <script>
        let synth = window.speechSynthesis;
        let isReading = false;
        function toggleTTS() {{
            if (isReading) {{
                synth.cancel();
                document.getElementById('ttsBtn').innerHTML = '🔊 लेख सुनें';
                isReading = False;
            }} else {{
                let text = document.getElementById('read-area').innerText;
                let utter = new SpeechSynthesisUtterance(text);
                utter.lang = 'hi-IN';
                utter.rate = 0.9;
                utter.pitch = 1.1;
                synth.speak(utter);
                document.getElementById('ttsBtn').innerHTML = '⏹️ आवाज़ बंद करें';
                isReading = true;
                utter.onend = () => {{ document.getElementById('ttsBtn').innerHTML = '🔊 लेख सुनें'; isReading = false; }};
            }}
        }}
    </script>
</body>
</html>
"""

with open(post_filename, "w", encoding="utf-8") as f: f.write(article_html)

# --- HOME PAGE GENERATOR ---
cards = "".join([f"""
    <div style="background:white; margin-bottom:25px; border-radius:8px; overflow:hidden; box-shadow:0 4px 15px rgba(0,0,0,0.1); display:flex; flex-wrap:wrap;">
        <img src="{p['img']}" style="width:300px; height:200px; object-fit:cover;">
        <div style="padding:20px; flex:1; min-width:300px;">
            <h3 style="margin-bottom:15px; font-size:22px;"><a href="{p['file']}" style="color:black; text-decoration:none;">{p['title']}</a></h3>
            <p style="color:#666; font-size:14px;">🗓 {p['date']}</p>
            <a href="{p['file']}" style="display:inline-block; margin-top:15px; color:var(--main-red); font-weight:bold; text-decoration:none;">पूरा लेख पढ़ें →</a>
        </div>
    </div>
""" for p in posts_db])

with open("index.html", "w", encoding="utf-8") as f:
    f.write(f"<!DOCTYPE html><html lang='hi'><head><meta charset='UTF-8'>{news_css}<title>Digital Kamai Hub</title></head><body style='background:#f4f4f4;'><header><div class='nav-top'><a href='index.html' class='logo'>Digital Kamai Hub</a></div></header><div class='main-container' style='max-width:1100px; margin:40px auto; padding:0 20px;'>{cards}</div></body></html>")

# --- STATIC PAGES GENERATOR (About, Privacy, etc.) ---
for page in ['about', 'privacy', 'disclaimer']:
    with open(f"{page}.html", "w", encoding="utf-8") as f:
        f.write(f"<html><head>{news_css}</head><body><header><div class='nav-top'><a href='index.html' class='logo'>Digital Kamai Hub</a></div></header><div class='container'><h1>{page.capitalize()} Us</h1><p>यह पन्ना अभी अपडेट हो रहा है...</p></div></body></html>")

