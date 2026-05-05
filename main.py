import urllib.request
import urllib.parse
import json
import os
import sys
import time
import re
import html
import requests
from datetime import datetime, timedelta

# ==========================================
# 1. NOTIFICATION & TELEGRAM ENGINE
# ==========================================
def send_push_notification(title, post_url):
    app_id = "f11333ae-cc73-489e-a1a5-6a74129c3785"
    api_key = os.environ.get("ONESIGNAL_API_KEY")
    if not api_key: return
    header = {"Content-Type": "application/json; charset=utf-8", "Authorization": f"Basic {api_key}"}
    payload = {"app_id": app_id, "included_segments": ["All"], "contents": {"en": f"Nayi Post: {title}"}, "headings": {"en": "Digital Kamai Hub: Taaza Khabar!"}, "url": post_url}
    try: requests.post("https://onesignal.com/api/v1/notifications", headers=header, json=payload)
    except: pass

def send_telegram_msg(message, target_chat_id=None):
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat_id = target_chat_id if target_chat_id else os.environ.get("TELEGRAM_CHAT_ID")
    if not token or not chat_id: return
    try:
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        requests.get(url, params={"chat_id": chat_id, "text": urllib.parse.unquote(message)}, timeout=10)
    except: pass

# ==========================================
# 2. AI & DATABASE SETUP
# ==========================================
raw_keys = os.environ.get("GEMINI_API_KEY", "")
API_KEYS = [k.strip() for k in raw_keys.split(",") if k.strip()]
if not API_KEYS:
    API_KEYS = ["AIzaSyBsr9sYpFc9evX4yDFBCM1WAkYhzz6F2fU", "AIzaSyBzy0HTMgJMa_64QI4XcCjXO2pmTlMX8Pw", "AIzaSyBxcY9nBb0m6WtjhtMdsYRNGd98q1kDpxo"]

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
    with urllib.request.urlopen(req, timeout=10) as response:
        res = json.loads(response.read().decode('utf-8'))
        for m in res.get('models', []):
            if 'generateContent' in m.get('supportedGenerationMethods', []) and 'flash' in m.get('name', '').lower():
                available_model = m['name']
                break
except: pass

def ask_ai(prompt, retries=4):
    for i in range(retries):
        current_key = API_KEYS[i % len(API_KEYS)]
        api_url = f"https://generativelanguage.googleapis.com/v1beta/{available_model}:generateContent?key={current_key}"
        try:
            data = json.dumps({"contents": [{"parts": [{"text": prompt}]}]}).encode("utf-8")
            req = urllib.request.Request(api_url, data=data, headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=30) as response:
                res = json.loads(response.read().decode("utf-8"))
                text = res['candidates'][0]['content']['parts'][0]['text'].strip()
                if len(text) > 10: return text
        except: time.sleep(5)
        
    hf_key = os.environ.get("HUGGINGFACE_API_KEY", "").strip()
    if not hf_key: return ""
    hf_url = "https://api-inference.huggingface.co/models/meta-llama/Meta-Llama-3-8B-Instruct"
    try:
        hf_res = requests.post(hf_url, headers={"Authorization": f"Bearer {hf_key}", "Content-Type": "application/json"}, json={"inputs": f"System: You are an expert AI blogger.\nUser: {prompt}", "parameters": {"max_new_tokens": 1500, "return_full_text": False}}, timeout=60)
        if hf_res.status_code == 200: return hf_res.json()[0].get('generated_text', '').strip()
    except: return ""

def pre_warm_image(url):
    try: urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'}), timeout=10)
    except: pass

