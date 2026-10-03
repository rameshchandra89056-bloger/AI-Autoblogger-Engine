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
    text = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', text)
    text = re.sub(r'\*(.*?)\*', r'<em>\1</em>', text)
    text = re.sub(r'```html', '', text)
    text = re.sub(r'```', '', text)
    text = re.sub(r'## (.*?)\n', r'<h2>\1</h2>', text)
    text = re.sub(r'### (.*?)\n', r'<h3>\1</h3>', text)
    return text.strip()

# --- FIXED TELEGRAM FUNCTIONS (WITH STRIP & SAFE TEXT) ---
def send_telegram_msg(message, target_chat_id=None):
    token = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
    chat_id = str(target_chat_id).strip() if target_chat_id else os.environ.get("TELEGRAM_CHAT_ID", "").strip()
    if not token or not chat_id: return
    try: 
        requests.get(f"https://api.telegram.org/bot{token}/sendMessage", params={"chat_id": chat_id, "text": urllib.parse.unquote(message)}, timeout=10)
    except: pass

def send_public_telegram_msg(title, post_url):
    pub_token = os.environ.get("PUBLIC_BOT_TOKEN", "").strip()
    pub_chat_id = os.environ.get("PUBLIC_CHANNEL_ID", "").strip()
    if not pub_token or not pub_chat_id: return
    # Markdown hata diya hai taaki koi error na aaye
    message = f"🔥 Naya Dhamakedaar Article Live Ho Chuka Hai!\n\n📌 {title}\n\n👇 Pura article padhne ke liye yahan click karein:\n🔗 {post_url}"
    try: 
        requests.post(f"https://api.telegram.org/bot{pub_token}/sendMessage", json={"chat_id": pub_chat_id, "text": message}, timeout=15)
    except: pass
# ---------------------------------------------------------

raw_keys = os.environ.get("GEMINI_API_KEY", "")
API_KEYS = [k.strip() for k in raw_keys.split(",") if k.strip()]
if not API_KEYS:
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
                if len(text) > 100: return clean_ad_garbage(text)
        except Exception: time.sleep(8)
    return ""

current_topic = ""
blog_content = ""

EMERGENCY_INTRO = f"<p>Dosto, 2026 mein technology aur aarthik duniya itni tezi se badal rahi hai ki jo aaj update nahi hoga, wo kal bahot piche chhut jayega.</p><div style='background: #fffafa; border-left: 5px solid #da251c; padding: 20px; border-radius: 8px; margin-bottom: 25px;'><h3 style='color: #da251c; margin-top: 0;'>📍 Is Article Mein Kya Hai:</h3><ul style='list-style:none; padding:0; line-height: 1.8;'><li>👉 <a href='#basic' style='color:#da251c; text-decoration:none; font-weight:bold;'>1. Basic Samajh (0 se shuruaat)</a></li><li>👉 <a href='#deep' style='color:#da251c; text-decoration:none; font-weight:bold;'>2. Top Tools aur Deep Setup Guide</a></li><li>👉 <a href='#pro' style='color:#da251c; text-decoration:none; font-weight:bold;'>3. Pro Execution aur Scale-up Hacks</a></li></ul></div>"
EMERGENCY_BODY = "<h2 id='basic'>1. Basic Samajh: Shunya Se Shuruaat</h2><p>Duniya mein 90% log sirf isliye fail hote hain kyunki wo direct paisa kamane ki sochte hain, bina foundation banaye.</p>[PHOTO]<h2 id='deep'>2. Top Tools aur Deep Setup Guide</h2><p>2026 mein aapke paas sahi AI aur automation tools hone chahiye.</p>[PHOTO]<h2 id='pro'>3. Pro Execution aur Scale-up Hacks</h2><p>Jab aapka pehla profit aaye, toh use turant kharch na karein.</p>[PHOTO]"
EMERGENCY_OUTRO = "<h2>Nishkarsh (Conclusion)</h2><p>Dosto, ummeed karta hoon yeh deep dive jankari aapke kaam aayegi.</p>[AFFILIATE]<h2>Akshar Puche Jane Wale Sawal (FAQs)</h2><p><strong>Q1: Kya isme risk hai?</strong><br>A: Duniya ka har bada kaam risk ke sath aata hai.</p>[AFFILIATE]"

