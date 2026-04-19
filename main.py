import urllib.request
import urllib.parse
import json
import os
import sys
import time
import re
import html

# ==========================================
# THE AI MILLIONAIRE - PREMIUM MASTER ENGINE
# ==========================================

# 🔑 API Keys (Fetching securely from GitHub Secrets)
raw_keys = os.environ.get("GEMINI_API_KEY", "")
API_KEYS = [k.strip() for k in raw_keys.split(",") if k.strip()]

# (अगर किसी कारण से Secret काम न करे, तो यह बैकअप है - इसे कोई चुरा नहीं सकता क्योंकि GitHub इसे रनटाइम पर छिपा देता है)
if not API_KEYS:
    API_KEYS = [
        "AIzaSyBsr9sYpFc9evX4yDFBCM1WAkYhzz6F2fU",
        "AIzaSyBzy0HTMgJMa_64QI4XcCjXO2pmTlMX8Pw",
        "AIzaSyBxcY9nBb0m6WtjhtMdsYRNGd98q1kDpxo"
    ]

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

# 🚀 SMART PRE-WARM FUNCTION (पलक झपकते फोटो लोड करने की तकनीक)
def pre_warm_image(url):
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        urllib.request.urlopen(req, timeout=20)
        time.sleep(3) # स्मार्ट गैप ताकि सर्वर हमें बॉट समझकर ब्लॉक न करे
    except:
        pass

# ---------------------------------------------------------
# THE AGENTS (HIGH-PAYING FINANCE & TRADING NICHE)
# ---------------------------------------------------------
topic_prompt = f"तुम एक ट्रेंड एनालिस्ट हो। {current_year} में 'फाइनेंस', 'ट्रेडिंग', 'स्टॉक मार्केट', या 'AI से ऑनलाइन कमाई' पर एक बहुत ही हाई-पेइंग और वायरल हिंदी ब्लॉग टाइटल दो। पुराने टाइटल्स: {[p['title'] for p in posts_db[:5]]} से अलग हो। सिर्फ 'टाइटल' लिखना।"
current_topic = ask_ai(topic_prompt).replace('"', '').replace("'", "").replace("*", "").replace("टाइटल:", "").replace("Title:", "").replace("टाइटल :", "").strip()

if not current_topic: sys.exit(1)

html_prompt = f"""तुम एक प्रो ब्लॉगर हो। विषय: '{current_topic}'। 
कम से कम 1000 शब्दों का एक बहुत ही विस्तार से लिखा गया शानदार हिंदी ब्लॉग पोस्ट लिखो।
नियम:
1. पोस्ट के बीच-बीच में 3 अलग-अलग जगह बिलकुल ऐसे ही लिख दो: [PHOTO]
2. अंत में एक दमदार 'निष्कर्ष' (Conclusion) और पाठकों के लिए एक 'Call to Action (CTA)' जरूर लिखें कि उन्हें आगे क्या करना चाहिए।
3. मुख्य टाइटल (Heading) दोबारा मत लिखना, सीधा इंट्रोडक्शन से शुरू करना।
4. सिर्फ HTML कोड (h2, p, strong, ul) दें।"""
blog_content = ask_ai(html_prompt, retries=20).replace("```html", "").replace("```", "").strip()
if not blog_content: sys.exit(1)

# ---------------------------------------------------------
# 🎨 100% SAFE & INSTANT IMAGE ENGINE (PREMIUM 3D LOOK)
# ---------------------------------------------------------
safe_img_base = "high end finance trading business technology wealth"

modifiers = ["cinematic 8k", "digital art illustration", "hyper realistic photography"]
for idx, mod in enumerate(modifiers):
    if "[PHOTO]" in blog_content:
        inner_prompt = f"{safe_img_base} {mod}".replace(" ", "%20")
        inner_img_url = f"https://image.pollinations.ai/prompt/{inner_prompt}?width=800&height=400&nologo=true&seed={post_id + idx + 1}"
        
        pre_warm_image(inner_img_url) # रोबोट छुपकर तस्वीरें तैयार कर रहा है
        
        img_html = f"<div style='text-align: center;'><img src='{inner_img_url}' alt='AI generated illustration' class='article-img'></div>"
        blog_content = blog_content.replace("[PHOTO]", img_html, 1)

main_prompt = f"{safe_img_base} hyper realistic masterpiece".replace(" ", "%20")
main_img_url = f"https://image.pollinations.ai/prompt/{main_prompt}?width=1200&height=600&nologo=true&seed={post_id}"
pre_warm_image(main_img_url) 