# ==========================================
# 3. CONTENT GENERATION (SAFE TRY BLOCK)
# ==========================================
current_topic = ""
blog_content = ""
try:
    topic_prompt = f"Tum ek trend analyst ho. {current_year} mein 'Finance', 'Trading', 'Stock Market', ya 'AI se online kamai' par ek bahut hi high-paying aur viral Hindi blog title do. Purane titles: {[p['title'] for p in posts_db[:5]]} se alag ho. Sirf mukhya Title likhna. 'Title:', 'Title {current_year}:' ya aise koi bhi faltu shabd aage mat lagana."
    raw_topic = ask_ai(topic_prompt)
    current_topic = raw_topic.replace('"', '').replace("'", "").replace("*", "").replace("टाइटल:", "").replace("Title:", "").strip()
    if not current_topic: raise Exception("Topic Generate Nahi Hua")

    html_prompt = f"Tum ek expert lekin bahut friendly teacher ho. Tumhe niche diye gaye topic par ek blog post likhni hai. Vishay: '{current_topic}'। Kam se kam 1000 shabdon ka ek bahut hi vistar se likha gaya shandar Hindi blog post likho. Niyam: 1. Post ke beech mein 5 alag-alag jagah bilkul aise hi likh do: [PHOTO] 2. Post ke beech mein theek 2 alag-alag jagah bilkul aise hi likh do: [AFFILIATE] 3. Ek 'Real Life Case Study' aur 'Step-by-Step Guide' likhein. 4. Sirf HTML code (h2, p, strong, ul) dein. 5. Bhasha aam insani honi chahiye. TEMPLATE TO COPY FOR TOC: <div style='background: #fffafa; border-left: 5px solid #da251c; padding: 20px; border-radius: 8px; margin-bottom: 25px; box-shadow: 0 4px 10px rgba(0,0,0,0.05);'><h3 style='color: #da251c; margin-top: 0; font-size: 20px;'>📍 Is Article Mein Kya Hai:</h3><ul style='list-style-type: none; padding-left: 0; margin: 0; font-size: 18px;'><li style='margin-bottom: 10px; font-weight: bold; color: #333;'>👉 [Point 1 yahan likho]</li><li style='margin-bottom: 10px; font-weight: bold; color: #333;'>👉 [Point 2 yahan likho]</li></ul></div>"
    blog_content = ask_ai(html_prompt, retries=5).replace("```html", "").replace("```", "").strip()
    if not blog_content: raise Exception("Blog Content Generate Nahi Hua")
except Exception as e:
    send_telegram_msg(urllib.parse.quote(f"❌ ERROR: {e}"))
    sys.exit(1)

# ==========================================
# 4. POST-PROCESSING (0-SPACE INDENT = NO ERRORS)
# ==========================================
affiliate_offers = [
    {"title": "🤖 2026 mein apni kamai ko 10X karein!", "desc": "The AI Millionaire ki exclusive community se judein aur rozana naye money-making secrets payein.", "btn": "👉 Community Join Karein 👈", "link": "#"},
    {"title": "🚀 Aaj hi apni 100X kamai shuru karein!", "desc": "AI aur smart trading ki duniya mein kadam rakhne ke liye pramanit platform.", "btn": "👉 Yahan Free Account Banayein 👈", "link": "#"}
]
for offer in affiliate_offers:
    if "[AFFILIATE]" in blog_content:
        mega_cta_html = f"<div style='background: linear-gradient(135deg, #111, #da251c); color: white; padding: 35px 25px; border-radius: 12px; margin: 40px 0; text-align: center; box-shadow: 0 10px 30px rgba(218, 37, 28, 0.3);'><h3 style='color: #fff; margin-top: 0; font-size: 24px; letter-spacing: 0.5px;'>{offer['title']}</h3><p style='font-size: 16px; opacity: 0.9; margin-bottom: 25px; line-height: 1.6;'>{offer['desc']}</p><a href='{offer['link']}' target='_blank' style='display: inline-block; background: #fff; color: #da251c; font-weight: bold; padding: 15px 35px; border-radius: 50px; text-decoration: none; font-size: 18px; box-shadow: 0 5px 15px rgba(0,0,0,0.2);'>{offer['btn']}</a><p style='font-size: 11px; opacity: 0.6; margin-top: 15px; margin-bottom: 0;'>*Shartein laagu. Nivesh baazar jokhimon ke adheen hai.</p></div>"
        blog_content = blog_content.replace("[AFFILIATE]", mega_cta_html, 1)
blog_content = blog_content.replace("[AFFILIATE]", "") 

safe_img_base = "future finance trading wealth technology"
safe_fallback = "https://placehold.co/800x400/c00000/ffffff?text=AI+Finance+Update"
modifiers = ["cinematic", "cyberpunk", "hyperrealistic", "neon", "futuristic", "8k"] # Extra modifiers added to fix [PHOTO] bug

for idx, mod in enumerate(modifiers):
    if "[PHOTO]" in blog_content:
        inner_prompt = urllib.parse.quote(f"{safe_img_base} {mod}")
        inner_img_url = f"https://image.pollinations.ai/prompt/{inner_prompt}?width=800&height=400&nologo=true&seed={post_id + idx + 1}"
        pre_warm_image(inner_img_url)
        blog_content = blog_content.replace("[PHOTO]", f"<div style='text-align: center;'><img src='{inner_img_url}' onerror=\"this.onerror=null; this.src='{safe_fallback}';\" class='article-img' style='width: 100%; border-radius: 12px; margin: 35px 0; box-shadow: 0 10px 30px rgba(0,0,0,0.15); object-fit: cover;'></div>", 1)