try:
    start_time = time.time()
    raw_topic = ask_ai(f"Tum ek trend analyst ho. Aaj ki category '{todays_category}' hai. Mujhe {current_year} ke liye '{todays_category}' niche par ek bohot hi viral Hindi blog title do. Sirf Title likhna.")
    if not raw_topic: current_topic = f"2026 Mein {todays_category} Se Paise Kaise Kamaye"
    else: current_topic = clean_ad_garbage(raw_topic.replace('"', '').replace("'", "").replace("*", "")).strip()

    intro_prompt = f"Topic: '{current_topic}'. Ek lamba Introduction likho. Uske baad ek Clickable TOC (Table of Contents) zaroor do. Format for TOC: <div style='background: #fffafa; border-left: 5px solid #da251c; padding: 20px; border-radius: 8px; margin-bottom: 25px;'><h3 style='color: #da251c; margin-top: 0;'>📍 Is Article Mein Kya Hai:</h3><ul style='list-style:none; padding:0;'><li>👉 <a href='#basic' style='color:#da251c; text-decoration:none; font-weight:bold;'>1. Basic Samajh (0 to 30%)</a></li> <li>👉 <a href='#deep' style='color:#da251c; text-decoration:none; font-weight:bold;'>2. Tools aur Deep Detail (30 to 70%)</a></li> <li>👉 <a href='#pro' style='color:#da251c; text-decoration:none; font-weight:bold;'>3. Pro Hacks (70 to 100%)</a></li></ul></div>. Poora HTML tags mein do."
    chunk_1 = ask_ai(intro_prompt)
    if not chunk_1: chunk_1 = EMERGENCY_INTRO
    
    time.sleep(8) 
    body_prompt = f"Topic: '{current_topic}'. Ab article ki main body likho. Total 3 sub-headings (<h2>) likho id ke sath. Har <h2> wale section ke baad exactly 1 baar [PHOTO] tag likho. HTML format mein do."
    chunk_2 = ask_ai(body_prompt)
    if not chunk_2: chunk_2 = EMERGENCY_BODY
    
    time.sleep(8) 
    chunk_3 = ask_ai(f"Topic: '{current_topic}'. Ek detailed Conclusion aur 3 FAQs likho. Beech-beech mein exactly 2 baar [AFFILIATE] tag likho. HTML mein do.")
    if not chunk_3: chunk_3 = EMERGENCY_OUTRO

    blog_content = clean_ad_garbage(chunk_1 + "\n" + chunk_2 + "\n" + chunk_3) 
    exec_time = round((time.time() - start_time) / 60, 2)
    send_telegram_msg(urllib.parse.quote(f"🟢 SYSTEM RUN SUCCESS\n\n🎯 Category: {todays_category}\n📝 Topic: {current_topic}\n✅ Status: Adsterra Active"))

except Exception as e:
    send_telegram_msg(urllib.parse.quote(f"🔴 SYSTEM FAILED\n⚠️ {str(e)[:100]}"))
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

# --- FOOLPROOF IMAGE SYSTEM ---
safe_topic = urllib.parse.quote(f"future {todays_category.lower()} tech")
fallback_url = "https://dummyimage.com/800x400/111/fff&text=Digital+Kamai+Hub"

for idx in range(3):
    if "[PHOTO]" in blog_content:
        api_primary = f"https://image.pollinations.ai/prompt/{safe_topic}?width=800&height=400&nologo=true&seed={post_id + idx + 1}"
        blog_content = blog_content.replace("[PHOTO]", f"<div style='text-align: center;'><img src='{api_primary}' onerror=\"this.onerror=null; this.src='{fallback_url}';\" loading='lazy' style='width: 100%; min-height: 200px; border-radius: 12px; margin: 35px 0; box-shadow: 0 10px 30px rgba(0,0,0,0.15); object-fit: cover; background-color: #e2e8f0;'></div>", 1)

