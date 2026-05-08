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
        try: posts_db = [p for p in json.load(f) if "img" in p]
        except: pass

def ask_ai(prompt, retries=2):
    for i in range(retries):
        current_key = API_KEYS[i % len(API_KEYS)]
        api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={current_key}"
        try:
            payload_data = {
                "contents": [{"parts": [{"text": prompt}]}],
                "safetySettings": [
                    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
                    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
                    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
                    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"}
                ]
            }
            req = urllib.request.Request(api_url, data=json.dumps(payload_data).encode("utf-8"), headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=30) as response:
                text = json.loads(response.read().decode("utf-8"))['candidates'][0]['content']['parts'][0]['text'].strip()
                if len(text) > 10: return clean_ad_garbage(text)
        except urllib.error.HTTPError as e:
            print(f"⚠️ Google API HTTP Error: {e.code}")
            if e.code == 404 or e.code == 403:
                print("🔄 Switching to Gemini Pro...")
                api_url_pro = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={current_key}"
                try:
                    req_pro = urllib.request.Request(api_url_pro, data=json.dumps(payload_data).encode("utf-8"), headers={"Content-Type": "application/json"})
                    with urllib.request.urlopen(req_pro, timeout=30) as res_pro:
                        text_pro = json.loads(res_pro.read().decode("utf-8"))['candidates'][0]['content']['parts'][0]['text'].strip()
                        if len(text_pro) > 10: return clean_ad_garbage(text_pro)
                except Exception as e_pro: print(f"⚠️ Gemini Pro Error: {e_pro}")
            time.sleep(3)
        except Exception as e:
            print(f"⚠️ Google API Network Error: {e}")
            time.sleep(3)
    
    print("🔄 Switching to Pollinations Text API Backup...")
    try:
        poll_url = "https://text.pollinations.ai/"
        poll_payload = {
            "messages": [
                {"role": "system", "content": "Tum ek expert Hindi blogger aur storyteller ho. Sirf HTML code output do. markdown tags jaise ```html mat lagana."},
                {"role": "user", "content": prompt}
            ],
            "model": "openai"
        }
        res_poll = requests.post(poll_url, json=poll_payload, timeout=40)
        if res_poll.status_code == 200:
            text_poll = res_poll.text.strip()
            if len(text_poll) > 10: return clean_ad_garbage(text_poll)
    except Exception as e: print(f"⚠️ Pollinations Exception: {e}")
    
    return ""

def pre_warm_image(url):
    try: urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'}), timeout=10)
    except: pass

current_topic = ""
blog_content = ""
emergency_topics = ["2026 Mein AI Se Paise Kaise Kamaye", "Top 5 Share Market Tips", "Bina Investment Ke Online Business"]