# JAD SE KHATAM [PHOTO] BUG: Agar koi [PHOTO] bach gaya ho, toh use mita do
blog_content = blog_content.replace("[PHOTO]", "")

main_prompt = urllib.parse.quote(f"{safe_img_base} masterpiece")
main_img_url = f"https://image.pollinations.ai/prompt/{main_prompt}?width=1200&height=600&nologo=true&seed={post_id}"
pre_warm_image(main_img_url)

audio_filename = f"audio_{post_id}.mp3"
clean_text = re.sub(r'<[^>]+>', ' ', blog_content)
clean_text = html.unescape(clean_text)
clean_text = re.sub(r'\s+', ' ', clean_text).replace("*", "").replace("#", "").strip()
with open("temp.txt", "w", encoding="utf-8") as temp_f: temp_f.write(clean_text)
os.system("pip install edge-tts > /dev/null 2>&1")
os.system(f"edge-tts -f temp.txt --voice hi-IN-SwaraNeural --write-media {audio_filename}")

post_filename = f"post_{post_id}.html"

# Smart Database Update
posts_db.insert(0, {"title": current_topic, "file": post_filename, "date": today_date, "img": main_img_url})
with open("posts.json", "w", encoding="utf-8") as f: json.dump(posts_db, f, ensure_ascii=False, indent=4)

# RELATED ARTICLES (PREMIUM UI WITH 🔗 ICON)
related_html = ""
if len(posts_db) > 0:
    related_html = """<div style="margin-top: 30px; background: #fffafa; padding: 25px; border-radius: 12px; border: 1px solid #eee; border-left: 5px solid #ffc107;">
    <h3 style="margin-top:0; margin-bottom: 15px; color: #111; font-size: 18px;">💡 Ye bhi padhein (Related Articles):</h3>
    <ul style="list-style: none; padding: 0; margin: 0; line-height: 1.8;">"""
    for p in posts_db[:4]:
        related_html += f"<li style='margin-bottom: 10px;'>🔗 <a href='{p['file']}' style='color: #0066cc; text-decoration: none; font-weight: bold; font-size: 15px;'>{p['title']}</a></li>"
    related_html += "</ul></div>"

# AUTHOR BIO (PREMIUM AVATAR BOX)
author_html = """
<div style="display: flex; align-items: center; background: #fff; border: 1px solid #eee; border-radius: 12px; padding: 20px; box-shadow: 0 4px 15px rgba(0,0,0,0.05); margin-top: 40px;">
    <img src="https://api.dicebear.com/7.x/avataaars/svg?seed=Mohit&backgroundColor=f0f2f5" style="width: 70px; height: 70px; border-radius: 50%; margin-right: 20px;">
    <div style="flex: 1;">
        <h3 style="margin: 0 0 5px 0; font-size: 18px; color: #111;">Mohit <span style="color: #888; font-weight: normal; font-size: 14px;">| The AI Millionaire</span></h3>
        <p style="margin: 0; font-size: 14px; color: #555; line-height: 1.5;">Namaste! Main Mohit hoon. Mera mission aapko AI ki taqat se vittiya azaadi dilana aur 2026 mein smart tareeke se online kamai ke sabse advance secrets sikhana hai.</p>
    </div>
</div>
"""