main_primary = f"https://image.pollinations.ai/prompt/{safe_topic}?width=1200&height=600&nologo=true&seed={post_id}"
main_fallback = f"https://dummyimage.com/1200x600/da251c/ffffff&text={urllib.parse.quote(current_topic[:30])}"

# --- AUDIO GENERATION ---
audio_filename = f"audio_{post_id}.mp3"
clean_text = re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', ' ', blog_content))).replace("*", "").replace("#", "").strip()
with open("temp.txt", "w", encoding="utf-8") as temp_f: temp_f.write(clean_text)
os.system("pip install edge-tts > /dev/null 2>&1")
os.system(f"edge-tts -f temp.txt --voice hi-IN-SwaraNeural --write-media {audio_filename}")

post_filename = f"post_{post_id}.html"
posts_db.insert(0, {"title": current_topic, "file": post_filename, "date": today_date, "img": main_primary, "fallback_img": main_fallback, "category": todays_category.lower()})
with open("posts.json", "w", encoding="utf-8") as f: json.dump(posts_db, f, ensure_ascii=False, indent=4)

# =======================================================
# 📱 MOBILE-LOCKED CSS (LAPTOP PAR BHI ANDROID VIEW)
# =======================================================
premium_css = """<style>
:root { --main-red: #da251c; --dark-bg: #111; --text-gray: #444; } 
html { scroll-behavior: smooth; } 
* { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Segoe UI', Tahoma, sans-serif; } 
body { background: #e9ecef; color: #111; line-height: 1.7; overflow-x: hidden; } 
header { background: white; border-bottom: 2px solid #eee; box-shadow: 0 4px 10px rgba(0,0,0,0.05); position: sticky; top: 0; z-index: 1000; } 
.nav-container { max-width: 500px; margin: 0 auto; padding: 15px 20px; display: flex; justify-content: space-between; align-items: center; position: relative; } 
.logo { font-size: 22px; font-weight: 900; color: var(--main-red); text-decoration: none; text-transform: uppercase; } 
.menu-btn { display: block; font-size: 30px; cursor: pointer; color: var(--main-red); font-weight: bold; user-select: none; } 
.nav-links { display: none; flex-direction: column; position: absolute; top: 100%; left: 0; width: 100%; background: #ffffff; box-shadow: 0 10px 30px rgba(0,0,0,0.15); border-top: 2px solid var(--main-red); z-index: 1001; padding: 10px 0; } 
.nav-links.active { display: flex !important; } 
.nav-links a { margin: 0; padding: 15px 25px; border-bottom: 1px solid #f0f0f0; width: 100%; text-align: left; font-size: 18px; color: #111; font-weight: bold; text-decoration: none; } 
.search-container { margin: 10px 20px; width: calc(100% - 40px); display: flex; justify-content: center; } 
.search-input { width: 100%; padding: 8px 12px; border: 1px solid #ccc; border-radius: 20px 0 0 20px; outline: none; font-size: 14px; } 
.search-btn { padding: 8px 15px; background: var(--main-red); color: white; border: none; border-radius: 0 20px 20px 0; cursor: pointer; font-weight: bold; } 
.container { max-width: 500px; margin: 20px auto; padding: 0 15px; } 
.article-box { background: white; padding: 25px; border-radius: 12px; box-shadow: 0 5px 20px rgba(0,0,0,0.05); } 
#article-body { font-size: 16px; color: var(--text-gray); } 
#article-body h2 { color: #000; margin: 30px 0 15px 0; border-left: 5px solid var(--main-red); padding-left: 15px; background: #fafafa; padding: 10px 15px; border-radius: 0 8px 8px 0; font-size: 20px; } 
#article-body h3 { color: #333; margin: 25px 0 10px 0; font-size: 18px; } 
#article-body p { margin-bottom: 20px; line-height: 1.8; } 
.timeline { position: relative; max-width: 500px; margin: 40px auto; } 
.timeline::after { content: ''; position: absolute; width: 4px; background: var(--main-red); top: 0; bottom: 0; left: 20px; margin-left: -2px; border-radius: 5px; } 
.timeline-card { width: 100%; padding: 10px 0 10px 50px; position: relative; box-sizing: border-box; left: 0 !important; } 
.timeline-card::after { content: ''; position: absolute; width: 16px; height: 16px; left: 10px !important; right: auto !important; background-color: white; border: 4px solid var(--main-red); top: 25px; border-radius: 50%; z-index: 1; } 
.timeline-content { padding: 15px; background: white; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.08); transition: transform 0.3s; } 
.timeline-content img { display: block; width: 100%; height: 180px; object-fit: cover; margin-bottom: 15px; background-color: #e2e8f0; border-radius: 8px; } 
footer { background: var(--dark-bg); color: #888; padding: 40px 20px 30px; margin-top: 50px; text-align: center; max-width: 500px; margin-left: auto; margin-right: auto; border-radius: 12px 12px 0 0; } 
.footer-links a { color: #ccc; text-decoration: none; margin: 0 10px; font-size: 14px; } 
</style>"""