try:
    start_time = time.time()
    print("🚀 Starting AI Bot...")
    
    raw_topic = ask_ai(f"Tum ek trend analyst ho. {current_year} mein 'Finance', 'Trading', ya 'AI se online kamai' par ek viral Hindi blog title do. Purane titles: {[p['title'] for p in posts_db[:3]]} se alag ho. Sirf mukhya Title likhna.")
    
    if not raw_topic: 
        current_topic = random.choice(emergency_topics)
    else: 
        current_topic = clean_ad_garbage(raw_topic.replace('"', '').replace("'", "").replace("*", "").replace("टाइटल:", "").replace("Title:", "")).strip()

    print(f"🎯 Topic: {current_topic}")

    print("⏳ Chunk 1 generating...")
    intro_prompt = f"Topic: '{current_topic}'. Tum ek expert Hindi blogger aur storyteller ho. Niyam 1: Kitabi bhasha ka bilkul prayog mat karna. Niyam 2: Shuruaat ek bohot hi chhoti aur dilchasp kahani (short story) ya kisi aam insaan ke real-life example se karo. Niyam 3: Dost ki tarah asaan bhasha mein samjhao. Uske baad ek TOC (Table of Contents) likho. Template for TOC: <div style='background: #fffafa; border-left: 5px solid #da251c; padding: 20px; border-radius: 8px; margin-bottom: 25px;'><h3 style='color: #da251c; margin-top: 0;'>📍 Is Article Mein Kya Hai:</h3><ul><li>👉 Point 1</li><li>👉 Point 2</li></ul></div>. Sirf HTML code do (<h2>, <p>). Conclusion mat likhna. Markdown tags (```html) mat lagana."
    chunk_1 = ask_ai(intro_prompt, retries=2)
    
    print("⏳ Chunk 2 generating...")
    body_prompt = f"Topic: '{current_topic}'. Ab article ki main body likho. 2 detailed sub-headings (<h2>) aur paragraphs (<p>). Niyam 1: Kitabi bhasha ka bilkul prayog mat karna. Aise samjhao jaise tum ek expert dost ho. Har point ke sath ek chota udaharan (example) zaroor do. Niyam 2: Har section ke baad exactly 1 baar [PHOTO] tag likho (kul 2 [PHOTO] tags hone chahiye). Sirf HTML code do. Markdown tags mat lagana."
    chunk_2 = ask_ai(body_prompt, retries=2)
    
    print("⏳ Chunk 3 generating...")
    conclusion_prompt = f"Topic: '{current_topic}'. Ab ek strong aur friendly Conclusion aur 3 FAQ likho. Niyam 1: Pura HTML format. Niyam 2: Beech mein exactly 2 baar [AFFILIATE] tag likho. Markdown tags mat lagana."
    chunk_3 = ask_ai(conclusion_prompt, retries=2)

    if not (chunk_1 and chunk_2 and chunk_3):
        raise Exception("API Timeout: Chunking fail ho gayi aur saare Backup plans bhi jawab de gaye.")

    raw_content = chunk_1 + "\n" + chunk_2 + "\n" + chunk_3
    blog_content = raw_content.replace("```html", "").replace("```", "").strip()
    
    end_time = time.time()
    exec_time = round((end_time - start_time) / 60, 2)
    send_telegram_msg(urllib.parse.quote(f"🟢 SYSTEM RUN SUCCESS\n\n📝 Topic: {current_topic}\n⏱️ Time: {exec_time} Mins\n✅ Status: AI Chunks Merged Successfully"))

except Exception as e:
    send_telegram_msg(urllib.parse.quote(f"🔴 SYSTEM RUN FAILED\n\n⚠️ Error: {str(e)[:150]}"))
    sys.exit(1)

# --- BACKEND LOGIC (Photos, Audio, Website generation) ---
affiliate_offers = [{"title": "🚀 Aaj hi apni 100X kamai shuru karein!", "desc": "AI aur smart trading ki duniya mein kadam rakhne ke liye pramanit platform.", "btn": "👉 Yahan Free Account Banayein 👈", "link": "#"}, {"title": "🤖 2026 mein apni kamai ko 10X karein!", "desc": "The AI Millionaire ki exclusive community se judein.", "btn": "👉 Community Join Karein 👈", "link": "#"}]
for offer in affiliate_offers:
    if "[AFFILIATE]" in blog_content:
        blog_content = blog_content.replace("[AFFILIATE]", f"<div style='background: linear-gradient(135deg, #111, #da251c); color: white; padding: 35px 25px; border-radius: 12px; margin: 40px 0; text-align: center; box-shadow: 0 10px 30px rgba(218, 37, 28, 0.3);'><h3 style='color: #fff; margin-top: 0; font-size: 24px;'>{offer['title']}</h3><p style='font-size: 16px; margin-bottom: 25px;'>{offer['desc']}</p><a href='{offer['link']}' target='_blank' style='display: inline-block; background: #fff; color: #da251c; font-weight: bold; padding: 15px 35px; border-radius: 50px; text-decoration: none;'>{offer['btn']}</a></div>", 1)