# ==========================================
# 5. PREMIUM UI & VERTICAL MENU ENGINE
# ==========================================
premium_css = """
<style>
    :root { --main-red: #da251c; --dark-bg: #111; --text-gray: #444; }
    * { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Segoe UI', Tahoma, sans-serif; }
    body { background: #f0f2f5; color: #111; line-height: 1.7; overflow-x: hidden; }
    
    header { background: white; border-bottom: 2px solid #eee; box-shadow: 0 4px 10px rgba(0,0,0,0.05); position: sticky; top: 0; z-index: 1000; }
    .nav-container { max-width: 1200px; margin: 0 auto; padding: 15px 20px; display: flex; justify-content: space-between; align-items: center; position: relative; }
    .logo { font-size: 26px; font-weight: 900; color: var(--main-red); text-decoration: none; text-transform: uppercase; }
    
    /* 🔴 THE VERTICAL MENU MAGIC (Mobile Responsive) 🔴 */
    .nav-links { display: flex; align-items: center; }
    .nav-links a { margin-left: 20px; text-decoration: none; color: #111; font-weight: bold; font-size: 15px; transition: 0.3s; }
    .nav-links a:hover { color: var(--main-red); }
    .menu-btn { display: none; font-size: 30px; cursor: pointer; color: var(--main-red); font-weight: bold; user-select: none; }
    
    .container { max-width: 900px; margin: 40px auto; padding: 0 20px; }
    .article-box { background: white; padding: 40px; border-radius: 12px; box-shadow: 0 5px 20px rgba(0,0,0,0.05); }
    #article-body { font-size: 18px; color: #333; line-height: 1.8; }
    #article-body p { margin-bottom: 20px; }
    #article-body h2 { color: #000; margin: 35px 0 15px 0; border-left: 5px solid var(--main-red); padding-left: 15px; background: #fafafa; padding: 10px 15px; border-radius: 0 8px 8px 0; font-size: 24px; }
    
    /* 🔥 PREMIUM TIMELINE (DANDI UI) FOR DESKTOP & MOBILE 🔥 */
    .timeline { position: relative; max-width: 900px; margin: 40px auto; }
    .timeline::after { content: ''; position: absolute; width: 4px; background: var(--main-red); top: 0; bottom: 0; left: 50%; margin-left: -2px; border-radius: 5px; }
    .timeline-card { padding: 10px 40px; position: relative; background: inherit; width: 50%; box-sizing: border-box; }
    .timeline-card.left { left: 0; }
    .timeline-card.right { left: 50%; }
    .timeline-card::after { content: ''; position: absolute; width: 22px; height: 22px; right: -11px; background-color: white; border: 4px solid var(--main-red); top: 20px; border-radius: 50%; z-index: 1; }
    .timeline-card.right::after { left: -11px; }
    .timeline-content { padding: 20px; background: white; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.08); transition: transform 0.3s; }
    .timeline-content:hover { transform: translateY(-5px); }
    .timeline-content img { width: 100%; border-radius: 8px; height: 180px; object-fit: cover; margin-bottom: 15px; }
    
    footer { background: var(--dark-bg); color: #888; padding: 60px 20px 80px; margin-top: 60px; text-align: center; }
    .footer-links a { color: #ccc; text-decoration: none; margin: 0 10px; font-size: 14px; }
    
    /* 🔴 MOBILE RESPONSIVE (Laptop Jaise Premium) 🔴 */
    @media (max-width: 768px) {
        .article-box { padding: 20px; }
        h1 { font-size: 26px !important; line-height: 1.4; }
        #article-body { font-size: 16px; }
        
        /* Menu Mobile UI (Vertical) */
        .menu-btn { display: block; }
        .nav-links { display: none; flex-direction: column; position: absolute; top: 100%; left: 0; width: 100%; background: #ffffff; box-shadow: 0 10px 30px rgba(0,0,0,0.15); border-top: 2px solid var(--main-red); z-index: 1001; padding: 10px 0; }
        .nav-links.active { display: flex !important; }
        .nav-links a { margin: 0; padding: 15px 25px; border-bottom: 1px solid #f0f0f0; width: 100%; text-align: left; font-size: 18px; }
        .nav-links a:hover { background: #fffafa; padding-left: 30px; }
        
        /* Mobile Timeline Fix */
        .timeline::after { left: 20px; }
        .timeline-card { width: 100%; padding-left: 50px; padding-right: 0; }
        .timeline-card.right { left: 0; }
        .timeline-card::after, .timeline-card.right::after { left: 10px; right: auto; width: 16px; height: 16px; top: 25px; }
        .timeline-content { padding: 15px; }
        .timeline-content img { height: 150px; }
    }
    
    .ticker-wrap { width: 100%; overflow: hidden; background-color: #f1f1f1; border-bottom: 2px solid #C00000; box-sizing: border-box; }
    .ticker-content { display: flex; white-space: nowrap; animation: tickerAnimation 15s linear infinite; color: #333; font-family: sans-serif; font-size: 14px; font-weight: bold; padding: 10px 0; }
    .ticker-content span { color: #C00000; }
    @keyframes tickerAnimation { 0% { transform: translateX(100%); } 100% { transform: translateX(-100%); } }
</style>
<script src="https://cdn.onesignal.com/sdks/web/v16/OneSignalSDK.page.js" defer></script>
<script>window.OneSignalDeferred = window.OneSignalDeferred || []; OneSignalDeferred.push(async function(OneSignal) { await OneSignal.init({ appId: "f11333ae-cc73-489e-a1a5-6a74129c3785" }); });</script>
"""

schema_markup = f"""<script type="application/ld+json">{{ "@context": "https://schema.org", "@type": "Article", "headline": "{current_topic}", "image": "{main_img_url}", "author": {{ "@type": "Person", "name": "Mohit (The AI Millionaire)" }}, "publisher": {{ "@type": "Organization", "name": "Digital Kamai Hub" }}, "datePublished": "{today_date}" }}</script>"""