# ---------------------------------------------------------
# 🎧 PREMIUM SUPER-CLEAN AUDIO ENGINE
# ---------------------------------------------------------
audio_filename = f"audio_{post_id}.mp3"
clean_text = re.sub(r'<[^>]+>', ' ', blog_content)
clean_text = html.unescape(clean_text)
clean_text = re.sub(r'\s+', ' ', clean_text).replace("*", "").replace("#", "").strip()

with open("temp.txt", "w", encoding="utf-8") as temp_f:
    temp_f.write(clean_text)
os.system("pip install edge-tts")
os.system(f"edge-tts -f temp.txt --voice hi-IN-SwaraNeural --write-media {audio_filename}")

post_filename = f"post_{post_id}.html"
posts_db.insert(0, {"title": current_topic, "file": post_filename, "date": today_date, "img": main_img_url})
with open("posts.json", "w", encoding="utf-8") as f: json.dump(posts_db, f, ensure_ascii=False, indent=4)

# ---------------------------------------------------------
# HTML & CSS DESIGN (THE 3D PREMIUM LOOK IS FULLY RESTORED)
# ---------------------------------------------------------
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
    .container { max-width: 850px; margin: 40px auto; background: white; padding: 40px; border-radius: 12px; box-shadow: 0 5px 20px rgba(0,0,0,0.05); }
    h1 { font-size: 38px; line-height: 1.3; margin-bottom: 15px; color: #000; }
    .meta { font-size: 14px; color: #888; border-bottom: 1px solid #eee; padding-bottom: 15px; margin-bottom: 25px; }
    /* Premium 3D Image Styling */
    .hero-img { width: 100%; border-radius: 12px; margin-bottom: 30px; box-shadow: 0 10px 30px rgba(0,0,0,0.15); border: 2px solid #f9f9f9; object-fit: cover; background-color: #fafafa; }
    .article-img { width: 100%; border-radius: 12px; margin: 35px 0; box-shadow: 0 10px 30px rgba(0,0,0,0.15); border: 2px solid #f9f9f9; object-fit: cover; background-color: #fafafa; }
    #article-body { font-size: 20px; color: var(--text-gray); }
    #article-body h2 { color: #000; margin: 35px 0 15px 0; border-left: 5px solid var(--main-red); padding-left: 15px; background: #fafafa; padding: 10px 15px; border-radius: 0 8px 8px 0; }
    .yt-btn { display: block; background: #ff0000; color: white; text-align: center; padding: 18px; border-radius: 8px; text-decoration: none; font-weight: bold; font-size: 18px; margin: 40px 0; transition: 0.3s; box-shadow: 0 5px 15px rgba(255,0,0,0.3); }
    .yt-btn:hover { background: #cc0000; transform: scale(1.02); }
    footer { background: var(--dark-bg); color: #888; padding: 60px 20px 30px; margin-top: 60px; text-align: center; }
    .footer-links a { color: #ccc; text-decoration: none; margin: 0 15px; font-size: 15px; }
</style>
"""

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
    {premium_css}
</head>
<body>
    {header_html}
    <div class="container">
        <h1>{current_topic}</h1>
        <div class="meta">📅 प्रकाशित: {today_date} | ✍️ लेखक: मोहित (The AI Millionaire)</div>
        <img src="{main_img_url}" class="hero-img" alt="Hero Image">
        
        <div id="article-body">{blog_content}</div>
        
        <div style="margin: 40px 0; padding: 25px; background: #fff; border-radius: 12px; box-shadow: 0 5px 20px rgba(0,0,0,0.08); display: flex; align-items: center; gap: 20px; border-top: 4px solid var(--main-red);">
            <img src="https://api.dicebear.com/7.x/avataaars/svg?seed=Mohit&backgroundColor=f0f2f5" alt="Mohit - The AI Millionaire" style="min-width: 80px; height: 80px; border-radius: 50%; padding: 5px; border: 2px solid var(--main-red);">
            <div>
                <h3 style="margin: 0; font-size: 22px; color: #111;">मोहित <span style="font-size: 16px; color: #888; font-weight: normal;">| The AI Millionaire</span></h3>
                <p style="margin: 8px 0 0; font-size: 15px; color: #555; line-height: 1.6;">नमस्ते! मैं मोहित हूँ। मेरा मिशन आपको AI की ताकत से वित्तीय आज़ादी दिलाना और 2026 में स्मार्ट तरीके से ऑनलाइन कमाई के सबसे एडवांस सीक्रेट्स सिखाना है। इस डिजिटल सफर में मेरे साथ जुड़ें!</p>
            </div>
        </div>
        
        <a href="https://www.youtube.com/results?search_query={urllib.parse.quote(current_topic)}" target="_blank" class="yt-btn">📺 यूट्यूब पर इस विषय का वीडियो देखें</a>
        
        <audio id="premium-audio" src="{audio_filename}"></audio>
        <button id="floating-tts-btn" onclick="toggleAudio()" style="position: fixed; bottom: 30px; right: 30px; background: #da251c; color: white; border: none; padding: 15px 25px; border-radius: 50px; font-weight: bold; font-size: 16px; cursor: pointer; box-shadow: 0 10px 25px rgba(218, 37, 28, 0.4); z-index: 1000; transition: 0.3s; display: flex; align-items: center; gap: 10px;">
            🎧 आर्टिकल सुनें
        </button>
        <script>
            function toggleAudio() {{
                var audio = document.getElementById("premium-audio");
                var btn = document.getElementById("floating-tts-btn");
                if (audio.paused) {{
                    audio.play();
                    btn.innerHTML = "⏸️ आवाज़ रोकें";
                    btn.style.background = "#111";
                }} else {{
                    audio.pause();
                    btn.innerHTML = "🎧 फिर से सुनें";
                    btn.style.background = "#da251c";
                }}
            }}
        </script>
        
    </div>
    
    {footer_html}
        
</body>
</html>"""

with open(post_filename, "w", encoding="utf-8") as f: f.write(article_page)

home_cards = "".join([f"""
    <div class="card" style="background:#fff; padding:15px; border-radius:12px; box-shadow:0 5px 15px rgba(0,0,0,0.08); transition: 0.3s;">
        <img src="{p['img']}" alt="Thumbnail" style="width:100%; border-radius:8px; object-fit: cover; min-height: 200px; background-color: #fafafa;">
        <div class="card-content" style="padding-top:15px;">
            <h3 style="margin-bottom:10px; font-size: 18px; line-height: 1.4;"><a href="{p['file']}" style="color:#000; text-decoration:none;">{p['title']}</a></h3>
            <p style="color:#888; font-size:13px; margin-bottom:15px;">🗓 {p['date']}</p>
            <a href="{p['file']}" style="color:var(--main-red); font-weight:bold; text-decoration:none; font-size: 15px;">पूरा लेख पढ़ें →</a>
        </div>
    </div>
""" for p in posts_db])

with open("index.html", "w", encoding="utf-8") as f:
        f.write(f"<!DOCTYPE html><html lang='hi'><head><meta name='google-site-verification' content='hjQKPcCjWtLzjl1g3I19cddaZ3ODDzEndKg3T91sQsI' /><script async src='https://www.googletagmanager.com/gtag/js?id=G-NSLHLYVTDM'></script><script>window.dataLayer = window.dataLayer || []; function gtag(){{dataLayer.push(arguments);}} gtag('js', new Date()); gtag('config', 'G-NSLHLYVTDM');</script><meta charset='UTF-8'><meta name='viewport' content='width=device-width, initial-scale=1.0'><title>Digital Kamai Hub</title>{premium_css}</head><body>{header_html}<div style='max-width:1100px; margin:40px auto; padding:0 20px;'><h2 style='font-size:32px; border-bottom:3px solid #da251c; padding-bottom:10px; display:inline-block; margin-bottom:30px;'>🔥 ताज़ा खबरें</h2><div class='grid' style='display:grid; grid-template-columns:repeat(auto-fit, minmax(320px, 1fr)); gap:30px;'>{home_cards}</div></div>{footer_html}</body></html>")
        
pages = {
    "about": ("About Us", "Digital Kamai Hub भारत का नंबर 1 AI और टेक्नोलॉजी ब्लॉग है। मोहित (The AI Millionaire) द्वारा स्थापित, हमारा उद्देश्य आपको डिजिटल दुनिया में सफल बनाना है।"),
    "privacy": ("Privacy Policy", "आपकी प्राइवेसी हमारे लिए महत्वपूर्ण है। हम आपकी जानकारी को सुरक्षित रखते हैं।"),
    "disclaimer": ("Disclaimer", "इस वेबसाइट पर दी गई सभी जानकारी केवल शिक्षा के लिए है। किसी भी वित्तीय निर्णय से पहले अपनी रिसर्च करें।")
}

for p_file, (p_title, p_content) in pages.items():
    with open(f"{p_file}.html", "w", encoding="utf-8") as f:
        f.write(f"<!DOCTYPE html><html lang='hi'><head><meta charset='UTF-8'><meta name='viewport' content='width=device-width, initial-scale=1.0'><title>{p_title}</title>{premium_css}</head><body>{header_html}<div class='container'><h1>{p_title}</h1><p style='font-size:18px;'>{p_content}</p></div>{footer_html}</body></html>")