blog_content = blog_content.replace("[AFFILIATE]", "") 

safe_img_base = "future finance trading wealth technology"
for idx, mod in enumerate(["cinematic", "cyberpunk", "hyperrealistic"]):
    if "[PHOTO]" in blog_content:
        inner_img_url = f"https://image.pollinations.ai/prompt/{urllib.parse.quote(f'{safe_img_base} {mod}')}?width=800&height=400&nologo=true&seed={post_id + idx + 1}"
        pre_warm_image(inner_img_url)
        blog_content = blog_content.replace("[PHOTO]", f"<div style='text-align: center;'><img src='{inner_img_url}' onerror=\"this.onerror=null; this.src='https://placehold.co/800x400/c00000/ffffff?text=AI+Finance';\" style='width: 100%; border-radius: 12px; margin: 35px 0; box-shadow: 0 10px 30px rgba(0,0,0,0.15); object-fit: cover;'></div>", 1)

main_img_url = f"https://image.pollinations.ai/prompt/{urllib.parse.quote(f'{safe_img_base} masterpiece')}?width=1200&height=600&nologo=true&seed={post_id}"
pre_warm_image(main_img_url)

audio_filename = f"audio_{post_id}.mp3"
clean_text = re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', ' ', blog_content))).replace("*", "").replace("#", "").strip()
with open("temp.txt", "w", encoding="utf-8") as temp_f: temp_f.write(clean_text)
os.system("pip install edge-tts > /dev/null 2>&1")
os.system(f"edge-tts -f temp.txt --voice hi-IN-SwaraNeural --write-media {audio_filename}")

post_filename = f"post_{post_id}.html"
posts_db.insert(0, {"title": current_topic, "file": post_filename, "date": today_date, "img": main_img_url})
with open("posts.json", "w", encoding="utf-8") as f: json.dump(posts_db, f, ensure_ascii=False, indent=4)