header_html = """
<div class="ticker-wrap"><div class="ticker-content"><span>TRENDING:</span> &nbsp; 2026 Best Tech, AI Income, Future Jobs, Digital Kamai Hub Ke Naye Hacks, Share Market Ka Sach!</div></div>
<header>
    <div class="nav-container">
        <a href="index.html" class="logo">Digital Kamai Hub</a>
        <div class="menu-btn" onclick="document.getElementById('mobile-menu').classList.toggle('active')">&#9776;</div>
        <div class="nav-links" id="mobile-menu">
            <a href="index.html">Home</a>
            <a href="category_ai.html">AI Hacks</a>
            <a href="category_trading.html">Trading</a>
            <a href="category_finance.html">Finance</a>
            <a href="about.html">About Us</a>
            <a href="contact.html">Contact</a>
        </div>
    </div>
</header>
"""

footer_html = f"""
<footer style="margin-top: 40px; background: #111; padding: 40px 20px; text-align: center;">
    <div style="margin-bottom: 25px;">
        <p style="color: #ccc; font-size: 14px; margin-bottom: 15px; font-weight: bold; letter-spacing: 1px;">JOIN THE AI MILLIONAIRE COMMUNITY:</p>
        <div style="display: flex; justify-content: center; gap: 20px; flex-wrap: wrap;">
            <a href="https://www.youtube.com/@TheAIMillionaire-h5g" target="_blank" style="color: #FF0000; text-decoration: none; font-weight: bold; background: white; padding: 8px 15px; border-radius: 5px;">YouTube</a>
            <a href="https://t.me/digitalkamaihub_2026" target="_blank" style="color: #0088cc; text-decoration: none; font-weight: bold; background: white; padding: 8px 15px; border-radius: 5px;">Telegram</a>
            <a href="https://www.instagram.com/aimillionaire_official" target="_blank" style="color: #E1306C; text-decoration: none; font-weight: bold; background: white; padding: 8px 15px; border-radius: 5px;">Instagram</a>
            <a href="https://www.facebook.com/share/1HNaL98HmW/" target="_blank" style="color: #1877F2; text-decoration: none; font-weight: bold; background: white; padding: 8px 15px; border-radius: 5px;">Facebook</a>
        </div>
    </div>
    <div class="footer-links" style="margin-bottom: 20px;">
        <a href="about.html">About Us</a> | <a href="privacy.html">Privacy Policy</a> | <a href="terms.html">Terms & Conditions</a> | <a href="disclaimer.html">Disclaimer</a> | <a href="contact.html">Contact Us</a>
    </div>
    <p style="margin-top:20px; font-size:13px; color: #888;">&copy; {current_year} Digital Kamai Hub. All Rights Reserved.</p>
</footer>
"""

# ==========================================
# 6. HTML PAGE GENERATORS
# ==========================================