schema_markup = f"""<script type="application/ld+json">{{ "@context": "https://schema.org", "@type": "Article", "headline": "{current_topic}", "image": "{main_primary}", "author": {{ "@type": "Person", "name": "Mohit (The AI Millionaire)" }}, "publisher": {{ "@type": "Organization", "name": "Digital Kamai Hub" }}, "datePublished": "{today_date}" }}</script>"""
header_html = """<header><div class="nav-container"><a href="index.html" class="logo">Digital Kamai Hub</a><div class="menu-btn" onclick="document.getElementById('mobile-menu').classList.toggle('active')">&#9776;</div><div class="nav-links" id="mobile-menu"><a href="index.html">Home</a><a href="all-posts.html">All Articles</a></div></div></header><script>function searchArticles() { var query = document.getElementById('site-search').value.toLowerCase(); if(query.length > 2) { window.location.href = 'all-posts.html?q=' + encodeURIComponent(query); } }</script>"""

# 💰 ADSTERRA CODE 💰
footer_html = f"""<footer style="margin-top: 40px; background: #111; padding: 40px 20px; text-align: center;"><div style="margin-bottom: 25px;"><p style="color: #ccc; font-size: 14px; margin-bottom: 15px; font-weight: bold; letter-spacing: 1px;">JOIN THE AI MILLIONAIRE COMMUNITY:</p><div style="display: flex; justify-content: center; gap: 10px; flex-wrap: wrap;"><a href="https://www.youtube.com/@TheAIMillionaire-h5g" target="_blank" style="color: #FF0000; text-decoration: none; font-weight: bold; background: white; padding: 8px 12px; border-radius: 5px;">YouTube</a><a href="https://t.me/digitalkamaihub_2026" target="_blank" style="color: #0088cc; text-decoration: none; font-weight: bold; background: white; padding: 8px 12px; border-radius: 5px;">Telegram</a></div></div><div class="footer-links" style="margin-bottom: 20px;"><a href="about.html">About Us</a> | <a href="contact.html">Contact</a></div><p style="margin-top:20px; font-size:13px; color: #888;">&copy; {current_year} Digital Kamai Hub. All Rights Reserved.</p></footer>
<button id="scrollTopBtn" onclick="window.scrollTo({{top: 0, behavior: 'smooth'}})" style="display:none; position:fixed; bottom:30px; right:20px; z-index:99; background:#da251c; color:white; border:none; padding:15px 20px; border-radius:50%; cursor:pointer; box-shadow:0 4px 10px rgba(0,0,0,0.3); font-size:20px; font-weight:bold;">↑</button>
<script>
window.addEventListener('scroll', function() {{ if (window.scrollY > 100) {{ document.getElementById('scrollTopBtn').style.display = 'block'; }} else {{ document.getElementById('scrollTopBtn').style.display = 'none'; }} }});
</script>
<script src="https://pl31601171.profitableratecpmnetwork.com/1f/d8/5e/1fd85e18370bd0dd9187ebabdb13185f.js"></script>
"""