premium_css = """<style>:root { --main-red: #da251c; --dark-bg: #111; --text-gray: #444; } * { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Segoe UI', Tahoma, sans-serif; } body { background: #f0f2f5; color: #111; line-height: 1.7; overflow-x: hidden; } header { background: white; border-bottom: 2px solid #eee; box-shadow: 0 4px 10px rgba(0,0,0,0.05); position: sticky; top: 0; z-index: 1000; } .nav-container { max-width: 1200px; margin: 0 auto; padding: 15px 20px; display: flex; justify-content: space-between; align-items: center; position: relative; } .logo { font-size: 26px; font-weight: 900; color: var(--main-red); text-decoration: none; text-transform: uppercase; } .nav-links { display: flex; align-items: center; } .nav-links a { margin-left: 20px; text-decoration: none; color: #111; font-weight: bold; font-size: 16px; transition: 0.3s; } .nav-links a:hover { color: var(--main-red); } .menu-btn { display: none; font-size: 30px; cursor: pointer; color: var(--main-red); font-weight: bold; user-select: none; } .container { max-width: 900px; margin: 40px auto; padding: 0 20px; } .article-box { background: white; padding: 40px; border-radius: 12px; box-shadow: 0 5px 20px rgba(0,0,0,0.05); } #article-body { font-size: 20px; color: var(--text-gray); } #article-body h2 { color: #000; margin: 35px 0 15px 0; border-left: 5px solid var(--main-red); padding-left: 15px; background: #fafafa; padding: 10px 15px; border-radius: 0 8px 8px 0; } .timeline { position: relative; max-width: 900px; margin: 40px auto; } .timeline::after { content: ''; position: absolute; width: 4px; background: var(--main-red); top: 0; bottom: 0; left: 50%; margin-left: -2px; border-radius: 5px; } .timeline-card { padding: 10px 40px; position: relative; background: inherit; width: 50%; box-sizing: border-box; } .timeline-card.left { left: 0; } .timeline-card.right { left: 50%; } .timeline-card::after { content: ''; position: absolute; width: 22px; height: 22px; right: -11px; background-color: white; border: 4px solid var(--main-red); top: 20px; border-radius: 50%; z-index: 1; } .timeline-card.right::after { left: -11px; } .timeline-content { padding: 20px; background: white; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.08); transition: transform 0.3s; } .timeline-content:hover { transform: translateY(-5px); } .timeline-content img { width: 100%; border-radius: 8px; height: 180px; object-fit: cover; margin-bottom: 15px; } footer { background: var(--dark-bg); color: #888; padding: 60px 20px 30px; margin-top: 60px; text-align: center; } .footer-links a { color: #ccc; text-decoration: none; margin: 0 10px; font-size: 14px; } @media (max-width: 768px) { .article-box { padding: 20px; } h1 { font-size: 24px !important; } #article-body { font-size: 16px; } .menu-btn { display: block; } .nav-links { display: none; flex-direction: column; position: absolute; top: 100%; left: 0; width: 100%; background: #ffffff; box-shadow: 0 10px 30px rgba(0,0,0,0.15); border-top: 2px solid var(--main-red); z-index: 1001; padding: 10px 0; } .nav-links.active { display: flex !important; } .nav-links a { margin: 0; padding: 15px 25px; border-bottom: 1px solid #f0f0f0; width: 100%; text-align: left; font-size: 18px; } .timeline::after { left: 20px; } .timeline-card { width: 100%; padding-left: 50px; padding-right: 0; } .timeline-card.right { left: 0; } .timeline-card::after, .timeline-card.right::after { left: 10px; right: auto; width: 16px; height: 16px; top: 25px; } .timeline-content { padding: 15px; } .timeline-content img { height: 120px; } } .ticker-wrap { width: 100%; overflow: hidden; background-color: #f1f1f1; border-bottom: 2px solid #C00000; box-sizing: border-box; } .ticker-content { display: flex; white-space: nowrap; animation: tickerAnimation 15s linear infinite; color: #333; font-family: sans-serif; font-size: 14px; font-weight: bold; padding: 10px 0; } .ticker-content span { color: #C00000; } @keyframes tickerAnimation { 0% { transform: translateX(100%); } 100% { transform: translateX(-100%); } }</style><script src="https://cdn.onesignal.com/sdks/web/v16/OneSignalSDK.page.js" defer></script><script>window.OneSignalDeferred = window.OneSignalDeferred || []; OneSignalDeferred.push(async function(OneSignal) { await OneSignal.init({ appId: "f11333ae-cc73-489e-a1a5-6a74129c3785", notifyButton: { enable: true } }); });</script>"""
schema_markup = f"""<script type="application/ld+json">{{ "@context": "https://schema.org", "@type": "Article", "headline": "{current_topic}", "image": "{main_img_url}", "author": {{ "@type": "Person", "name": "Mohit (The AI Millionaire)" }}, "publisher": {{ "@type": "Organization", "name": "Digital Kamai Hub" }}, "datePublished": "{today_date}" }}</script>"""
header_html = """<div class="ticker-wrap"><div class="ticker-content"><span>TRENDING:</span> &nbsp; 2026 Best Tech, AI Income, Future Jobs, Digital Kamai Hub Ke Naye Hacks, Share Market Ka Sach!</div></div><header><div class="nav-container"><a href="index.html" class="logo">Digital Kamai Hub</a><div class="menu-btn" onclick="document.getElementById('mobile-menu').classList.toggle('active')">&#9776;</div><div class="nav-links" id="mobile-menu"><a href="index.html">Home</a><a href="category_ai.html">AI Hacks</a><a href="category_trading.html">Trading</a><a href="category_finance.html">Finance</a><a href="about.html">About</a><a href="contact.html">Contact</a></div></div></header>"""
footer_html = f"""<footer style="margin-top: 40px; background: #111; padding: 40px 20px; text-align: center;"><div style="margin-bottom: 25px;"><p style="color: #ccc; font-size: 14px; margin-bottom: 15px; font-weight: bold; letter-spacing: 1px;">JOIN THE AI MILLIONAIRE COMMUNITY:</p><div style="display: flex; justify-content: center; gap: 20px; flex-wrap: wrap;"><a href="https://www.youtube.com/@TheAIMillionaire-h5g" target="_blank" style="color: #FF0000; text-decoration: none; font-weight: bold; background: white; padding: 8px 15px; border-radius: 5px;">YouTube</a><a href="https://t.me/digitalkamaihub_2026" target="_blank" style="color: #0088cc; text-decoration: none; font-weight: bold; background: white; padding: 8px 15px; border-radius: 5px;">Telegram</a><a href="https://www.instagram.com/aimillionaire_official" target="_blank" style="color: #E1306C; text-decoration: none; font-weight: bold; background: white; padding: 8px 15px; border-radius: 5px;">Instagram</a></div></div><div class="footer-links" style="margin-bottom: 20px;"><a href="about.html">About Us</a> | <a href="privacy.html">Privacy Policy</a> | <a href="terms.html">Terms</a> | <a href="disclaimer.html">Disclaimer</a> | <a href="contact.html">Contact</a></div><p style="margin-top:20px; font-size:13px; color: #888;">&copy; {current_year} Digital Kamai Hub. All Rights Reserved.</p></footer>"""