article_page = f"""<!DOCTYPE html>
<html lang="hi">
<head>
    <meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{current_topic} - Digital Kamai Hub</title>
    {premium_css}
    {schema_markup}
</head>
<body>
    <div style="position: fixed; top: 0; left: 0; width: 100%; height: 5px; background-color: transparent; z-index: 9999;">
        <div id="smart-progress" style="height: 5px; background-color: #da251c; width: 0%; border-top-right-radius: 3px; border-bottom-right-radius: 3px;"></div>
    </div>
    <script>
        window.addEventListener('scroll', function() {{
            var winScroll = document.body.scrollTop || document.documentElement.scrollTop;
            var height = document.documentElement.scrollHeight - document.documentElement.clientHeight;
            var scrolled = (winScroll / height) * 100;
            document.getElementById("smart-progress").style.width = scrolled + "%";
        }});
        function toggleAudio() {{
            var audio = document.getElementById("premium-audio");
            var btn = document.getElementById("floating-tts-btn");
            if (audio.paused) {{ audio.play(); btn.innerHTML = "⏸️ Pause"; }} 
            else {{ audio.pause(); btn.innerHTML = "🔊 Article Sunein"; }}
        }}
    </script>
    {header_html}
    <div class="container">
        <div class="article-box">
            <h1 style="color: #111; margin-bottom: 15px;">{current_topic}</h1>
            <div style="color: #666; font-size: 14px; margin-bottom: 20px; border-bottom: 1px solid #eee; padding-bottom: 10px; font-weight: bold;">
                📅 Prakashit: {today_date} | ✍️ Lekhak: Mohit (The AI Millionaire)
            </div>
            <img src="{main_img_url}" onerror="this.onerror=null; this.src='https://placehold.co/1200x600/da251c/ffffff?text=Digital+Kamai+Hub';" style="width: 100%; border-radius: 10px; margin-bottom: 25px; box-shadow: 0 5px 15px rgba(0,0,0,0.1); object-fit: cover;">
            
            <div style="background: #fff3f3; padding: 15px; border-radius: 8px; margin-bottom: 25px; color: #da251c; font-weight: bold; border-left: 4px solid #da251c;">
                🎧 Samay kam hai? Niche diye gaye laal button ko dabakar poora article audio mein sunein!
            </div>

            <div id="article-body">
                {blog_content}
            </div>
            
            {author_html}
            {related_html}
            
            <audio id="premium-audio" src="{audio_filename}"></audio>
            <button id="floating-tts-btn" onclick="toggleAudio()" style="position: fixed; bottom: 80px; right: 20px; background: #da251c; color: white; border: none; padding: 15px 25px; font-weight: bold; border-radius: 50px; cursor: pointer; box-shadow: 0 4px 15px rgba(218,37,28,0.4); z-index: 1000; font-size: 16px; display: flex; align-items: center; gap: 8px;">
                🔊 Article Sunein
            </button>

            <div style="margin-top: 40px; display: flex; gap: 15px;">
                <button onclick="window.open('https://api.whatsapp.com/send?text=Digital Kamai Hub ka naya secret: ' + window.location.href, '_blank')" style="flex: 1; background: #25D366; color: white; border: none; padding: 15px; border-radius: 8px; font-weight: bold; cursor: pointer; font-size: 16px; box-shadow: 0 4px 10px rgba(37,211,102,0.2);">💬 WhatsApp par bhejein</button>
                <button onclick="window.open('https://t.me/share/url?url=' + window.location.href + '&text=Digital Kamai Hub ka naya secret!', '_blank')" style="flex: 1; background: #0088cc; color: white; border: none; padding: 15px; border-radius: 8px; font-weight: bold; cursor: pointer; font-size: 16px; box-shadow: 0 4px 10px rgba(0,136,204,0.2);">✈️ Telegram par bhejein</button>
            </div>
        </div>
    </div>
    {footer_html}
</body>
</html>"""
with open(post_filename, "w", encoding="utf-8") as f: f.write(article_page)

# 🧠 SMART CATEGORIZATION ENGINE
def get_category(title):
    t = title.lower()
    if any(w in t for w in ['ai', 'chatgpt', 'bot', 'artificial intelligence', 'tech', 'automation']): return 'ai'
    if any(w in t for w in ['trade', 'trading', 'share', 'stock', 'market', 'crypto', 'nifty', 'option']): return 'trading'
    if any(w in t for w in ['finance', 'paisa', 'kamai', 'wealth', 'amir', 'money', 'income', 'bank']): return 'finance'
    return 'trending'

categorized_posts = {'ai': [], 'trading': [], 'finance': [], 'trending': []}
for p in posts_db:
    cat = get_category(p['title'])
    categorized_posts[cat].append(p)
    categorized_posts['trending'].append(p)

# 🎨 TIMELINE HTML GENERATOR (THE DANDI DESIGN)
def generate_timeline(post_list):
    if not post_list: return "<p style='text-align: center; color: #888; margin-top: 30px;'>Abhi yahan koi article nahi hai. Naye updates ka intezaar karein!</p>"
    html_str = '<div class="timeline">'
    for i, p in enumerate(post_list):
        side = "left" if i % 2 == 0 else "right"
        html_str += f"""
        <div class="timeline-card {side}">
            <div class="timeline-content">
                <img src="{p['img']}" onerror="this.onerror=null; this.src='https://placehold.co/800x400/111/fff?text=Digital+Kamai+Hub';">
                <p style="color: #888; font-size: 13px; font-weight: bold; margin-bottom: 5px;">📅 {p['date']}</p>
                <h3 style="margin-bottom: 10px; font-size: 18px; line-height: 1.4;"><a href="{p['file']}" style="color: #111; text-decoration: none;">{p['title']}</a></h3>
                <a href="{p['file']}" style="color: #da251c; font-weight: bold; text-decoration: none; font-size: 14px;">Read More →</a>
            </div>
        </div>
        """
    html_str += '</div>'
    return html_str

def create_page(filename, title, post_list):
    content = f"<!DOCTYPE html><html lang='hi'><head><meta charset='UTF-8'><meta name='viewport' content='width=device-width, initial-scale=1.0'><title>{title} - Digital Kamai Hub</title>{premium_css}</head><body>{header_html}<div class='container'><h1 style='text-align: center; margin-bottom: 10px; color: #da251c; font-size: 32px; font-weight: 900;'>🔥 {title}</h1>{generate_timeline(post_list)}</div>{footer_html}</body></html>"
    with open(filename, "w", encoding="utf-8") as f: f.write(content)