top_buttons_html = f"""
<audio id="premium-audio" src="{audio_filename}"></audio>
<div style="display: flex; gap: 8px; margin-bottom: 20px;">
    <button id="audio-btn" onclick="toggleAudio()" style="flex: 2; background: #da251c; color: white; border: none; padding: 10px; border-radius: 5px; font-size: 13px; font-weight: bold; cursor: pointer;">▶️ Play Audio</button>
    <button onclick="window.open('https://api.whatsapp.com/send?text=Digital Kamai Hub: ' + window.location.href, '_blank')" style="flex: 1; background: #25D366; color: white; border: none; padding: 10px; border-radius: 5px; font-size: 13px; font-weight: bold; cursor: pointer;">💬 WA</button>
    <button onclick="window.open('https://t.me/share/url?url=' + window.location.href + '&text=Digital Kamai Hub!', '_blank')" style="flex: 1; background: #0088cc; color: white; border: none; padding: 10px; border-radius: 5px; font-size: 13px; font-weight: bold; cursor: pointer;">✈️ TG</button>
</div>
"""

author_box_html = """
<div style="background: #ffffff; padding: 20px; border-radius: 12px; margin-top: 30px; margin-bottom: 30px; box-shadow: 0 5px 20px rgba(0,0,0,0.05); display: flex; align-items: center; gap: 15px; border-left: 5px solid #da251c; flex-wrap: wrap;">
    <div style="width: 70px; height: 70px; border-radius: 50%; background: #da251c; color: white; display: flex; align-items: center; justify-content: center; font-size: 30px; font-weight: bold;">M</div>
    <div style="flex: 1;">
        <h3 style="margin: 0; color: #111; font-size: 18px;">Mohit (The AI Millionaire)</h3>
        <p style="margin: 5px 0 0 0; color: #555; font-size: 14px; line-height: 1.5;">Founder & Lead AI Automation Expert. <strong>Smart work > Hard work.</strong></p>
    </div>
</div>
"""

ajax_form_html = """
<div style="background: linear-gradient(135deg, #f9f9f9, #ffffff); padding: 25px; border-radius: 12px; border: 2px dashed #da251c; text-align: center;">
    <h3 style="color: #111; font-size: 18px; margin-top: 0; margin-bottom: 10px;">🔥 VIP List Join Karein</h3>
    <form id="ajax-vip-form" style="display: flex; gap: 10px; flex-wrap: wrap; justify-content: center;">
        <input type="email" id="vip-email" placeholder="Apna Email likhein..." required style="flex: 1; padding: 10px; border: 1px solid #ccc; border-radius: 8px; font-size: 14px; min-width: 150px;">
        <button type="submit" id="vip-btn" style="background: #111; color: white; border: none; padding: 10px 20px; font-weight: bold; border-radius: 8px; font-size: 14px;">Join 🚀</button>
    </form>
    <div id="vip-msg" style="display:none; color: #4caf50; font-size: 14px; font-weight: bold; margin-top: 15px; padding: 10px; border: 1px solid #4caf50; border-radius: 8px; background: #e8f5e9;">✅ Thanks! Aapka email jud gaya hai.</div>
</div>
<script>
document.getElementById('ajax-vip-form').addEventListener('submit', function(e) {
    e.preventDefault();
    var btn = document.getElementById('vip-btn'); btn.innerText = 'Wait...'; btn.disabled = true;
    fetch('https://formsubmit.co/ajax/rameshchandra89056@gmail.com', { method: 'POST', headers: { 'Content-Type': 'application/json', 'Accept': 'application/json' }, body: JSON.stringify({ email: document.getElementById('vip-email').value, _subject: 'New VIP Subscriber' }) }).then(response => response.json()).then(data => { document.getElementById('ajax-vip-form').style.display = 'none'; document.getElementById('vip-msg').style.display = 'block'; }).catch(error => { btn.innerText = 'Error!'; btn.disabled = false; });
});
</script>
"""