# --- UI FIX: CHHOTE STATIC BUTTONS (NO FLOATING) ---
top_buttons_html = f"""
<audio id="premium-audio" src="{audio_filename}"></audio>
<div style="display: flex; gap: 10px; margin-bottom: 20px;">
    <button id="audio-btn" onclick="toggleAudio()" style="flex: 2; background: #da251c; color: white; border: none; padding: 10px; border-radius: 5px; font-size: 14px; font-weight: bold; cursor: pointer;">▶️ Sunne Ke Liye Click Karein</button>
    <button onclick="window.open('https://api.whatsapp.com/send?text=Digital Kamai Hub: ' + window.location.href, '_blank')" style="flex: 1; background: #25D366; color: white; border: none; padding: 10px; border-radius: 5px; font-size: 14px; font-weight: bold; cursor: pointer;">💬 WhatsApp</button>
    <button onclick="window.open('https://t.me/share/url?url=' + window.location.href + '&text=Digital Kamai Hub!', '_blank')" style="flex: 1; background: #0088cc; color: white; border: none; padding: 10px; border-radius: 5px; font-size: 14px; font-weight: bold; cursor: pointer;">✈️ Telegram</button>
</div>
"""

article_page = f"""<!DOCTYPE html><html lang="hi"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"><title>{current_topic} - Digital Kamai Hub</title>{premium_css}{schema_markup}</head><body><div style="position: fixed; top: 0; left: 0; width: 100%; height: 5px; background-color: transparent; z-index: 9999;"><div id="smart-progress" style="height: 5px; background-color: #da251c; width: 0%; border-top-right-radius: 3px; border-bottom-right-radius: 3px;"></div></div><script>window.addEventListener('scroll', function() {{ var winScroll = document.body.scrollTop || document.documentElement.scrollTop; var height = document.documentElement.scrollHeight - document.documentElement.clientHeight; var scrolled = (winScroll / height) * 100; document.getElementById("smart-progress").style.width = scrolled + "%"; }}); function toggleAudio() {{ var audio = document.getElementById("premium-audio"); var btn = document.getElementById("audio-btn"); if (audio.paused) {{ audio.play(); btn.innerHTML = "⏸️ Pause Audio"; }} else {{ audio.pause(); btn.innerHTML = "▶️ Play Audio"; }} }}</script>{header_html}<div class="container"><div class="article-box"><h1 style="color: #111; margin-bottom: 15px;">{current_topic}</h1><div style="color: #666; font-size: 14px; margin-bottom: 15px; border-bottom: 1px solid #eee; padding-bottom: 10px; font-weight: bold;">Date: {today_date} | Author: Mohit (The AI Millionaire)</div>{top_buttons_html}<img src="{main_img_url}" onerror="this.onerror=null; this.src='https://placehold.co/1200x600/da251c/ffffff?text=Digital+Kamai+Hub';" style="width: 100%; border-radius: 10px; margin-bottom: 25px; box-shadow: 0 5px 15px rgba(0,0,0,0.1); object-fit: cover;"><div id="article-body">{blog_content}</div><div style="background: linear-gradient(135deg, #f9f9f9, #ffffff); padding: 30px; border-radius: 12px; border: 2px dashed #da251c; margin-top: 40px; text-align: center; box-shadow: 0 10px 30px rgba(218, 37, 28, 0.1);"><h3 style="color: #111; font-size: 22px; margin-top: 0; margin-bottom: 10px;">🔥 2026 ke Secret Hacks Seedhe Inbox Mein!</h3><p style="color: #555; font-size: 16px; margin-bottom: 20px;">'The AI Millionaire' ki VIP list join karein aur rozana 10X kamai ke naye tarike seekhein (Free).</p><form action="https://formsubmit.co/rameshchandra89056@gmail.com" method="POST" style="display: flex; gap: 10px; max-width: 500px; margin: 0 auto; flex-wrap: wrap; justify-content: center;"><input type="text" name="_honey" style="display:none"><input type="hidden" name="_captcha" value="false"><input type="email" name="email" placeholder="Apna Email likhein..." required style="flex: 1; padding: 12px; border: 1px solid #ccc; border-radius: 8px; font-size: 16px; min-width: 200px;"><button type="submit" style="background: #111; color: white; border: none; padding: 12px 25px; font-weight: bold; border-radius: 8px; font-size: 16px; cursor: pointer;">Join Now 🚀</button></form></div></div></div>{footer_html}</body></html>"""
with open(post_filename, "w", encoding="utf-8") as f: f.write(article_page)