create_page("index.html", "Latest Trending Articles", posts_db[:10])
create_page("category_ai.html", "AI & Tech Hacks", categorized_posts['ai'])
create_page("category_trading.html", "Share Market & Trading", categorized_posts['trading'])
create_page("category_finance.html", "Finance & Wealth", categorized_posts['finance'])
create_page("all-posts.html", "Sabhi Articles (Archive)", posts_db)

# 📝 3. ALL LEGAL PAGES FOR ADSENSE + WORKING CONTACT FORM
pages = {
    "about": ("About Us", "<h2 style='color: var(--main-red); margin-bottom: 15px; font-size: 28px;'>Hamari Kahani (Our Story)</h2><p style='font-size: 18px; margin-bottom: 25px; color: #333;'>Namaste! <strong>Digital Kamai Hub</strong> mein aapka swagat hai. Yeh sirf ek blog nahi, balki ek digital revolution hai.</p><h2 style='color: var(--main-red); margin-bottom: 15px; font-size: 24px;'>🎯 Mission & Vision</h2><p style='font-size: 18px; margin-bottom: 25px; color: #333;'>Hamara mission bilkul saaf hai: <strong>\"Bacchon ka khel nahi, Smart Work!\"</strong></p><h2 style='color: var(--main-red); margin-bottom: 15px; font-size: 24px;'>👨‍💻 Meet The Founder: Mohit (The AI Millionaire)</h2><div style='background: #fafafa; padding: 25px; border-left: 5px solid var(--main-red); border-radius: 8px; margin-bottom: 30px;'><p style='font-size: 17px; margin-bottom: 15px; color: #222;'>Mohit ek <strong>Full-Stack Web Developer aur Visionary Entrepreneur</strong> hain. Any manual task is a bug.</p></div>"),
    "privacy": ("Privacy Policy", "<h2 style='color: var(--main-red); margin-bottom: 15px; font-size: 28px;'>Privacy Policy</h2><p style='font-size: 18px; margin-bottom: 15px; color: #333;'>Aapki privacy hamare liye sabse zyada zaroori hai. Digital Kamai Hub par hum aapka data kaise use karte hain:</p><ul><li style='margin-bottom: 10px;'><strong>Cookies:</strong> Hum website ka experience behtar banane aur Google AdSense ke ads dikhane ke liye cookies ka istemal karte hain.</li><li style='margin-bottom: 10px;'><strong>Data Security:</strong> Hum aapki email ya personal jankari kisi third-party ko nahi bechte.</li></ul>"),
    "terms": ("Terms & Conditions", "<h2 style='color: var(--main-red); margin-bottom: 15px; font-size: 28px;'>Terms and Conditions</h2><p style='font-size: 18px; margin-bottom: 15px; color: #333;'>Is website ka istemal karke aap hamari in sharton ko mante hain:</p><ul><li style='margin-bottom: 10px;'><strong>Samagri (Content):</strong> Is website ka content sirf shikhsha ke liye hai. Ise copy karke kahin aur bechna mana hai.</li><li style='margin-bottom: 10px;'><strong>Zimmewari:</strong> Hum kisi bhi aarthik nuksan ke liye zimmewar nahi hain.</li></ul>"),
    "disclaimer": ("Disclaimer", "<h2 style='color: var(--main-red); margin-bottom: 15px; font-size: 28px;'>Disclaimer (Chetawani)</h2><p style='font-size: 18px; margin-bottom: 15px; color: #333;'><strong>Digital Kamai Hub</strong> par di gayi sabhi jankari (Finance, Share Market, AI Tools) keval shikhsha ke liye hai.</p><ul><li style='margin-bottom: 10px;'><strong>Financial Advice Nahi:</strong> Hum SEBI registered financial advisor nahi hain.</li><li style='margin-bottom: 10px;'><strong>Risk (Jokhim):</strong> Trading aur investment mein jokhim hota hai.</li></ul>"),
    "contact": ("Contact Us", """<div style="text-align: center;"><h1 style="color: #da251c; font-size: 32px; font-weight: bold; margin-bottom: 10px;">Contact Us</h1><p style="margin-bottom: 30px; font-size: 18px; color: #555;">Humse sampark karein! Apne sawal ya business inquiry form ke madhyam se bhejein.</p><div id="form-container" style="max-width: 550px; margin: 0 auto; text-align: left; background: #fff; padding: 30px; border-radius: 12px; box-shadow: 0 5px 15px rgba(0,0,0,0.1); border-top: 5px solid #da251c;"><form id="my-contact-form" action="https://formsubmit.co/ajax/rameshchandra89056@gmail.com" method="POST"><input type="text" name="_honey" style="display:none"><input type="hidden" name="_captcha" value="false"><input type="text" name="name" placeholder="Aapka Naam" required style="width: 100%; padding: 15px; margin-bottom: 15px; border: 1px solid #ccc; border-radius: 8px; font-size: 16px;"><input type="email" name="email" placeholder="Aapka Email" required style="width: 100%; padding: 15px; margin-bottom: 15px; border: 1px solid #ccc; border-radius: 8px; font-size: 16px;"><textarea name="message" rows="5" placeholder="Apna Sandesh (Message) likhein..." required style="width: 100%; padding: 15px; margin-bottom: 20px; border: 1px solid #ccc; border-radius: 8px; font-size: 16px;"></textarea><button type="submit" id="submit-btn" style="width: 100%; background: #da251c; color: white; padding: 15px; font-weight: bold; font-size: 18px; border: none; border-radius: 8px; cursor: pointer;">Bhejein (Send Message)</button></form><div id="success-message" style="display:none; text-align: center; padding: 20px; background: #e8f5e9; border: 2px solid #4caf50; border-radius: 8px; margin-top: 10px;"><h3 style="color: #4caf50; margin-top:0; margin-bottom: 10px;">✅ Message Bhej Diya Gaya!</h3><p style="color: #333; font-size: 16px; margin: 0;">Dhanyawad! Hum 24-48 ghante ke andar aapse sampark karenge.</p></div></div></div><script>const form = document.getElementById('my-contact-form'); form.addEventListener('submit', function(e) { e.preventDefault(); const btn = document.getElementById('submit-btn'); btn.innerText = 'Bheja ja raha hai...'; btn.disabled = true; fetch(form.action, { method: 'POST', body: new FormData(form), headers: { 'Accept': 'application/json' } }).then(response => response.json()).then(data => { if(data.success === 'true' || data.success === true) { form.style.display = 'none'; document.getElementById('success-message').style.display = 'block'; } else { alert('Error: Kripya dhyan dein ki aapne apna Gmail activate kiya hai ya nahi!'); btn.innerText = 'Bhejein (Send Message)'; btn.disabled = false; } }).catch(error => { alert('Network Error! Kripya internet check karein.'); btn.innerText = 'Bhejein (Send Message)'; btn.disabled = false; }); });</script>""")
}

