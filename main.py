import urllib.request
import urllib.parse
import json
import os
import sys
import time
import re
import html
import requests
import random
from datetime import datetime, timedelta

def clean_ad_garbage(text):
    if "🌸 Ad" in text: text = text.split("🌸 Ad")[0]
    if "--- Support" in text: text = text.split("--- Support")[0]
    if "pollinations.ai" in text: text = text.split("pollinations.ai")[0]
    # Anti-Markdown shield (Safe line breaks for mobile)
    text = text.replace("**", "")
    text = text.replace("```html", "")
    text = text.replace("```", "")
    return text.strip()

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
    try: requests.get(f"https://api.telegram.org/bot{token}/sendMessage", params={"chat_id": chat_id, "text": urllib.parse.unquote(message)}, timeout=10)
    except: pass

# --- SECURE API ---
raw_keys = os.environ.get("GEMINI_API_KEY", "")
API_KEYS = [k.strip() for k in raw_keys.split(",") if k.strip()]
if not API_KEYS:
    send_telegram_msg("🔴 CRITICAL ERROR: API Keys missing in GitHub Secrets.")
    sys.exit(1)

current_year = time.strftime("%Y")
today_date = time.strftime("%d %B %Y")
post_id = int(time.time())

posts_db = []
if os.path.exists("posts.json"):
    with open("posts.json", "r", encoding="utf-8") as f:
        try: posts_db = [p for p in json.load(f) if "img" in p]
        except: pass

todays_category = ["AI", "Trading", "Finance"][len(posts_db) % 3]