def get_category(title):
    t = title.lower()
    if any(w in t for w in ['ai', 'chatgpt', 'bot', 'artificial intelligence', 'tech', 'automation']): return 'ai'
    if any(w in t for w in ['trade', 'trading', 'share', 'stock', 'market', 'crypto', 'nifty', 'option']): return 'trading'
    if any(w in t for w in ['finance', 'paisa', 'kamai', 'wealth', 'amir', 'money', 'income', 'bank']): return 'finance'
    return 'trending'

categorized_posts = {'ai': [], 'trading': [], 'finance': [], 'trending': []}
for p in posts_db: categorized_posts[get_category(p['title'])].append(p); categorized_posts['trending'].append(p)

def generate_timeline(post_list):
    if not post_list: return "<p style='text-align: center; color: #888; margin-top: 30px;'>Abhi yahan koi article nahi hai. Naye updates ka intezaar karein!</p>"
    html_str = '<div class="timeline">'
    for i, p in enumerate(post_list):
        side = "left" if i % 2 == 0 else "right"
        html_str += f"<div class='timeline-card {side}'><div class='timeline-content'><img src='{p['img']}' onerror=\"this.onerror=null; this.src='https://placehold.co/800x400/111/fff?text=Digital+Kamai+Hub';\"><p style='color: #888; font-size: 13px; font-weight: bold; margin-bottom: 5px;'>📅 {p['date']}</p><h3 style='margin-bottom: 10px; font-size: 18px; line-height: 1.4;'><a href='{p['file']}' style='color: #111; text-decoration: none;'>{p['title']}</a></h3><a href='{p['file']}' style='color: #da251c; font-weight: bold; text-decoration: none; font-size: 14px;'>Read More →</a></div></div>"
    return html_str + '</div>'