for p_file, (p_title, p_content) in pages.items():
    legal_html = f"<!DOCTYPE html><html lang='hi'><head><meta charset='UTF-8'><meta name='viewport' content='width=device-width, initial-scale=1.0'><title>{p_title} - Digital Kamai Hub</title>{premium_css}</head><body>{header_html}<div class='container'><div class='article-box'>{p_content}</div></div>{footer_html}</body></html>"
    with open(f"{p_file}.html", "w", encoding="utf-8") as f: f.write(legal_html)

# ==========================================
# 8. SITEMAP GENERATOR (ZERO-TOUCH) & ALERTS
# ==========================================
def generate_auto_sitemap():
    try:
        base_url = "https://rameshchandra89056-bloger.github.io/AI-Autoblogger-Engine"
        sitemap_content = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        for file in [f for f in os.listdir() if f.endswith('.html')]:
            sitemap_content += f'  <url>\n    <loc>{base_url}/{file}</loc>\n    <lastmod>{datetime.now().strftime("%Y-%m-%d")}</lastmod>\n    <changefreq>daily</changefreq>\n  </url>\n'
        with open('sitemap.xml', 'w', encoding='utf-8') as f: f.write(sitemap_content + '</urlset>')
    except: pass

generate_auto_sitemap()

blog_url = f"https://rameshchandra89056-bloger.github.io/AI-Autoblogger-Engine/{post_filename}"
send_telegram_msg(urllib.parse.quote(f"✅ SUCCESS: Naya blog post publish ho gaya!\n⏰ Samay: {datetime.now().strftime('%I:%M %p')}\n📝 Kul Post: {len(posts_db)}\n🌐 Link: {blog_url}"))
if os.environ.get("TELEGRAM_PUBLIC_CHANNEL"):
    send_telegram_msg(urllib.parse.quote(f"🚀 Nayi post live ho gayi hai!\n\n🔥 Topic: {current_topic}\n\n👉 Padhein: {blog_url}"), target_chat_id=os.environ.get("TELEGRAM_PUBLIC_CHANNEL"))
send_push_notification(current_topic, blog_url)
print("✅ Website 100% safalta ke sath ban gayi hai!")
