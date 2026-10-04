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

# Auto-install missing libraries for advanced features
os.system("pip install edge-tts requests google-auth > /dev/null 2>&1")

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

# ==========================================
# 🚀 TELEGRAM, ONESIGNAL & GOOGLE APIS
# ==========================================
def send_telegram_msg(message, target_chat_id=None):
    token = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
    chat_id = str(target_chat_id).strip() if target_chat_id else os.environ.get("TELEGRAM_CHAT_ID", "").strip()
    if not token or not chat_id: return
    try: requests.get(f"https://api.telegram.org/bot{token}/sendMessage", params={"chat_id": chat_id, "text": urllib.parse.unquote(message)}, timeout=10)
    except: pass

def send_public_telegram_msg(title, post_url):
    pub_token = os.environ.get("PUBLIC_BOT_TOKEN", "").strip()
    pub_chat_id = os.environ.get("PUBLIC_CHANNEL_ID", "").strip()
    if not pub_token or not pub_chat_id: return
    message = f"🔥 *Naya Dhamakedaar Article Live Ho Chuka Hai!*\n\n📌 *{title}*\n\n👇 *Pura article padhne ke liye yahan click karein:*\n🔗 {post_url}"
    try: requests.post(f"https://api.telegram.org/bot{pub_token}/sendMessage", json={"chat_id": pub_chat_id, "text": message, "parse_mode": "Markdown"}, timeout=15)
    except: pass

def send_onesignal_push(title, post_url):
    api_key = os.environ.get("ONESIGNAL_API_KEY", "").strip()
    if not api_key: return
    headers = {"Content-Type": "application/json", "Authorization": f"Basic {api_key}"}
    payload = {
        "app_id": "f11333ae-cc73-489e-a1a5-6a74129c3785",
        "included_segments": ["All"],
        "headings": {"en": "Digital Kamai Hub 🚀"},
        "contents": {"en": f"Naya Article: {title}"},
        "url": post_url
    }
    try: requests.post("https://onesignal.com/api/v1/notifications", json=payload, headers=headers, timeout=10)
    except: pass

def ping_google_indexing(url_list):
    creds_json = os.environ.get("GOOGLE_CREDENTIALS", "").strip()
    if not creds_json: return
    try:
        from google.oauth2 import service_account
        from google.auth.transport.requests import AuthorizedSession
        creds_dict = json.loads(creds_json)
        creds = service_account.Credentials.from_service_account_info(creds_dict, scopes=['https://www.googleapis.com/auth/indexing'])
        session = AuthorizedSession(creds)
        for url in url_list:
            session.post("https://indexing.googleapis.com/v3/urlNotifications:publish", json={"url": url, "type": "URL_UPDATED"})
    except Exception as e:
        send_telegram_msg(f"⚠️ Google Indexing Ping Failed: {str(e)[:100]}")

# ==========================================
# 🧠 AI CONTENT GENERATION SETUP
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
        try: posts_db = [p for p in json.load(f) if "img" in p]
        except: pass

todays_category = ["AI", "Trading", "Finance"][len(posts_db) % 3]
generated_urls = []
primary_url_for_tg = ""