def create_page(filename, title, post_list):
    with open(filename, "w", encoding="utf-8") as f: f.write(f"<!DOCTYPE html><html lang='hi'><head><meta charset='UTF-8'><meta name='viewport' content='width=device-width, initial-scale=1.0'><title>{title} - Digital Kamai Hub</title>{premium_css}</head><body>{header_html}<div class='container'><h1 style='text-align: center; margin-bottom: 10px; color: #da251c; font-size: 32px; font-weight: 900;'>{title}</h1>{generate_timeline(post_list)}</div>{footer_html}</body></html>")

create_page("index.html", "🔥 Latest Trending Articles", posts_db[:10])
create_page("category_ai.html", "🤖 AI & Tech Hacks", categorized_posts['ai'])
create_page("category_trading.html", "📈 Share Market & Trading", categorized_posts['trading'])
create_page("category_finance.html", "💰 Finance & Wealth", categorized_posts['finance'])
create_page("all-posts.html", "📚 Sabhi Articles (Archive)", posts_db)

pages = {
    "about": ("About Us", "<h2 style='color: var(--main-red); margin-bottom: 15px; font-size: 28px;'>Hamari Kahani (Our Story)</h2><p style='font-size: 18px; margin-bottom: 25px; color: #333;'>Namaste! <strong>Digital Kamai Hub</strong> mein aapka swagat hai. Yeh sirf ek blog nahi, balki ek digital revolution hai.</p><h2 style='color: var(--main-red); margin-bottom: 15px; font-size: 24px;'>🎯 Mission & Vision</h2><p style='font-size: 18px; margin-bottom: 25px; color: #333;'>Hamara mission bilkul saaf hai: <strong>\"Bacchon ka khel nahi, Smart Work!\"</strong></p><h2 style='color: var(--main-red); margin-bottom: 15px; font-size: 24px;'>👨‍💻 Meet The Founder: Mohit (The AI Millionaire)</h2><div style='background: #fafafa; padding: 25px; border-left: 5px solid var(--main-red); border-radius: 8px; margin-bottom: 30px;'><p style='font-size: 17px; margin-bottom: 15px; color: #222;'>Mohit ek <strong>Full-Stack Web Developer aur Visionary Entrepreneur</strong> hain. Any manual task is a bug.</p></div>"),
    "privacy": ("Privacy Policy", "<h2 style='color: var(--main-red); margin-bottom: 15px; font-size: 28px;'>Privacy Policy</h2><p style='font-size: 18px; margin-bottom: 15px; color: #333;'>Aapki privacy hamare liye sabse zyada zaroori hai. Digital Kamai Hub par hum aapka data kaise use karte hain:</p><ul><li style='margin-bottom: 10px;'><strong>Cookies:</strong> Hum website ka experience behtar banane aur Google AdSense ke ads dikhane ke liye cookies ka istemal karte hain.</li><li style='margin-bottom: 10px;'><strong>Data Security:</strong> Hum aapki email ya personal jankari kisi third-party ko nahi bechte.</li></ul>"),
    "terms": ("Terms & Conditions", "<h2 style='color: var(--main-red); margin-bottom: 15px; font-size: 28px;'>Terms and Conditions</h2><p style='font-size: 18px; margin-bottom: 15px; color: #333;'>Is website ka istemal karke aap hamari in sharton ko mante hain:</p><ul><li style='margin-bottom: 10px;'><strong>Samagri (Content):</strong> Is website ka content sirf shikhsha ke liye hai. Ise copy karke kahin aur bechna mana hai.</li><li style='margin-bottom: 10px;'><strong>Zimmewari:</strong> Hum kisi bhi aarthik nuksan ke liye zimmewar nahi hain.</li></ul>"),
    "disclaimer": ("Disclaimer", "<h2 style='color: var(--main-red); margin-bottom: 15px; font-size: 28px;'>Disclaimer (Chetawani)</h2><p style='font-size: 18px; margin-bottom: 15px; color: #333;'><strong>Digital Kamai Hub</strong> par di gayi sabhi jankari (Finance, Share Market, AI Tools) keval shikhsha ke liye hai.</p><ul><li style='margin-bottom: 10px;'><strong>Financial Advice Nahi:</strong> Hum SEBI registered financial advisor nahi hain.</li><li style='margin-bottom: 10px;'><strong>Risk (Jokhim):</strong> Trading aur investment mein jokhim hota hai.</li></ul>"),
    "contact": ("Contact Us", """<div style="text-align: center;"><h1 style="color: #da251c; font-size: 32px; font-weight: bold; margin-bottom: 10px;">Contact Us</h1><p style="margin-bottom: 30px; font-size: 18px; color: #555;">Humse sampark karein! Apne sawal ya inquiry form ke madhyam se bhejein.</p><div id="form-container" style="max-width: 550px; margin: 0 auto; text-align: left; background: #fff; padding: 30px; border-radius: 12px; box-shadow: 0 5px 15px rgba(0,0,0,0.1); border-top: 5px solid #da251c;"><form action="https://formsubmit.co/rameshchandra89056@gmail.com" method="POST"><input type="text" name="_honey" style="display:none"><input type="hidden" name="_captcha" value="false"><input type="text" name="name" placeholder="Aapka Naam" required style="width: 100%; padding: 15px; margin-bottom: 15px; border: 1px solid #ccc; border-radius: 8px; font-size: 16px;"><input type="email" name="email" placeholder="Aapka Email" required style="width: 100%; padding: 15px; margin-bottom: 15px; border: 1px solid #ccc; border-radius: 8px; font-size: 16px;"><textarea name="message" rows="5" placeholder="Apna Sandesh (Message) likhein..." required style="width: 100%; padding: 15px; margin-bottom: 20px; border: 1px solid #ccc; border-radius: 8px; font-size: 16px;"></textarea><button type="submit" style="width: 100%; background: #da251c; color: white; padding: 15px; font-weight: bold; font-size: 18px; border: none; border-radius: 8px; cursor: pointer;">Bhejein (Send Message)</button></form></div></div>""")
}