article_page = f"""<!DOCTYPE html><html lang="hi"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"><title>{current_topic} - Digital Kamai Hub</title>{premium_css}{schema_markup}</head><body><script>function toggleAudio() {{ var audio = document.getElementById("premium-audio"); var btn = document.getElementById("audio-btn"); if (audio.paused) {{ audio.play(); btn.innerHTML = "⏸️ Pause Audio"; }} else {{ audio.pause(); btn.innerHTML = "▶️ Play Audio"; }} }}</script>{header_html}<div class="container"><div class="article-box"><h1 style="color: #111; font-size: 24px; margin-bottom: 15px;">{current_topic}</h1><div style="color: #666; font-size: 13px; margin-bottom: 15px; border-bottom: 1px solid #eee; padding-bottom: 10px; font-weight: bold;">📅 {today_date} | {todays_category.upper()}</div>{top_buttons_html}<img src="{main_primary}" onerror="this.onerror=null; this.src='{main_fallback}';" loading="lazy" style="width: 100%; min-height: 200px; border-radius: 10px; margin-bottom: 25px; box-shadow: 0 5px 15px rgba(0,0,0,0.1); object-fit: cover; background-color: #e2e8f0;"><div id="article-body">{blog_content}</div>{author_box_html}{ajax_form_html}</div></div>{footer_html}</body></html>"""
with open(post_filename, "w", encoding="utf-8") as f: f.write(article_page)

def generate_timeline(post_list):
    if not post_list: return "<p style='text-align: center; color: #888; margin-top: 30px;'>Abhi yahan koi article nahi hai.</p>"
    html_str = '<div class="timeline">'
    for p in post_list:
        img_src = p.get('img', p.get('fallback_img', 'https://dummyimage.com/800x400/111/fff&text=Digital+Kamai+Hub'))
        html_str += f"<div class='timeline-card'><div class='timeline-content'><img src='{img_src}' onerror=\"this.onerror=null; this.src='https://dummyimage.com/800x400/da251c/fff&text=Digital+Kamai+Hub';\"><p style='color: #888; font-size: 13px; font-weight: bold; margin-bottom: 5px;'>📅 {p['date']}</p><h3 style='margin-bottom: 10px; font-size: 18px; line-height: 1.4;'><a href='{p['file']}' style='color: #111; text-decoration: none;'>{p['title']}</a></h3><a href='{p['file']}' style='color: #da251c; font-weight: bold; text-decoration: none; font-size: 14px;'>Read More →</a></div></div>"
    html_str += '</div>'
    return html_str

def create_page(filename, title, post_list):
    with open(filename, "w", encoding="utf-8") as f: f.write(f"<!DOCTYPE html><html lang='hi'><head><meta charset='UTF-8'><meta name='viewport' content='width=device-width, initial-scale=1.0'><title>{title} - Digital Kamai Hub</title>{premium_css}</head><body>{header_html}<div class='container'><h1 style='text-align: center; margin-bottom: 10px; color: #da251c; font-size: 26px; font-weight: 900;'>{title}</h1>{generate_timeline(post_list)}</div>{footer_html}</body></html>")

create_page("index.html", "🔥 Latest Articles", posts_db[:10])
create_page("all-posts.html", "📚 Sabhi Articles", posts_db)

post_full_url = f"https://rameshchandra89056-bloger.github.io/AI-Autoblogger-Engine/{post_filename}"
send_public_telegram_msg(current_topic, post_full_url)