def ask_ai(prompt, retries=3):
    for i in range(retries):
        current_key = API_KEYS[i % len(API_KEYS)]
        api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={current_key}"
        try:
            payload_data = {"contents": [{"parts": [{"text": prompt}]}], "safetySettings": [{"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"}, {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"}, {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"}, {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"}]}
            req = urllib.request.Request(api_url, data=json.dumps(payload_data).encode("utf-8"), headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=40) as response:
                text = json.loads(response.read().decode("utf-8"))['candidates'][0]['content']['parts'][0]['text'].strip()
                if len(text) > 50: return clean_ad_garbage(text)
        except Exception: time.sleep(8)
    return ""

languages = {
    "hindi": {"code": "hi", "prompt_lang": "Hindi (India) written in Devanagari script. Use VERY SIMPLE, everyday conversational words. Write with HUMAN EMOTION (Manavta) and empathy. Do NOT sound like an AI."},
    "english": {"code": "en", "prompt_lang": "Simple, conversational US English. Highly human-like, easy to understand."},
    "marathi": {"code": "mr", "prompt_lang": "Pure, simple conversational Marathi (Devanagari)."},
    "bengali": {"code": "bn", "prompt_lang": "Pure, simple conversational Bengali."},
    "tamil": {"code": "ta", "prompt_lang": "Pure, simple conversational Tamil."}
}

try:
    start_time = time.time()
    
    raw_topic = ask_ai(f"Tum ek expert ho. Aaj ki category '{todays_category}' hai. Mujhe {current_year} ke liye is par ek viral, attention-grabbing Hindi blog title do. Sirf Title likhna.")
    if not raw_topic: core_title = f"2026 Mein {todays_category} Se Lakho Kaise Kamaye"
    else: core_title = clean_ad_garbage(raw_topic.replace('"', '').replace("'", "").replace("*", "")).strip()

    for lang_name, lang_data in languages.items():
        time.sleep(3)
        current_topic = ask_ai(f"Translate this blog title to {lang_name}: '{core_title}'. ONLY give the translated title.")
        if not current_topic: current_topic = core_title

        intro_prompt = f"Topic: '{current_topic}'. Language: {lang_data['prompt_lang']}. Act as a caring mentor teaching a beginner. Write a DEEP, LONG, and HIGHLY VALUABLE Introduction (at least 300 words). Use a relatable real-life story. No robotic words. Make them feel understood. Then provide a Clickable TOC. Format for TOC: <div style='background: #fffafa; border-left: 5px solid #da251c; padding: 20px; border-radius: 8px; margin-bottom: 25px;'><h3 style='color: #da251c; margin-top: 0;'>📍 Is Article Mein Kya Hai:</h3><ul style='list-style:none; padding:0;'><li>👉 <a href='#basic'>1. Basic Samajh (Foundation)</a></li> <li>👉 <a href='#deep'>2. Deep Details & Setup</a></li> <li>👉 <a href='#pro'>3. Pro Level Hacks</a></li></ul></div>. Use HTML tags."
        chunk_1 = ask_ai(intro_prompt)
        
        time.sleep(8) 
        body_prompt = f"Topic: '{current_topic}'. Language: {lang_data['prompt_lang']}. Write the MAIN BODY. Make it EXTREMELY detailed, practical, and useful. Use simple words. Write 3 long sub-headings (<h2>) with id='basic', id='deep', id='pro'. After the first <h2> section, write [PHOTO]. After the second <h2> section, write [INTERNAL_LINK]. After the third <h2> section, write [PHOTO]. Use HTML format."
        chunk_2 = ask_ai(body_prompt)
        
        time.sleep(8) 
        outro_prompt = f"Topic: '{current_topic}'. Language: {lang_data['prompt_lang']}. Write a very emotional and motivational Conclusion. Then write 4 FAQs with detailed practical answers. Insert the tag [AFFILIATE] exactly 2 times randomly. Use HTML."
        chunk_3 = ask_ai(outro_prompt)

        blog_content = clean_ad_garbage((chunk_1 or "") + "\n" + (chunk_2 or "") + "\n" + (chunk_3 or "")) 

        if "[INTERNAL_LINK]" in blog_content and len(posts_db) > 1:
            random_post = random.choice(posts_db[1:6] if len(posts_db) > 5 else posts_db[1:])
            internal_html = f"<div style='background: #f0f8ff; border: 1px solid #cce7ff; padding: 15px; border-radius: 8px; margin: 25px 0; font-size: 16px;'><span style='font-size: 20px;'>💡</span> <strong>Bonus Tip:</strong> <a href='{random_post['file']}' style='color: #0066cc; text-decoration: underline; font-weight: bold;'>{random_post['title']}</a></div>"
            blog_content = blog_content.replace("[INTERNAL_LINK]", internal_html, 1)
        blog_content = blog_content.replace("[INTERNAL_LINK]", "")

        affiliate_offers = [
            {"title": "🚀 100X Growth Starts Here!", "desc": "Bina risk aaj hi shuruat karein best tools ke sath.", "btn": "👉 Free Account 👈", "link": "https://upstox.com/"}, 
            {"title": "🤖 Auto-Income Machine Set Karein!", "desc": "Top creators jo tools use karte hain, unhe try karein.", "btn": "👉 View Tools 👈", "link": "https://hostinger.in/"}
        ]
        for offer in affiliate_offers:
            if "[AFFILIATE]" in blog_content:
                blog_content = blog_content.replace("[AFFILIATE]", f"<div style='background: linear-gradient(135deg, #111, #da251c); color: white; padding: 35px 25px; border-radius: 12px; margin: 40px 0; text-align: center; box-shadow: 0 10px 30px rgba(218, 37, 28, 0.3);'><h3 style='color: #fff; margin-top: 0; font-size: 24px;'>{offer['title']}</h3><p style='font-size: 16px; margin-bottom: 25px;'>{offer['desc']}</p><a href='{offer['link']}' target='_blank' style='display: inline-block; background: #fff; color: #da251c; font-weight: bold; padding: 15px 35px; border-radius: 50px; text-decoration: none;'>{offer['btn']}</a></div>", 1)
        blog_content = blog_content.replace("[AFFILIATE]", "") 

        safe_topic = urllib.parse.quote(f"future {todays_category.lower()} technology")
        js_chain = f"this.onerror=null; this.src='https://picsum.photos/seed/{{SEED}}/800/400'; setTimeout(()=>{{if(this.naturalHeight<50) this.src='https://api.dicebear.com/7.x/shapes/svg?seed=shape{{SEED}}&backgroundColor=da251c'; setTimeout(()=>{{if(this.naturalHeight<50) this.src='https://image-charts.com/chart?chs=800x400&cht=p3&chd=t:100&chf=bg,s,111111'; setTimeout(()=>{{if(this.naturalHeight<50) this.src='https://dummyimage.com/800x400/111/fff&text=Digital+Kamai+Hub';}},1000);}},1000);}},1000);"

        for idx in range(3):
            if "[PHOTO]" in blog_content:
                seed_val = post_id + idx + (100 if lang_name != "hindi" else 0)
                api_primary = f"https://image.pollinations.ai/prompt/{safe_topic}?width=800&height=400&nologo=true&seed={seed_val}"
                current_js = js_chain.replace("{SEED}", str(seed_val))
                blog_content = blog_content.replace("[PHOTO]", f"<div style='text-align: center;'><img src='{api_primary}' onerror=\"{current_js}\" loading='lazy' style='width: 100%; min-height: 200px; border-radius: 12px; margin: 35px 0; box-shadow: 0 10px 30px rgba(0,0,0,0.15); object-fit: cover; background-color: #e2e8f0;'></div>", 1)

        main_seed = post_id + (50 if lang_name != "hindi" else 0)
        main_primary = f"https://image.pollinations.ai/prompt/{safe_topic}%204k%20masterpiece?width=1200&height=600&nologo=true&seed={main_seed}"
        main_js = js_chain.replace("{SEED}", str(main_seed))

        audio_filename = f"audio_{lang_data['code']}_{post_id}.mp3"
        clean_text = re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', ' ', blog_content))).replace("*", "").replace("#", "").strip()
        with open("temp.txt", "w", encoding="utf-8") as temp_f: temp_f.write(clean_text)
        voice = {"hindi": "hi-IN-SwaraNeural", "english": "en-US-AriaNeural", "marathi": "mr-IN-AarohiNeural", "bengali": "bn-IN-TanishaaNeural", "tamil": "ta-IN-PallaviNeural"}[lang_name]
        os.system(f"edge-tts -f temp.txt --voice {voice} --write-media {audio_filename}")

        post_filename = f"post_{lang_data['code']}_{post_id}.html"
        full_page_url = f"https://rameshchandra89056-bloger.github.io/AI-Autoblogger-Engine/{post_filename}"
        generated_urls.append(full_page_url)
        
        if lang_name == "hindi":
            primary_url_for_tg = full_page_url
            posts_db.insert(0, {"title": current_topic, "file": post_filename, "date": today_date, "img": main_primary, "fallback_js": main_js, "category": todays_category.lower()})

        # =======================================================
        # 🎨 THE BEAUTIFUL OLD UI + ONESIGNAL FRONTEND
        # =======================================================
        onesignal_script = """
        <script src="https://cdn.onesignal.com/sdks/web/v16/OneSignalSDK.page.js" defer></script>
        <script>
          window.OneSignalDeferred = window.OneSignalDeferred || [];
          OneSignalDeferred.push(function(OneSignal) {
            OneSignal.init({
              appId: "f11333ae-cc73-489e-a1a5-6a74129c3785",
              notifyButton: { enable: true, position: 'bottom-right', size: 'medium', showCredit: false }
            });
          });
        </script>
        """

        premium_css = """<style>
        :root{--main-red:#da251c;--dark-bg:#111;--text-gray:#444} html{scroll-behavior:smooth} *{box-sizing:border-box;margin:0;padding:0;font-family:'Segoe UI',Tahoma,sans-serif} body{background:#e9ecef;color:#111;line-height:1.7;overflow-x:hidden} .top-header{background:white;border-bottom:2px solid #eee;box-shadow:0 4px 10px rgba(0,0,0,0.05);position:sticky;top:0;z-index:1000} .nav-container{max-width:800px;margin:0 auto;padding:15px 20px;display:flex;justify-content:space-between;align-items:center} .logo{font-size:22px;font-weight:900;color:var(--main-red);text-decoration:none;text-transform:uppercase} .desktop-menu{display:flex;gap:20px} .desktop-menu a{text-decoration:none;color:#111;font-weight:600;font-size:14px;transition:color 0.3s} .desktop-menu a:hover{color:var(--main-red)} .container{max-width:700px;margin:20px auto;padding:0 15px} .article-box{background:white;padding:30px;border-radius:12px;box-shadow:0 5px 20px rgba(0,0,0,0.05)} #article-body{font-size:16px;color:var(--text-gray)} #article-body h2{color:#000;margin:30px 0 15px 0;border-left:5px solid var(--main-red);padding-left:15px;background:#fafafa;padding:10px 15px;border-radius:0 8px 8px 0;font-size:22px} #article-body h3{color:#333;margin:25px 0 10px 0;font-size:19px} #article-body p{margin-bottom:20px;line-height:1.8} .timeline{position:relative;max-width:700px;margin:40px auto} .timeline::after{content:'';position:absolute;width:4px;background:var(--main-red);top:0;bottom:0;left:20px;margin-left:-2px;border-radius:5px} .timeline-card{width:100%;padding:10px 0 10px 50px;position:relative;box-sizing:border-box} .timeline-card::after{content:'';position:absolute;width:16px;height:16px;left:10px;background-color:white;border:4px solid var(--main-red);top:25px;border-radius:50%;z-index:1} .timeline-content{padding:20px;background:white;border-radius:12px;box-shadow:0 4px 15px rgba(0,0,0,0.08);transition:transform 0.3s} .timeline-content img{display:block;width:100%;height:220px;object-fit:cover;margin-bottom:15px;background-color:#e2e8f0;border-radius:8px} footer{background:var(--dark-bg);color:#888;padding:40px 20px 30px;margin-top:50px;text-align:center;border-radius:12px 12px 0 0; max-width:800px; margin-left:auto; margin-right:auto;} .footer-links a{color:#ccc;text-decoration:none;margin:0 10px;font-size:14px} @media (max-width: 768px) { .desktop-menu { flex-wrap: wrap; justify-content: center; gap: 10px; margin-top: 10px; display: none; } .nav-container { flex-direction: column; } .menu-btn { display: block; width: 100%; text-align: center; background: #f9f9f9; padding: 10px; margin-top: 10px; cursor: pointer; font-weight: bold; color: var(--main-red); border-radius: 5px; } .menu-active { display: flex !important; flex-direction: column; width: 100%; } } .menu-btn { display: none; }
        </style>"""

        header_html = """<header class="top-header"><div class="nav-container"><a href="index.html" class="logo">Digital Kamai Hub</a><div class="menu-btn" onclick="document.getElementById('mobile-menu').classList.toggle('menu-active')">☰ MENU</div><div class="desktop-menu" id="mobile-menu"><a href="index.html">Home</a><a href="category_ai.html">AI Hacks</a><a href="category_trading.html">Trading</a><a href="category_finance.html">Finance</a><a href="all-posts.html">All Articles</a><a href="about.html">About</a><a href="contact.html">Contact</a></div></div></header>"""

        lang_switcher = f"""<div style="background:#f4f4f4; padding:12px; border-radius:8px; margin-bottom:25px; text-align:center; box-shadow:inset 0 2px 4px rgba(0,0,0,0.05); border:1px solid #ddd;"><span style="font-size:15px; font-weight:bold; color:#333; margin-right:10px;">🌍 Read In:</span><div style="display:inline-flex; flex-wrap:wrap; gap:8px; justify-content:center; margin-top:5px;"><a href="post_hi_{post_id}.html" style="background:white; padding:5px 12px; border-radius:20px; font-size:13px; font-weight:bold; color:var(--main-red); text-decoration:none; border:1px solid #ccc;">🇮🇳 Hindi</a><a href="post_en_{post_id}.html" style="background:white; padding:5px 12px; border-radius:20px; font-size:13px; font-weight:bold; color:#111; text-decoration:none; border:1px solid #ccc;">🇺🇸 English</a><a href="post_mr_{post_id}.html" style="background:white; padding:5px 12px; border-radius:20px; font-size:13px; font-weight:bold; color:#111; text-decoration:none; border:1px solid #ccc;">🚩 Marathi</a><a href="post_bn_{post_id}.html" style="background:white; padding:5px 12px; border-radius:20px; font-size:13px; font-weight:bold; color:#111; text-decoration:none; border:1px solid #ccc;">🟢 Bengali</a><a href="post_ta_{post_id}.html" style="background:white; padding:5px 12px; border-radius:20px; font-size:13px; font-weight:bold; color:#111; text-decoration:none; border:1px solid #ccc;">🔵 Tamil</a></div></div>"""

        footer_html = f"""<footer style="margin-top: 40px; background: #111; padding: 40px 20px; text-align: center;"><div style="margin-bottom: 25px;"><p style="color: #ccc; font-size: 14px; margin-bottom: 15px; font-weight: bold; letter-spacing: 1px;">JOIN THE AI MILLIONAIRE COMMUNITY:</p><div style="display: flex; justify-content: center; gap: 10px; flex-wrap: wrap;"><a href="https://www.youtube.com/@TheAIMillionaire-h5g" target="_blank" style="color: #FF0000; text-decoration: none; font-weight: bold; background: white; padding: 8px 12px; border-radius: 5px;">YouTube</a><a href="https://t.me/digitalkamaihub_2026" target="_blank" style="color: #0088cc; text-decoration: none; font-weight: bold; background: white; padding: 8px 12px; border-radius: 5px;">Telegram</a><a href="https://www.instagram.com/aimillionaire_official" target="_blank" style="color: #E1306C; text-decoration: none; font-weight: bold; background: white; padding: 8px 12px; border-radius: 5px;">Instagram</a><a href="https://www.facebook.com/profile.php?id=61566373760814" target="_blank" style="color: #1877F2; text-decoration: none; font-weight: bold; background: white; padding: 8px 12px; border-radius: 5px;">Facebook</a></div></div><div class="footer-links" style="margin-bottom: 20px;"><a href="about.html">About Us</a> | <a href="privacy.html">Privacy</a> | <a href="terms.html">Terms</a> | <a href="disclaimer.html">Disclaimer</a> | <a href="contact.html">Contact</a></div><p style="margin-top:20px; font-size:13px; color: #888;">&copy; {current_year} Digital Kamai Hub. All Rights Reserved.</p></footer><script src="https://pl31601171.profitableratecpmnetwork.com/1f/d8/5e/1fd85e18370bd0dd9187ebabdb13185f.js"></script>"""

        top_buttons_html = f"""<audio id="premium-audio" src="{audio_filename}"></audio><div style="display: flex; gap: 8px; margin-bottom: 25px;"><button id="audio-btn" onclick="toggleAudio()" style="flex: 2; background: #da251c; color: white; border: none; padding: 12px; border-radius: 5px; font-size: 14px; font-weight: bold; cursor: pointer;">▶️ Play Audio</button><button onclick="window.open('https://api.whatsapp.com/send?text=Digital Kamai Hub: ' + window.location.href, '_blank')" style="flex: 1; background: #25D366; color: white; border: none; padding: 12px; border-radius: 5px; font-size: 14px; font-weight: bold; cursor: pointer;">💬 Share</button></div>"""

        author_box_html = """<div style="background: #f9f9f9; padding: 20px; border-radius: 12px; margin-top: 40px; margin-bottom: 30px; box-shadow: 0 4px 15px rgba(0,0,0,0.05); display: flex; align-items: center; gap: 15px; border-left: 5px solid #da251c; flex-wrap: wrap;"><img src="https://api.dicebear.com/7.x/avataaars/svg?seed=Mohit&backgroundColor=da251c" loading="lazy" style="width: 75px; height: 75px; border-radius: 50%; border: 3px solid white; box-shadow: 0 2px 10px rgba(0,0,0,0.1);"><div style="flex: 1;"><h3 style="margin: 0; color: #111; font-size: 18px;">Mohit (The AI Millionaire)</h3><p style="margin: 5px 0 0 0; color: #555; font-size: 14px; line-height: 1.5;">Founder & Lead AI Automation Expert. Yahan main apne 2026 ke secret hacks share karta hoon. <strong>Smart work > Hard work.</strong></p></div></div>"""

        article_page = f"""<!DOCTYPE html><html lang="{lang_data['code']}"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"><title>{current_topic} - Digital Kamai Hub</title>{premium_css}{onesignal_script}</head><body><script>function toggleAudio() {{ var audio = document.getElementById("premium-audio"); var btn = document.getElementById("audio-btn"); if (audio.paused) {{ audio.play(); btn.innerHTML = "⏸ Pause Audio"; }} else {{ audio.pause(); btn.innerHTML = "▶️ Play Audio"; }} }}</script>{header_html}<div class="container"><div class="article-box">{lang_switcher}<h1 style="color: #111; font-size: 26px; margin-bottom: 15px; font-weight:900; line-height:1.3;">{current_topic}</h1><div style="color: #777; font-size: 13px; margin-bottom: 20px; border-bottom: 1px solid #eee; padding-bottom: 10px; font-weight: bold;">📅 {today_date} | {todays_category.upper()}</div>{top_buttons_html}<img src="{main_primary}" onerror="{main_js}" loading="lazy" style="width: 100%; min-height: 250px; border-radius: 12px; margin-bottom: 30px; box-shadow: 0 5px 20px rgba(0,0,0,0.1); object-fit: cover; background-color: #e2e8f0;"><div id="article-body">{blog_content}</div>{author_box_html}</div></div>{footer_html}</body></html>"""
        with open(post_filename, "w", encoding="utf-8") as f: f.write(article_page)

except Exception as e:
    send_telegram_msg(urllib.parse.quote(f"🔴 SYSTEM FAILED\n⚠️ {str(e)[:100]}"))
    sys.exit(1)

# Generate Timeline and Static Pages
with open("posts.json", "w", encoding="utf-8") as f: json.dump(posts_db, f, ensure_ascii=False, indent=4)

def generate_timeline(post_list):
    if not post_list: return "<p style='text-align: center; color: #888; margin-top: 30px;'>Abhi yahan koi article nahi hai.</p>"
    html_str = '<div class="timeline">'
    for p in post_list:
        img_src = p.get('img', 'https://dummyimage.com/800x400/111/fff&text=Digital+Kamai+Hub')
        fallback = p.get('fallback_js', "this.onerror=null; this.src='https://dummyimage.com/800x400/da251c/fff&text=Digital+Kamai+Hub';")
        html_str += f"<div class='timeline-card'><div class='timeline-content'><img src='{img_src}' onerror=\"{fallback}\"><p style='color: #888; font-size: 13px; font-weight: bold; margin-bottom: 5px;'>📅 {p['date']}</p><h3 style='margin-bottom: 10px; font-size: 19px; line-height: 1.4;'><a href='{p['file']}' style='color: #111; text-decoration: none;'>{p['title']}</a></h3><a href='{p['file']}' style='color: #da251c; font-weight: bold; text-decoration: none; font-size: 14px;'>Read More →</a></div></div>"
    html_str += '</div>'
    return html_str

def create_page(filename, title, post_list):
    with open(filename, "w", encoding="utf-8") as f: f.write(f"<!DOCTYPE html><html lang='hi'><head><meta charset='UTF-8'><meta name='viewport' content='width=device-width, initial-scale=1.0'><title>{title} - Digital Kamai Hub</title>{premium_css}{onesignal_script}</head><body>{header_html}<div class='container'><h1 style='text-align: center; margin-bottom: 20px; color: #da251c; font-size: 28px; font-weight: 900;'>{title}</h1>{generate_timeline(post_list)}</div>{footer_html}</body></html>")

create_page("index.html", "🔥 Latest Articles", posts_db[:10])
create_page("all-posts.html", "📚 Sabhi Articles", posts_db)
categorized = {'ai': [], 'trading': [], 'finance': []}
for p in posts_db: 
    cat = p.get('category', 'ai')
    if cat in categorized: categorized[cat].append(p)
create_page("category_ai.html", "🤖 AI Hacks", categorized['ai'])
create_page("category_trading.html", "📈 Trading", categorized['trading'])
create_page("category_finance.html", "💰 Finance", categorized['finance'])

static_pages = {
    "about": ("About Us", "<h2 style='color: var(--main-red);'>Hamari Kahani</h2><p>Digital Kamai Hub par aapka swagat hai. Yeh ek premium tech blog hai jahan 2026 ke best financial hacks share kiye jate hain. Founder: Mohit.</p>"),
    "contact": ("Contact Us", "<h2 style='color: var(--main-red);'>Sampark Karein</h2><p>Email: rameshchandra89056@gmail.com par hume mail karein ya hamare Telegram channel par join karein.</p>"),
    "privacy": ("Privacy Policy", "<h2 style='color: var(--main-red);'>Privacy Policy</h2><p>Humari website Google cookies aur third-party Adsterra ads ka upyog karti hai taaki aapko behtar anubhav mil sake.</p>"),
    "terms": ("Terms & Conditions", "<h2 style='color: var(--main-red);'>Terms</h2><p>Website par maujood samagri educational purpose ke liye hai. Ise copy karna mana hai.</p>"),
    "disclaimer": ("Disclaimer", "<h2 style='color: var(--main-red);'>Disclaimer</h2><p>Hum SEBI registered advisor nahi hain. Crypto aur trading mein jokhim hai, kripya apni research khud karein.</p>")
}
for p_file, (p_title, p_content) in static_pages.items():
    with open(f"{p_file}.html", "w", encoding="utf-8") as f: f.write(f"<!DOCTYPE html><html lang='hi'><head><meta charset='UTF-8'><meta name='viewport' content='width=device-width, initial-scale=1.0'><title>{p_title} - Digital Kamai Hub</title>{premium_css}{onesignal_script}</head><body>{header_html}<div class='container'><div class='article-box'>{p_content}</div></div>{footer_html}</body></html>")

# ==========================================
# 📢 FINAL PUSH & NOTIFICATIONS
# ==========================================
exec_time = round((time.time() - start_time) / 60, 2)
send_telegram_msg(urllib.parse.quote(f"🟢 MULTILINGUAL SYSTEM SUCCESS\n\n🎯 Category: {todays_category}\n⏱️ Time: {exec_time} mins\n✅ Adsterra, OneSignal, Google Indexing ACTIVE"))

if primary_url_for_tg:
    send_public_telegram_msg(core_title, primary_url_for_tg)
    send_onesignal_push(core_title, primary_url_for_tg)
    ping_google_indexing(generated_urls)