for p_file, (p_title, p_content) in pages.items():
    with open(f"{p_file}.html", "w", encoding="utf-8") as f: f.write(f"<!DOCTYPE html><html lang='hi'><head><meta charset='UTF-8'><meta name='viewport' content='width=device-width, initial-scale=1.0'><title>{p_title} - Digital Kamai Hub</title>{premium_css}</head><body>{header_html}<div class='container'><div class='article-box'>{p_content}</div></div>{footer_html}</body></html>")

try:
    sitemap_content = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    for file in [f for f in os.listdir() if f.endswith('.html')]: sitemap_content += f'  <url>\n    <loc>https://rameshchandra89056-bloger.github.io/AI-Autoblogger-Engine/{file}</loc>\n    <lastmod>{datetime.now().strftime("%Y-%m-%d")}</lastmod>\n    <changefreq>daily</changefreq>\n  </url>\n'
    with open('sitemap.xml', 'w', encoding='utf-8') as f: f.write(sitemap_content + '</urlset>')
except: pass

blog_url = f"https://rameshchandra89056-bloger.github.io/AI-Autoblogger-Engine/{post_filename}"
send_telegram_msg(urllib.parse.quote(f"✅ FINAL SUCCESS: Naya Clean Blog live!\n📝 Kul Post: {len(posts_db)}\n🌐 Link: {blog_url}"))
if os.environ.get("TELEGRAM_PUBLIC_CHANNEL"): send_telegram_msg(urllib.parse.quote(f"🚀 Nayi post live ho gayi hai!\n\n🔥 Topic: {current_topic}\n\n👉 Padhein: {blog_url}"), target_chat_id=os.environ.get("TELEGRAM_PUBLIC_CHANNEL"))
send_push_notification(current_topic, blog_url)
print("✅ Website 100% safalta ke sath ban gayi hai!")