def ask_ai(prompt, retries=3):
    for i in range(retries):
        current_key = API_KEYS[i % len(API_KEYS)]
        api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={current_key}"
        try:
            payload_data = {"contents": [{"parts": [{"text": prompt}]}], "safetySettings": [{"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"}, {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"}, {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"}, {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"}]}
            req = urllib.request.Request(api_url, data=json.dumps(payload_data).encode("utf-8"), headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=30) as response:
                text = json.loads(response.read().decode("utf-8"))['candidates'][0]['content']['parts'][0]['text'].strip()
                if len(text) > 10: return clean_ad_garbage(text)
        except Exception: time.sleep(5)
    
    try:
        poll_url = "https://text.pollinations.ai/"
        res_poll = requests.post(poll_url, json={"messages": [{"role": "system", "content": "Tum ek expert Hindi blogger ho. Sirf HTML output do. Markdown bilkul nahi."}, {"role": "user", "content": prompt}], "model": "openai"}, timeout=40)
        if res_poll.status_code == 200:
            text_poll = res_poll.text.strip()
            if len(text_poll) > 10: return clean_ad_garbage(text_poll)
    except Exception: pass
    return ""

def pre_warm_image(url):
    try: urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'}), timeout=10)
    except: pass

current_topic = ""
blog_content = ""

try:
    start_time = time.time()
    raw_topic = ask_ai(f"Tum ek trend analyst ho. Aaj ki category '{todays_category}' hai. Mujhe {current_year} ke liye '{todays_category}' niche par ek bohot hi viral Hindi blog title do. Purane titles se bilkul alag ho. Sirf Title likhna. No markdown.")
    if not raw_topic: current_topic = f"2026 Mein {todays_category} Se Paise Kaise Kamaye"
    else: current_topic = clean_ad_garbage(raw_topic.replace('"', '').replace("'", "").replace("*", "").replace("टाइटल:", "").replace("Title:", "")).strip()

    print("⏳ Chunk 1 generating...")
    intro_prompt = f"Topic: '{current_topic}'. Ek lamba Introduction (250 words) likho. Niyam 1: Bhasha ekdum 'Desi' aur simple ho. Niyam 2: Markdown (**) bilkul use mat karna. Sirf valid HTML tags (<p>, <strong>) use karna. Uske baad ek Clickable TOC likho: <div style='background: #fffafa; border-left: 5px solid #da251c; padding: 20px; border-radius: 8px; margin-bottom: 25px;'><h3 style='color: #da251c; margin-top: 0;'>📍 Is Article Mein Kya Hai:</h3><ul style='list-style:none; padding:0;'><li>👉 <a href='#basic' style='color:#da251c; text-decoration:none; font-weight:bold;'>1. Basic Samajh (0 to 30%)</a></li> <li>👉 <a href='#deep' style='color:#da251c; text-decoration:none; font-weight:bold;'>2. Tools aur Deep Detail (30 to 70%)</a></li> <li>👉 <a href='#pro' style='color:#da251c; text-decoration:none; font-weight:bold;'>3. Pro Execution Hacks (70 to 100%)</a></li></ul></div>."
    chunk_1 = ask_ai(intro_prompt)
    if not chunk_1: chunk_1 = f"<h2>{current_topic} ki Shuruaat</h2><p>Dosto, aaj ke waqt mein tech aur finance ko samajhna bohot zaroori hai. Chaliye is article mein isko detail mein samajhte hain.</p>"
    
    time.sleep(8) 
    
    print("⏳ Chunk 2 generating...")
    body_prompt = f"Topic: '{current_topic}'. Ab main body likho. 3 sub-headings (<h2>) likho. Niyam 1: Pehle <h2> mein id='basic', dusre mein id='deep', teesre mein id='pro' lagao. Niyam 2: Markdown use kiya toh code crash ho jayega, isliye ONLY HTML (<p>, <strong>, <br>, <ul>, <li>) use karna. Niyam 3: Har <h2> wale section ke baad exactly 1 baar [PHOTO] tag likho. Sirf HTML code do."
    chunk_2 = ask_ai(body_prompt)
    if not chunk_2: chunk_2 = "<h2 id='basic'>Basic Samajh</h2><p>Kisi bhi nayi cheez mein safalta paane ke liye uski neev mazboot honi chahiye.</p>[PHOTO]<h2 id='deep'>Deep Detail</h2><p>Market ya technology ke andar bohot saare data hote hain.</p>[PHOTO]<h2 id='pro'>Pro Hacks</h2><p>Ek pro smart work karta hai. Automation se aap apne kaam ko 10X fast kar sakte hain.</p>[PHOTO]"
    
    time.sleep(8) 
    
    print("⏳ Chunk 3 generating...")
    conclusion_prompt = f"Topic: '{current_topic}'. Ek lamba Conclusion aur 3 FAQs likho. Sirf aur sirf HTML (<p>, <strong>) format mein. Markdown (**) mana hai. Beech mein exactly 2 baar [AFFILIATE] tag likho."
    chunk_3 = ask_ai(conclusion_prompt)
    if not chunk_3: chunk_3 = "<h2>Nishkarsh (Conclusion)</h2><p>Umeed hai yeh jankari aapke liye faydemand hogi!</p>[AFFILIATE]<h2>FAQ</h2><p><strong>Q1: Kya yeh sahi waqt hai?</strong><br>A: Haan, bilkul.</p>[AFFILIATE]"

    raw_content = chunk_1 + "\n" + chunk_2 + "\n" + chunk_3
    blog_content = raw_content.replace("```html", "").replace("```", "").replace("**", "").strip()
    
    end_time = time.time()
    exec_time = round((end_time - start_time) / 60, 2)
    send_telegram_msg(urllib.parse.quote(f"🟢 SYSTEM RUN SUCCESS\n\n🎯 Category: {todays_category}\n📝 Topic: {current_topic}\n⏱️ Time: {exec_time} Mins\n✅ Status: Pagination & Syntax Error Fixed"))

except Exception as e:
    send_telegram_msg(urllib.parse.quote(f"🔴 SYSTEM RUN FAILED\n\n⚠️ Error: {str(e)[:150]}"))
    sys.exit(1)

# --- BACKEND LOGIC ---
affiliate_offers = [
    {"title": "🚀 Aaj hi apni 100X kamai shuru karein!", "desc": "AI aur smart trading ki duniya mein kadam rakhne ke liye sabse best platform.", "btn": "👉 Yahan Free Account Banayein 👈", "link": "https://upstox.com/"}, 
    {"title": "🤖 2026 mein apni kamai ko 10X karein!", "desc": "The AI Millionaire ki exclusive premium toolkit use karein.", "btn": "👉 Tools Check Karein 👈", "link": "https://hostinger.in/"}
]

for offer in affiliate_offers:
    if "[AFFILIATE]" in blog_content:
        blog_content = blog_content.replace("[AFFILIATE]", f"<div style='background: linear-gradient(135deg, #111, #da251c); color: white; padding: 35px 25px; border-radius: 12px; margin: 40px 0; text-align: center; box-shadow: 0 10px 30px rgba(218, 37, 28, 0.3);'><h3 style='color: #fff; margin-top: 0; font-size: 24px;'>{offer['title']}</h3><p style='font-size: 16px; margin-bottom: 25px;'>{offer['desc']}</p><a href='{offer['link']}' target='_blank' style='display: inline-block; background: #fff; color: #da251c; font-weight: bold; padding: 15px 35px; border-radius: 50px; text-decoration: none;'>{offer['btn']}</a></div>", 1)
blog_content = blog_content.replace("[AFFILIATE]", "") 

safe_img_base = f"future {todays_category.lower()} technology"
for idx, mod in enumerate(["cinematic", "cyberpunk", "hyperrealistic"]):
    if "[PHOTO]" in blog_content:
        inner_img_url = f"https://image.pollinations.ai/prompt/{urllib.parse.quote(f'{safe_img_base} {mod}')}?width=800&height=400&nologo=true&seed={post_id + idx + 1}"
        pre_warm_image(inner_img_url)
        blog_content = blog_content.replace("[PHOTO]", f"<div style='text-align: center;'><img src='{inner_img_url}' loading='lazy' onerror=\"this.onerror=null; this.src='https://placehold.co/800x400/c00000/ffffff?text=AI+Finance';\" style='width: 100%; border-radius: 12px; margin: 35px 0; box-shadow: 0 10px 30px rgba(0,0,0,0.15); object-fit: cover;'></div>", 1)

main_img_url = f"https://image.pollinations.ai/prompt/{urllib.parse.quote(f'{safe_img_base} masterpiece')}?width=1200&height=600&nologo=true&seed={post_id}"
pre_warm_image(main_img_url)

audio_filename = f"audio_{post_id}.mp3"
clean_text = re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', ' ', blog_content))).replace("*", "").replace("#", "").strip()
with open("temp.txt", "w", encoding="utf-8") as temp_f: temp_f.write(clean_text)
os.system("pip install edge-tts > /dev/null 2>&1")
os.system(f"edge-tts -f temp.txt --voice hi-IN-SwaraNeural --write-media {audio_filename}")

post_filename = f"post_{post_id}.html"
posts_db.insert(0, {"title": current_topic, "file": post_filename, "date": today_date, "img": main_img_url, "category": todays_category.lower()})
with open("posts.json", "w", encoding="utf-8") as f: json.dump(posts_db, f, ensure_ascii=False, indent=4)

# --- CSS WITH SEARCH BAR ---
premium_css = """<style>:root { --main-red: #da251c; --dark-bg: #111; --text-gray: #444; } html { scroll-behavior: smooth; } * { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Segoe UI', Tahoma, sans-serif; } body { background: #f0f2f5; color: #111; line-height: 1.7; overflow-x: hidden; } header { background: white; border-bottom: 2px solid #eee; box-shadow: 0 4px 10px rgba(0,0,0,0.05); position: sticky; top: 0; z-index: 1000; } .nav-container { max-width: 1200px; margin: 0 auto; padding: 15px 20px; display: flex; justify-content: space-between; align-items: center; position: relative; } .logo { font-size: 26px; font-weight: 900; color: var(--main-red); text-decoration: none; text-transform: uppercase; } .nav-links { display: flex; align-items: center; } .nav-links a { margin-left: 20px; text-decoration: none; color: #111; font-weight: bold; font-size: 16px; transition: 0.3s; } .nav-links a:hover { color: var(--main-red); } .menu-btn { display: none; font-size: 30px; cursor: pointer; color: var(--main-red); font-weight: bold; user-select: none; } .search-container { display: flex; align-items: center; margin-left: 20px; } .search-input { padding: 8px 12px; border: 1px solid #ccc; border-radius: 20px 0 0 20px; outline: none; font-size: 14px; } .search-btn { padding: 8px 15px; background: var(--main-red); color: white; border: none; border-radius: 0 20px 20px 0; cursor: pointer; font-weight: bold; } .container { max-width: 900px; margin: 40px auto; padding: 0 20px; } .article-box { background: white; padding: 40px; border-radius: 12px; box-shadow: 0 5px 20px rgba(0,0,0,0.05); } #article-body { font-size: 20px; color: var(--text-gray); } #article-body h2 { color: #000; margin: 35px 0 15px 0; border-left: 5px solid var(--main-red); padding-left: 15px; background: #fafafa; padding: 10px 15px; border-radius: 0 8px 8px 0; scroll-margin-top: 80px; } #article-body p { margin-bottom: 20px; line-height: 1.8; } /* PREMIUM CODE BLOCKS */ pre { background: #1e1e1e; color: #00ff00; padding: 15px; border-radius: 8px; overflow-x: auto; font-family: monospace; font-size: 16px; margin: 20px 0; border-left: 4px solid var(--main-red); box-shadow: inset 0 0 10px rgba(0,0,0,0.5); } code { background: #f4f4f4; color: #d63384; padding: 2px 6px; border-radius: 4px; font-family: monospace; font-size: 90%; } blockquote { border-left: 5px solid var(--main-red); background: #fdfdfd; padding: 15px 20px; margin: 20px 0; font-style: italic; color: #555; border-radius: 0 8px 8px 0; } .timeline { position: relative; max-width: 900px; margin: 40px auto; } .timeline::after { content: ''; position: absolute; width: 4px; background: var(--main-red); top: 0; bottom: 0; left: 50%; margin-left: -2px; border-radius: 5px; } .timeline-card { padding: 10px 40px; position: relative; background: inherit; width: 50%; box-sizing: border-box; } .timeline-card.left { left: 0; } .timeline-card.right { left: 50%; } .timeline-card::after { content: ''; position: absolute; width: 22px; height: 22px; right: -11px; background-color: white; border: 4px solid var(--main-red); top: 20px; border-radius: 50%; z-index: 1; } .timeline-card.right::after { left: -11px; } .timeline-content { padding: 20px; background: white; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.08); transition: transform 0.3s; } .timeline-content:hover { transform: translateY(-5px); } .timeline-content img { width: 100%; border-radius: 8px; height: 180px; object-fit: cover; margin-bottom: 15px; } footer { background: var(--dark-bg); color: #888; padding: 60px 20px 30px; margin-top: 60px; text-align: center; } .footer-links a { color: #ccc; text-decoration: none; margin: 0 10px; font-size: 14px; } @media (max-width: 768px) { .article-box { padding: 20px; } h1 { font-size: 24px !important; } #article-body { font-size: 16px; } pre { font-size: 14px; } .menu-btn { display: block; } .nav-links { display: none; flex-direction: column; position: absolute; top: 100%; left: 0; width: 100%; background: #ffffff; box-shadow: 0 10px 30px rgba(0,0,0,0.15); border-top: 2px solid var(--main-red); z-index: 1001; padding: 10px 0; } .nav-links.active { display: flex !important; } .nav-links a { margin: 0; padding: 15px 25px; border-bottom: 1px solid #f0f0f0; width: 100%; text-align: left; font-size: 18px; } .search-container { margin: 10px 20px; width: calc(100% - 40px); justify-content: center; } .search-input { width: 100%; } .timeline::after { left: 20px; } .timeline-card { width: 100%; padding-left: 50px; padding-right: 0; } .timeline-card.right { left: 0; } .timeline-card::after, .timeline-card.right::after { left: 10px; right: auto; width: 16px; height: 16px; top: 25px; } .timeline-content { padding: 15px; } .timeline-content img { height: 120px; } } .ticker-wrap { width: 100%; overflow: hidden; background-color: #f1f1f1; border-bottom: 2px solid #C00000; box-sizing: border-box; } .ticker-content { display: flex; white-space: nowrap; animation: tickerAnimation 15s linear infinite; color: #333; font-family: sans-serif; font-size: 14px; font-weight: bold; padding: 10px 0; } .ticker-content span { color: #C00000; } @keyframes tickerAnimation { 0% { transform: translateX(100%); } 100% { transform: translateX(-100%); } }</style>"""
schema_markup = f"""<script type="application/ld+json">{{ "@context": "https://schema.org", "@type": "Article", "headline": "{current_topic}", "image": "{main_img_url}", "author": {{ "@type": "Person", "name": "Mohit (The AI Millionaire)" }}, "publisher": {{ "@type": "Organization", "name": "Digital Kamai Hub" }}, "datePublished": "{today_date}" }}</script>"""
header_html = """<div class="ticker-wrap"><div class="ticker-content"><span>TRENDING:</span> &nbsp; 2026 Best Tech, AI Income, Future Jobs, Digital Kamai Hub Ke Naye Hacks, Share Market Ka Sach!</div></div><header><div class="nav-container"><a href="index.html" class="logo">Digital Kamai Hub</a><div class="menu-btn" onclick="document.getElementById('mobile-menu').classList.toggle('active')">&#9776;</div><div class="nav-links" id="mobile-menu"><a href="index.html">Home</a><a href="category_ai.html">AI Hacks</a><a href="category_trading.html">Trading</a><a href="category_finance.html">Finance</a><a href="about.html">About</a><a href="all-posts.html">All Articles</a><a href="contact.html">Contact</a><div class="search-container"><input type="text" id="site-search" class="search-input" placeholder="Search articles..."><button onclick="searchArticles()" class="search-btn">🔍</button></div></div></div></header><script>function searchArticles() { var query = document.getElementById('site-search').value.toLowerCase(); if(query.length > 2) { window.location.href = 'all-posts.html?q=' + encodeURIComponent(query); } }</script>"""

footer_html = f"""<footer style="margin-top: 40px; background: #111; padding: 40px 20px; text-align: center;"><div style="margin-bottom: 25px;"><p style="color: #ccc; font-size: 14px; margin-bottom: 15px; font-weight: bold; letter-spacing: 1px;">JOIN THE AI MILLIONAIRE COMMUNITY:</p><div style="display: flex; justify-content: center; gap: 15px; flex-wrap: wrap;"><a href="https://www.youtube.com/@TheAIMillionaire-h5g" target="_blank" style="color: #FF0000; text-decoration: none; font-weight: bold; background: white; padding: 8px 15px; border-radius: 5px;">YouTube</a><a href="https://t.me/digitalkamaihub_2026" target="_blank" style="color: #0088cc; text-decoration: none; font-weight: bold; background: white; padding: 8px 15px; border-radius: 5px;">Telegram</a><a href="https://www.instagram.com/aimillionaire_official" target="_blank" style="color: #E1306C; text-decoration: none; font-weight: bold; background: white; padding: 8px 15px; border-radius: 5px;">Instagram</a><a href="https://www.facebook.com/share/18wcH7GqjA/" target="_blank" style="color: #1877F2; text-decoration: none; font-weight: bold; background: white; padding: 8px 15px; border-radius: 5px;">Facebook</a></div></div><div class="footer-links" style="margin-bottom: 20px;"><a href="about.html">About Us</a> | <a href="privacy.html">Privacy Policy</a> | <a href="terms.html">Terms</a> | <a href="disclaimer.html">Disclaimer</a> | <a href="contact.html">Contact</a></div><p style="margin-top:20px; font-size:13px; color: #888;">&copy; {current_year} Digital Kamai Hub. All Rights Reserved.</p></footer>
<button id="scrollTopBtn" onclick="window.scrollTo({{top: 0, behavior: 'smooth'}})" style="display:none; position:fixed; bottom:30px; right:20px; z-index:99; background:#da251c; color:white; border:none; padding:15px 20px; border-radius:50%; cursor:pointer; box-shadow:0 4px 10px rgba(0,0,0,0.3); font-size:20px; font-weight:bold;">↑</button>
<div id="cookieConsent" style="position:fixed; bottom:0; left:0; width:100%; background:#111; color:#fff; text-align:center; padding:15px; z-index:10000; font-size:14px; display:none; box-shadow:0 -5px 15px rgba(0,0,0,0.2);">🍪 Hum behtar anubhav aur AdSense ke liye cookies ka upyog karte hain. <button onclick="acceptCookies()" style="background:#da251c; color:#fff; border:none; padding:5px 15px; border-radius:5px; margin-left:10px; cursor:pointer; font-weight:bold;">Theek Hai</button></div>
<script>
window.addEventListener('scroll', function() {{
    if (window.scrollY > 100) {{ document.getElementById('scrollTopBtn').style.display = 'block'; }} 
    else {{ document.getElementById('scrollTopBtn').style.display = 'none'; }}
    localStorage.setItem('scrollpos_' + window.location.pathname, window.scrollY);
}});
if (!localStorage.getItem('cookiesAccepted')) {{ document.getElementById('cookieConsent').style.display = 'block'; }}
function acceptCookies() {{ localStorage.setItem('cookiesAccepted', 'true'); document.getElementById('cookieConsent').style.display = 'none'; }}
document.addEventListener('DOMContentLoaded', function() {{
    var savedScroll = localStorage.getItem('scrollpos_' + window.location.pathname);
    if (savedScroll && parseInt(savedScroll) > 100) {{
        var toast = document.createElement('div');
        toast.innerHTML = '📚 Aapne pichli baar yahan tak padha tha. <button id="scroll-btn" style="background:#da251c;color:#fff;border:none;padding:5px 10px;border-radius:5px;cursor:pointer;margin-left:10px;font-weight:bold;">Wahin Jayein</button>';
        toast.style.cssText = 'position:fixed;bottom:80px;left:50%;transform:translateX(-50%);background:#222;color:#fff;padding:15px;border-radius:8px;z-index:9999;box-shadow:0 5px 15px rgba(0,0,0,0.3);font-size:14px;display:flex;align-items:center;white-space:nowrap;';
        document.body.appendChild(toast);
        document.getElementById('scroll-btn').onclick = function() {{ window.scrollTo({{top: parseInt(savedScroll), behavior: 'smooth'}}); toast.style.display = 'none'; }};
        setTimeout(function(){{ toast.style.display = 'none'; }}, 8000);
    }}
}});
</script>
"""

top_buttons_html = f"""
<audio id="premium-audio" src="{audio_filename}"></audio>
<div style="display: flex; gap: 10px; margin-bottom: 20px;">
    <button id="audio-btn" onclick="toggleAudio()" style="flex: 2; background: #da251c; color: white; border: none; padding: 10px; border-radius: 5px; font-size: 14px; font-weight: bold; cursor: pointer;">▶️ Sunne Ke Liye Click Karein</button>
    <button onclick="window.open('https://api.whatsapp.com/send?text=Digital Kamai Hub: ' + window.location.href, '_blank')" style="flex: 1; background: #25D366; color: white; border: none; padding: 10px; border-radius: 5px; font-size: 14px; font-weight: bold; cursor: pointer;">💬 WhatsApp</button>
    <button onclick="window.open('https://t.me/share/url?url=' + window.location.href + '&text=Digital Kamai Hub!', '_blank')" style="flex: 1; background: #0088cc; color: white; border: none; padding: 10px; border-radius: 5px; font-size: 14px; font-weight: bold; cursor: pointer;">✈️ Telegram</button>
</div>
"""

author_box_html = """
<div style="background: #ffffff; padding: 25px; border-radius: 12px; margin-top: 40px; margin-bottom: 40px; box-shadow: 0 5px 20px rgba(0,0,0,0.05); display: flex; align-items: center; gap: 20px; border-left: 5px solid #da251c; flex-wrap: wrap;">
    <img src="https://api.dicebear.com/7.x/avataaars/svg?seed=Mohit&backgroundColor=da251c" loading="lazy" style="width: 80px; height: 80px; border-radius: 50%; border: 3px solid #f0f0f0;">
    <div style="flex: 1;">
        <h3 style="margin: 0; color: #111; font-size: 20px;">Mohit (The AI Millionaire)</h3>
        <p style="margin: 5px 0 0 0; color: #555; font-size: 15px; line-height: 1.5;">Founder & Lead AI Automation Expert. Yahan main apne 2026 ke secret hacks, automation aur digital kamai ke 100% working methods share karta hoon. <strong>Smart work > Hard work.</strong></p>
    </div>
</div>
"""

ajax_form_html = """
<div style="background: linear-gradient(135deg, #f9f9f9, #ffffff); padding: 30px; border-radius: 12px; border: 2px dashed #da251c; text-align: center; box-shadow: 0 10px 30px rgba(218, 37, 28, 0.1);">
    <h3 style="color: #111; font-size: 22px; margin-top: 0; margin-bottom: 10px;">🔥 2026 ke Secret Hacks Seedhe Inbox Mein!</h3>
    <p style="color: #555; font-size: 16px; margin-bottom: 20px;">'The AI Millionaire' ki VIP list join karein (Free).</p>
    <form id="ajax-vip-form" style="display: flex; gap: 10px; max-width: 500px; margin: 0 auto; flex-wrap: wrap; justify-content: center;">
        <input type="email" id="vip-email" placeholder="Apna Email likhein..." required style="flex: 1; padding: 12px; border: 1px solid #ccc; border-radius: 8px; font-size: 16px; min-width: 200px;">
        <button type="submit" id="vip-btn" style="background: #111; color: white; border: none; padding: 12px 25px; font-weight: bold; border-radius: 8px; font-size: 16px; cursor: pointer;">Join Now 🚀</button>
    </form>
    <div id="vip-msg" style="display:none; color: #4caf50; font-size: 18px; font-weight: bold; margin-top: 15px; padding: 10px; border: 1px solid #4caf50; border-radius: 8px; background: #e8f5e9;">
        ✅ Thanks for you! Aapka email jud gaya hai. 24-48 ghanto mein aapko update mil jayega.
    </div>
</div>
<script>
document.getElementById('ajax-vip-form').addEventListener('submit', function(e) {
    e.preventDefault();
    var btn = document.getElementById('vip-btn');
    btn.innerText = 'Wait...';
    btn.disabled = true;
    fetch('https://formsubmit.co/ajax/rameshchandra89056@gmail.com', {
        method: 'POST', headers: { 'Content-Type': 'application/json', 'Accept': 'application/json' },
        body: JSON.stringify({ email: document.getElementById('vip-email').value, _subject: 'New VIP Subscriber' })
    }).then(response => response.json()).then(data => {
        document.getElementById('ajax-vip-form').style.display = 'none';
        document.getElementById('vip-msg').style.display = 'block';
    }).catch(error => { btn.innerText = 'Error! Try Again'; btn.disabled = false; });
});
</script>
"""

article_page = f"""<!DOCTYPE html><html lang="hi"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"><title>{current_topic} - Digital Kamai Hub</title>{premium_css}{schema_markup}</head><body><div style="position: fixed; top: 0; left: 0; width: 100%; height: 5px; background-color: transparent; z-index: 9999;"><div id="smart-progress" style="height: 5px; background-color: #da251c; width: 0%; border-top-right-radius: 3px; border-bottom-right-radius: 3px;"></div></div><script>window.addEventListener('scroll', function() {{ var winScroll = document.body.scrollTop || document.documentElement.scrollTop; var height = document.documentElement.scrollHeight - document.documentElement.clientHeight; var scrolled = (winScroll / height) * 100; document.getElementById("smart-progress").style.width = scrolled + "%"; }}); function toggleAudio() {{ var audio = document.getElementById("premium-audio"); var btn = document.getElementById("audio-btn"); if (audio.paused) {{ audio.play(); btn.innerHTML = "⏸️ Pause Audio"; }} else {{ audio.pause(); btn.innerHTML = "▶️ Play Audio"; }} }}</script>{header_html}<div class="container"><div class="article-box"><h1 style="color: #111; margin-bottom: 15px;">{current_topic}</h1><div style="color: #666; font-size: 14px; margin-bottom: 15px; border-bottom: 1px solid #eee; padding-bottom: 10px; font-weight: bold;">Date: {today_date} | Author: Mohit (The AI Millionaire) | Category: {todays_category}</div>{top_buttons_html}<img src="{main_img_url}" loading="lazy" onerror="this.onerror=null; this.src='https://placehold.co/1200x600/da251c/ffffff?text=Digital+Kamai+Hub';" style="width: 100%; border-radius: 10px; margin-bottom: 25px; box-shadow: 0 5px 15px rgba(0,0,0,0.1); object-fit: cover;"><div id="article-body">{blog_content}</div>{author_box_html}{ajax_form_html}</div></div>{footer_html}</body></html>"""
with open(post_filename, "w", encoding="utf-8") as f: f.write(article_page)

categorized_posts = {'ai': [], 'trading': [], 'finance': [], 'trending': []}
for p in posts_db: 
    cat = p.get('category', 'trending').lower()
    if cat not in categorized_posts: cat = 'trending'
    categorized_posts[cat].append(p)
    if cat != 'trending': categorized_posts['trending'].append(p)

def generate_timeline(post_list, is_home=False):
    if not post_list: return "<p style='text-align: center; color: #888; margin-top: 30px;'>Abhi yahan koi article nahi hai. Naye updates ka intezaar karein!</p>"
    html_str = '<div class="timeline">'
    for i, p in enumerate(post_list):
        side = "left" if i % 2 == 0 else "right"
        html_str += f"<div class='timeline-card {side}'><div class='timeline-content'><img src='{p['img']}' loading='lazy' onerror=\"this.onerror=null; this.src='https://placehold.co/800x400/111/fff?text=Digital+Kamai+Hub';\"><p style='color: #888; font-size: 13px; font-weight: bold; margin-bottom: 5px;'>📅 {p['date']}</p><h3 style='margin-bottom: 10px; font-size: 18px; line-height: 1.4;'><a href='{p['file']}' style='color: #111; text-decoration: none;'>{p['title']}</a></h3><a href='{p['file']}' style='color: #da251c; font-weight: bold; text-decoration: none; font-size: 14px;'>Read More →</a></div></div>"
    # --- PAGINATION BUTTON ---
    if is_home and len(posts_db) > 10:
        html_str += "</div><div style='text-align:center; margin-top:50px;'><a href='all-posts.html' style='background:#111; color:#fff; padding:15px 30px; border-radius:50px; text-decoration:none; font-weight:bold; font-size:16px; box-shadow:0 4px 10px rgba(0,0,0,0.2);'>Aur Articles Dekhein ➔</a>"
    html_str += '</div>'
    return html_str

def create_page(filename, title, post_list, is_home=False):
    with open(filename, "w", encoding="utf-8") as f: f.write(f"<!DOCTYPE html><html lang='hi'><head><meta charset='UTF-8'><meta name='viewport' content='width=device-width, initial-scale=1.0'><title>{title} - Digital Kamai Hub</title>{premium_css}</head><body>{header_html}<div class='container'><h1 style='text-align: center; margin-bottom: 10px; color: #da251c; font-size: 32px; font-weight: 900;'>{title}</h1>{generate_timeline(post_list, is_home)}</div>{footer_html}</body></html>")

create_page("index.html", "🔥 Latest Trending Articles", posts_db[:10], is_home=True)
create_page("category_ai.html", "🤖 AI & Tech Hacks", categorized_posts['ai'])
create_page("category_trading.html", "📈 Share Market & Trading", categorized_posts['trading'])
create_page("category_finance.html", "💰 Finance & Wealth", categorized_posts['finance'])
create_page("all-posts.html", "📚 Sabhi Articles (Archive)", posts_db)

pages = {
    "about": ("About Us", "<h2 style='color: var(--main-red); margin-bottom: 15px; font-size: 28px;'>Hamari Kahani (Our Story)</h2><p style='font-size: 18px; margin-bottom: 25px; color: #333;'>Namaste! <strong>Digital Kamai Hub</strong> mein aapka swagat hai. Yeh sirf ek blog nahi, balki ek digital revolution hai.</p><h2 style='color: var(--main-red); margin-bottom: 15px; font-size: 24px;'>🎯 Mission & Vision</h2><p style='font-size: 18px; margin-bottom: 25px; color: #333;'>Hamara mission bilkul saaf hai: <strong>\"Bacchon ka khel nahi, Smart Work!\"</strong></p><h2 style='color: var(--main-red); margin-bottom: 15px; font-size: 24px;'>👨‍💻 Meet The Founder: Mohit (The AI Millionaire)</h2><div style='background: #fafafa; padding: 25px; border-left: 5px solid var(--main-red); border-radius: 8px; margin-bottom: 30px;'><p style='font-size: 17px; margin-bottom: 15px; color: #222;'>Mohit ek <strong>Full-Stack Web Developer aur Visionary Entrepreneur</strong> hain. Any manual task is a bug.</p></div>"),
    "privacy": ("Privacy Policy", "<h2 style='color: var(--main-red); margin-bottom: 15px; font-size: 28px;'>Privacy Policy</h2><p style='font-size: 16px; margin-bottom: 15px; color: #333;'>Digital Kamai Hub par hum aapki privacy ka poora samman karte hain. Niche padhein ki hum aapka data kaise manage karte hain:</p><h3 style='margin-top:20px;'>1. Cookies aur Web Beacons</h3><p>Humari website aapka behtar anubhav dene ke liye 'Cookies' ka upyog karti hai. Isse humein samajh aata hai ki aap kaunse pages pasand karte hain.</p><h3 style='margin-top:20px;'>2. Google DoubleClick DART Cookie</h3><p>Google humari site par third-party vendor ke roop mein ads dikhata hai. Google DART cookies ka istemal karta hai taaki aapko aapki pasand (interest) ke hisab se ads dikhayein. Aap <a href='https://policies.google.com/technologies/ads' target='_blank'>Google Ad and Content Network Privacy Policy</a> par jaakar DART cookies ka upyog band kar sakte hain.</p><h3 style='margin-top:20px;'>3. Data Security</h3><p>Hum VIP newsletter ya Contact form ke zariye aapse jo Email lete hain, wo 100% surakshit (safe) hai. Hum kabhi bhi aapka data kisi third-party ko sell (bechte) nahi karte hain.</p>"),
    "terms": ("Terms & Conditions", "<h2 style='color: var(--main-red); margin-bottom: 15px; font-size: 28px;'>Terms and Conditions</h2><p style='font-size: 16px; margin-bottom: 15px; color: #333;'>Is website ka istemal karke aap hamari in sharton ko (Terms of Use) ko mante hain:</p><ul style='line-height: 1.8; font-size: 16px;'><li><strong>Samagri (Content) ka upyog:</strong> Is website par maujood sabhi articles, photos aur audio Digital Kamai Hub ki property hain. Ise copy karke apne blog par publish karna Copyright Act ka ullanghan (violation) hoga.</li><li><strong>Bhari (External) Links:</strong> Humari site par affiliate links ya dusri sites ke links ho sakte hain. Un links par click karne ke baad hone wali kisi bhi activity ke liye hum zimmewar nahi hain.</li><li><strong>User Conduct:</strong> Humari website par kisi bhi tarah ka spam, abusive language ya illegal activity completely prohibited hai.</li></ul>"),
    "disclaimer": ("Disclaimer", "<h2 style='color: var(--main-red); margin-bottom: 15px; font-size: 28px;'>Disclaimer (Chetawani)</h2><p style='font-size: 16px; margin-bottom: 15px; color: #333;'><strong>Digital Kamai Hub</strong> par di gayi sabhi jankari (Finance, Share Market, Trading, AI Tools) keval shikhsha (Education) ke uddeshya se hai.</p><ul style='line-height: 1.8; font-size: 16px;'><li><strong>Financial Advice Nahi:</strong> Hum SEBI registered financial advisor nahi hain. Website par diya gaya koi bhi content financial ya investment advice nahi hai.</li><li><strong>Risk (Jokhim):</strong> Share Market, Crypto aur Trading mein bohot jokhim (risk) hota hai. Aap apna paisa khone (lose) ke liye poori tarah khud zimmewar honge. Kripya nivesh karne se pehle apni research zaroor karein.</li><li><strong>Affiliate Disclosure:</strong> Is blog mein kuch links 'Affiliate Links' ho sakte hain. Agar aap un links se kuch kharidte hain, toh humein ek chota commission mil sakta hai, lekin iska aapse koi extra charge nahi liya jayega.</li></ul>"),
    "contact": ("Contact Us", """<div style="text-align: center;"><h1 style="color: #da251c; font-size: 32px; font-weight: bold; margin-bottom: 10px;">Contact Us</h1><p style="margin-bottom: 30px; font-size: 18px; color: #555;">Kripya apne sawal, feedback, ya business inquiry niche diye gaye form ke madhyam se bhejein.</p><div id="form-container" style="max-width: 550px; margin: 0 auto; text-align: left; background: #fff; padding: 30px; border-radius: 12px; box-shadow: 0 5px 15px rgba(0,0,0,0.1); border-top: 5px solid #da251c;"><form id="contact-ajax" style="display: flex; flex-direction: column; gap: 15px;"><input type="text" id="c-name" placeholder="Aapka Naam" required style="padding: 15px; border: 1px solid #ccc; border-radius: 8px; font-size: 16px;"><input type="email" id="c-email" placeholder="Aapka Email" required style="padding: 15px; border: 1px solid #ccc; border-radius: 8px; font-size: 16px;"><textarea id="c-msg" rows="5" placeholder="Apna Sandesh (Message) likhein..." required style="padding: 15px; border: 1px solid #ccc; border-radius: 8px; font-size: 16px;"></textarea><button type="submit" id="c-btn" style="background: #da251c; color: white; padding: 15px; font-weight: bold; font-size: 18px; border: none; border-radius: 8px; cursor: pointer;">Bhejein (Send Message)</button></form><div id="c-success" style="display:none; text-align: center; padding: 20px; background: #e8f5e9; border: 2px solid #4caf50; border-radius: 8px; margin-top: 10px;"><h3 style="color: #4caf50; margin-top:0; margin-bottom: 10px;">✅ Message Bhej Diya Gaya!</h3><p style="color: #333; font-size: 16px; margin: 0;">Thanks for you! Hum 24-48 ghante ke andar aapse sampark karenge.</p></div></div></div><script>document.getElementById('contact-ajax').addEventListener('submit', function(e) { e.preventDefault(); var btn = document.getElementById('c-btn'); btn.innerText = 'Wait...'; btn.disabled = true; fetch('https://formsubmit.co/ajax/rameshchandra89056@gmail.com', { method: 'POST', headers: { 'Content-Type': 'application/json', 'Accept': 'application/json' }, body: JSON.stringify({ name: document.getElementById('c-name').value, email: document.getElementById('c-email').value, message: document.getElementById('c-msg').value, _subject: 'New Contact Inquiry' }) }).then(response => response.json()).then(data => { document.getElementById('contact-ajax').style.display = 'none'; document.getElementById('c-success').style.display = 'block'; }).catch(error => { btn.innerText = 'Error!'; btn.disabled = false; }); });</script>""")
}

for p_file, (p_title, p_content) in pages.items():
    with open(f"{p_file}.html", "w", encoding="utf-8") as f: f.write(f"<!DOCTYPE html><html lang='hi'><head><meta charset='UTF-8'><meta name='viewport' content='width=device-width, initial-scale=1.0'><title>{p_title} - Digital Kamai Hub</title>{premium_css}</head><body>{header_html}<div class='container'><div class='article-box'>{p_content}</div></div>{footer_html}</body></html>")

try:
    sitemap_content = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    for file in [f for f in os.listdir() if f.endswith('.html')]: sitemap_content += f'  <url>\n    <loc>https://rameshchandra89056-bloger.github.io/AI-Autoblogger-Engine/{file}</loc>\n    <lastmod>{datetime.now().strftime("%Y-%m-%d")}</lastmod>\n    <changefreq>daily</changefreq>\n  </url>\n'
    with open('sitemap.xml', 'w', encoding='utf-8') as f: f.write(sitemap_content + '</urlset>')
except: pass

print("✅ Website 100% safalta ke sath Theek ho gayi hai!")
