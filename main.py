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

# 🔔 ONESIGNAL AUTO-NOTIFICATION ROBOT (REST API)
def send_push_notification(title, post_url):
    app_id = "f11333ae-cc73-489e-a1a5-6a74129c3785"
    api_key = os.environ.get("ONESIGNAL_API_KEY")
    if not api_key:
        print("⚠️ API Key missing! Notification nahi gaya.")
        return
    header = {
        "Content-Type": "application/json; charset=utf-8",
        "Authorization": f"Basic {api_key}"
    }
    payload = {
        "app_id": app_id,
        "included_segments": ["All"],
        "contents": {"en": f"Nayi Post: {title}"},
        "headings": {"en": "Digital Kamai Hub: Taaza Khabar!"},
        "url": post_url
    }
    try:
        response = requests.post("https://onesignal.com/api/v1/notifications", headers=header, json=payload)
        if response.status_code == 200:
            print("✅ OneSignal SUCCESS!")
    except Exception as e:
        print(f"❌ Notification Robot Failed: {e}")

# ==========================================
def send_telegram_msg(message, target_chat_id=None):
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat_id = target_chat_id if target_chat_id else os.environ.get("TELEGRAM_CHAT_ID")
    if not token or not chat_id: return
    try:
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        params = {"chat_id": chat_id, "text": urllib.parse.unquote(message)}
        requests.get(url, params=params, timeout=10)
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
        try:
            raw_db = json.load(f)
            posts_db = [p for p in raw_db if "img" in p]
        except: pass

available_model = "models/gemini-1.5-flash"
try:
    req = urllib.request.Request(f"https://generativelanguage.googleapis.com/v1beta/models?key={API_KEYS[0]}")
    with urllib.request.urlopen(req, timeout=15) as response:
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
    headers = {"Authorization": f"Bearer {hf_key}", "Content-Type": "application/json"}
    payload = {"inputs": f"System: You are an expert AI and Finance blogger.\nUser: {prompt}", "parameters": {"max_new_tokens": 1500, "return_full_text": False}}
    try:
        hf_res = requests.post(hf_url, headers=headers, json=payload, timeout=60)
        if hf_res.status_code == 200: return hf_res.json()[0].get('generated_text', '').strip()
    except: pass
    return ""

def pre_warm_image(url):
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        urllib.request.urlopen(req, timeout=10)
    except: pass

# ==========================================
# 🚨 MAIN EXECUTION BLOCK (NO EMPTY LINES ALLOWED INSIDE)
# ==========================================
try:
    topic_prompt = f"Tum ek trend analyst ho. {current_year} mein 'Finance', 'Trading', 'Stock Market', ya 'AI se online kamai' par ek bahut hi high-paying aur viral Hindi blog title do. Purane titles: {[p['title'] for p in posts_db[:5]]} se alag ho. Sirf mukhya Title likhna. 'Title:', 'Title {current_year}:' ya aise koi bhi faltu shabd aage mat lagana."
    raw_topic = ask_ai(topic_prompt)
    current_topic = raw_topic.replace('"', '').replace("'", "").replace("*", "").replace("टाइटल:", "").replace("Title:", "").replace(f"Title {current_year}:", "").replace("Title", "").strip()
    if not current_topic: 
        sys.exit(1)
    #
    html_prompt = f"Tum ek expert lekin bahut friendly teacher ho. Tumhe niche diye gaye topic par ek blog post likhni hai. Vishay: '{current_topic}'। Kam se kam 1000 shabdon ka ek bahut hi vistar se likha gaya shandar Hindi blog post likho. Niyam: 1. Post ke beech-beech mein 4 alag-alag jagah bilkul aise hi likh do: [PHOTO] 2. Post ke beech mein theek 2 alag-alag jagah (jahan paisa kamane ya tool ka jikra ho) bilkul aise hi likh do: [AFFILIATE] 3. Post mein ek 'Real Life Case Study' (udaharan) aur ek 'Step-by-Step Guide' jarur shamil karein. 4. Ant mein ek damdar 'Nishkarsh', aur yeh 'Chetawani (Disclaimer)' jarur likhein. 5. Mukhya title (Heading) dobara mat likhna, seedha introduction se shuru karna. 6. Sirf HTML code (h2, p, strong, ul) dein. 7. Bhasha bilkul aam insani honi chahiye, jaise gaon ya dosto ke beech baat hoti hai. 8. Koi bhi robotic ya kitabi shabd bilkul use nahi karna hai. 9. User ko ZERO knowledge se lekar 100% knowledge tak le jana hai. 10. Har badi baat ko samjhane ke liye aam jindagi (Real-life) ke asaan udaharan (Examples) dene hain. 11. Post ko padhkar user ko lagna chahiye ki koi bada bhai use asaan bhasha mein samjha raha hai. 12. CRITICAL HTML TEMPLATE RULE: Tumhe 'Table of Contents' ke liye apna koi dimag nahi lagana hai aur koi markdown (- ya *) use nahi karna hai. Tumhe EXACTLY niche diya gaya HTML template copy karna hai aur uske andar apne points fill karne hain. Iske bahar ek bhi point nahi likhna hai! TEMPLATE TO COPY: <div style='background: #fffafa; border-left: 5px solid #da251c; padding: 20px; border-radius: 8px; margin-bottom: 25px; box-shadow: 0 4px 10px rgba(0,0,0,0.05);'><h3 style='color: #da251c; margin-top: 0; font-size: 20px;'>📍 Is Article Mein Kya Hai:</h3><ul style='list-style-type: none; padding-left: 0; margin: 0; font-size: 18px;'><li style='margin-bottom: 10px; font-weight: bold; color: #333;'>👉 [Point 1 yahan likho]</li><li style='margin-bottom: 10px; font-weight: bold; color: #333;'>👉 [Point 2 yahan likho]</li><li style='margin-bottom: 10px; font-weight: bold; color: #333;'>👉 [Point 3 yahan likho]</li></ul></div>"
    blog_content = ask_ai(html_prompt, retries=5).replace("```html", "").replace("```", "").strip()
    if not blog_content: 
        sys.exit(1)
    #
    affiliate_offers = [{"title": "🚀 Aaj hi apni 100X kamai shuru karein!", "desc": "AI aur smart trading ki duniya mein kadam rakhne ke liye top experts dwara pramanit platform ka istemal karein.", "btn": "👉 Yahan Free Account Banayein 👈", "link": "#"}, {"title": "🤖 2026 mein apni kamai ko 10X karein!", "desc": "The AI Millionaire ki exclusive community se judein aur rozana naye money-making secrets payein.", "btn": "👉 Community Join Karein 👈", "link": "#"}]
    for offer in affiliate_offers:
        if "[AFFILIATE]" in blog_content:
            mega_cta_html = f"<div style='background: linear-gradient(135deg, #111, #da251c); color: white; padding: 35px 25px; border-radius: 12px; margin: 40px 0; text-align: center; box-shadow: 0 10px 30px rgba(218, 37, 28, 0.3);'><h3 style='color: #fff; margin-top: 0; font-size: 24px; letter-spacing: 0.5px;'>{offer['title']}</h3><p style='font-size: 16px; opacity: 0.9; margin-bottom: 25px; line-height: 1.6;'>{offer['desc']}</p><a href='{offer['link']}' target='_blank' style='display: inline-block; background: #fff; color: #da251c; font-weight: bold; padding: 15px 35px; border-radius: 50px; text-decoration: none; font-size: 18px; transition: 0.3s; box-shadow: 0 5px 15px rgba(0,0,0,0.2);'>{offer['btn']}</a><p style='font-size: 11px; opacity: 0.6; margin-top: 15px; margin-bottom: 0;'>*Shartein laagu. Nivesh baazar jokhimon ke adheen hai.</p></div>"
            blog_content = blog_content.replace("[AFFILIATE]", mega_cta_html, 1)
    blog_content = blog_content.replace("[AFFILIATE]", "") 
    #
    safe_img_base = "future finance trading wealth technology"
    modifiers = ["cinematic", "cyberpunk", "hyperrealistic"]
    safe_fallback = "https://placehold.co/800x400/c00000/ffffff?text=AI+Finance+Update"
    for idx, mod in enumerate(modifiers):
        if "[PHOTO]" in blog_content:
            inner_prompt = urllib.parse.quote(f"{safe_img_base} {mod}")
            inner_img_url = f"https://image.pollinations.ai/prompt/{inner_prompt}?width=800&height=400&nologo=true&seed={post_id + idx + 1}"
            pre_warm_image(inner_img_url)
            img_html = f"<div style='text-align: center;'><img src='{inner_img_url}' onerror=\"this.onerror=null; this.src='{safe_fallback}';\" alt='Premium Finance Illustration' class='article-img'></div>"
            blog_content = blog_content.replace("[PHOTO]", img_html, 1)
    main_prompt = urllib.parse.quote(f"{safe_img_base} masterpiece")
    main_img_url = f"https://image.pollinations.ai/prompt/{main_prompt}?width=1200&height=600&nologo=true&seed={post_id}"
    pre_warm_image(main_img_url)
    #
    audio_filename = f"audio_{post_id}.mp3"
    clean_text = re.sub(r'<[^>]+>', ' ', blog_content)
    clean_text = html.unescape(clean_text)
    clean_text = re.sub(r'\s+', ' ', clean_text).replace("*", "").replace("#", "").strip()
    with open("temp.txt", "w", encoding="utf-8") as temp_f: temp_f.write(clean_text)
    os.system("pip install edge-tts > /dev/null 2>&1")
    os.system(f"edge-tts -f temp.txt --voice hi-IN-SwaraNeural --write-media {audio_filename}")
    post_filename = f"post_{post_id}.html"
    #
    related_html = ""
    if len(posts_db) > 0:
        related_html = "<div style='margin-top: 40px; padding: 25px; background: #fff; border-radius: 12px; box-shadow: 0 5px 20px rgba(0,0,0,0.05); border-left: 5px solid var(--main-red);'><h3 style='margin-top:0; margin-bottom: 15px; color: #111;'>💡 Ye bhi padhein (Related Articles):</h3><ul style='list-style: none; padding: 0;'>"
        for p in posts_db[:3]: related_html += f"<li style='margin-bottom: 12px; font-size: 16px;'>🔗 <a href='{p['file']}' style='color: var(--main-red); text-decoration: none; font-weight: bold;'>{p['title']}</a></li>"
        related_html += "</ul></div>"
    posts_db.insert(0, {"title": current_topic, "file": post_filename, "date": today_date, "img": main_img_url})
    with open("posts.json", "w", encoding="utf-8") as f: json.dump(posts_db, f, ensure_ascii=False, indent=4)
    #
    premium_css = "<style>:root { --main-red: #da251c; --dark-bg: #111; --text-gray: #444; } * { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Segoe UI', Tahoma, sans-serif; } body { background: #f0f2f5; color: #111; line-height: 1.7; } .top-bar { background: var(--main-red); color: white; padding: 5px 0; text-align: center; font-size: 13px; font-weight: bold; letter-spacing: 1px; } header { background: white; border-bottom: 2px solid #eee; box-shadow: 0 4px 10px rgba(0,0,0,0.05); position: sticky; top: 0; z-index: 1000; } .nav-container { max-width: 1100px; margin: 0 auto; padding: 15px 20px; display: flex; justify-content: space-between; align-items: center; position: relative; } .logo { font-size: 28px; font-weight: 900; color: var(--main-red); text-decoration: none; text-transform: uppercase; } .nav-links { display: flex; align-items: center; } .nav-links a { margin-left: 20px; text-decoration: none; color: #111; font-weight: bold; font-size: 16px; transition: 0.3s; } .nav-links a:hover { color: var(--main-red); } .menu-btn { display: none; font-size: 28px; cursor: pointer; color: var(--main-red); font-weight: bold; user-select: none; } .container { max-width: 850px; margin: 40px auto; background: white; padding: 40px; border-radius: 12px; box-shadow: 0 5px 20px rgba(0,0,0,0.05); } h1 { font-size: 38px; line-height: 1.3; margin-bottom: 15px; color: #000; } .meta { font-size: 14px; color: #888; border-bottom: 1px solid #eee; padding-bottom: 15px; margin-bottom: 25px; } .hero-img { width: 100%; border-radius: 12px; margin-bottom: 30px; box-shadow: 0 10px 30px rgba(0,0,0,0.15); border: 2px solid #f9f9f9; object-fit: cover; background-color: #fafafa; } .article-img { width: 100%; border-radius: 12px; margin: 35px 0; box-shadow: 0 10px 30px rgba(0,0,0,0.15); border: 2px solid #f9f9f9; object-fit: cover; background-color: #fafafa; } #article-body { font-size: 20px; color: var(--text-gray); } #article-body h2 { color: #000; margin: 35px 0 15px 0; border-left: 5px solid var(--main-red); padding-left: 15px; background: #fafafa; padding: 10px 15px; border-radius: 0 8px 8px 0; } .tts-box { background: #fff3f3; padding: 15px; border-left: 4px solid var(--main-red); margin-bottom: 25px; font-weight: bold; color: #da251c; border-radius: 0 8px 8px 0; display: flex; align-items: center; gap: 10px;} .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(320px, 1fr)); gap: 30px; } footer { background: var(--dark-bg); color: #888; padding: 60px 20px 30px; margin-top: 60px; text-align: center; } .footer-links a { color: #ccc; text-decoration: none; margin: 0 15px; font-size: 15px; } @media (max-width: 600px) { .grid { grid-template-columns: repeat(2, 1fr) !important; gap: 15px !important; } .container { padding: 15px !important; margin: 15px auto !important; } h1 { font-size: 22px !important; line-height: 1.4 !important; } #article-body { font-size: 16px !important; } .logo { font-size: 20px !important; } .card { padding: 10px !important; } .card-content h3 { font-size: 13px !important; line-height: 1.3 !important; margin-bottom: 8px !important; } .card-content p { font-size: 11px !important; margin-bottom: 10px !important; } .card-content a { font-size: 12px !important; } .hero-img, .article-img { margin: 15px 0 !important; border-radius: 8px !important; } .menu-btn { display: block !important; } .nav-links { display: none; flex-direction: column; position: absolute; top: 100%; left: 0; width: 100%; background: white; padding: 15px 20px; box-shadow: 0 10px 20px rgba(0,0,0,0.1); border-top: 1px solid #eee; z-index: 1001; } .nav-links.active { display: flex !important; } .nav-links a { margin: 0 0 15px 0 !important; font-size: 16px !important; border-bottom: 1px solid #f0f0f0; padding-bottom: 10px; display: block; } } .ticker-wrap { width: 100%; overflow: hidden; background-color: #f1f1f1; border-bottom: 2px solid #C00000; box-sizing: border-box; } .ticker-content { display: flex; white-space: nowrap; animation: tickerAnimation 15s linear infinite; color: #333; font-family: sans-serif; font-size: 14px; font-weight: bold; padding: 10px 0; } .ticker-content span { color: #C00000; } @keyframes tickerAnimation { 0% { transform: translateX(100%); } 100% { transform: translateX(-100%); } } </style><script src='https://cdn.onesignal.com/sdks/web/v16/OneSignalSDK.page.js' defer></script><script>window.OneSignalDeferred = window.OneSignalDeferred || []; OneSignalDeferred.push(async function(OneSignal) { await OneSignal.init({ appId: 'f11333ae-cc73-489e-a1a5-6a74129c3785' }); });</script>"
    schema_markup = f"<script type='application/ld+json'>{{ \"@context\": \"https://schema.org\", \"@type\": \"Article\", \"headline\": \"{current_topic}\", \"image\": \"{main_img_url}\", \"author\": {{ \"@type\": \"Person\", \"name\": \"Mohit (The AI Millionaire)\" }}, \"publisher\": {{ \"@type\": \"Organization\", \"name\": \"Digital Kamai Hub\", \"logo\": {{ \"@type\": \"ImageObject\", \"url\": \"https://api.dicebear.com/7.x/avataaars/svg?seed=Mohit&backgroundColor=f0f2f5\" }} }}, \"datePublished\": \"{today_date}\", \"description\": \"AI aur Finance se judi sabse advance jankari.\" }}</script>"
    header_html = f"<div class='ticker-wrap'><div class='ticker-content'><span>TRENDING:</span> &nbsp; 2026 Best Tech, AI Income, Future Jobs, Digital Kamai Hub Ke Naye Hacks, Share Market Ka Sach!</div></div><header><div class='nav-container'><a href='index.html' class='logo'>Digital Kamai Hub</a><div class='menu-btn' onclick=\"document.getElementById('mobile-menu').classList.toggle('active')\">&#9776;</div><div class='nav-links' id='mobile-menu'><a href='index.html'>Home</a><a href='all-posts.html'>AI Hacks</a><a href='all-posts.html'>Share Market</a><a href='all-posts.html'>Trading Tips</a><a href='contact.html'>Contact</a></div></div></header>"
    footer_html = f"<footer style='margin-top: 40px; background: #111; padding: 40px 20px; text-align: center;'><div style='margin-bottom: 25px;'><p style='color: #ccc; font-size: 14px; margin-bottom: 15px; font-weight: bold; letter-spacing: 1px;'>JOIN THE AI MILLIONAIRE COMMUNITY:</p><div style='display: flex; justify-content: center; gap: 20px; flex-wrap: wrap;'><a href='https://www.youtube.com/@TheAIMillionaire-h5g' target='_blank' style='color: #FF0000; text-decoration: none; font-weight: bold; background: white; padding: 8px 15px; border-radius: 5px;'>YouTube</a><a href='https://t.me/digitalkamaihub_2026' target='_blank' style='color: #0088cc; text-decoration: none; font-weight: bold; background: white; padding: 8px 15px; border-radius: 5px;'>Telegram</a><a href='https://www.instagram.com/aimillionaire_official' target='_blank' style='color: #E1306C; text-decoration: none; font-weight: bold; background: white; padding: 8px 15px; border-radius: 5px;'>Instagram</a><a href='https://www.facebook.com/share/1HNaL98HmW/' target='_blank' style='color: #1877F2; text-decoration: none; font-weight: bold; background: white; padding: 8px 15px; border-radius: 5px;'>Facebook</a></div></div><div class='footer-links' style='margin-bottom: 20px;'><a href='about.html' style='color: #ccc; text-decoration: none; margin: 0 10px;'>About Us</a> | <a href='privacy.html' style='color: #ccc; text-decoration: none; margin: 0 10px;'>Privacy Policy</a> | <a href='disclaimer.html' style='color: #ccc; text-decoration: none; margin: 0 10px;'>Disclaimer</a> | <a href='contact.html' style='color: #ccc; text-decoration: none; margin: 0 10px;'>Contact Us</a></div><p style='margin-top:20px; font-size:13px; color: #888;'>&copy; {current_year} Digital Kamai Hub. All Rights Reserved.</p></footer><div id='cookie-banner' style='position: fixed; bottom: 0; left: 0; width: 100%; background: rgba(17, 17, 17, 0.95); color: white; text-align: center; padding: 15px; font-size: 14px; z-index: 1000;'><span>Hum aapko behtar anubhav dene ke liye cookies ka istemal karte hain. Hamari website ka istemal karke aap hamari Privacy Policy se sahamat hote hain.</span><button onclick=\"document.getElementById('cookie-banner').style.display='none'\" style='background: #da251c; color: white; border: none; padding: 8px 20px; font-weight: bold; border-radius: 5px; cursor: pointer; margin-left: 15px;'>Theek Hai</button></div>"
    article_page = f"<!DOCTYPE html><html lang='hi'><head><meta charset='UTF-8'><meta name='viewport' content='width=device-width, initial-scale=1.0'><title>{current_topic} - Digital Kamai Hub</title>{premium_css}{schema_markup}</head><body><div style='position: fixed; top: 0; left: 0; width: 100%; height: 5px; background-color: transparent; z-index: 9999;'><div id='smart-progress' style='height: 5px; background-color: #da251c; width: 0%; border-top-right-radius: 3px; border-bottom-right-radius: 3px;'></div></div><script>window.addEventListener('scroll', function() {{ var winScroll = document.body.scrollTop || document.documentElement.scrollTop; var height = document.documentElement.scrollHeight - document.documentElement.clientHeight; var scrolled = (winScroll / height) * 100; document.getElementById('smart-progress').style.width = scrolled + '%'; }});</script>{header_html}<div class='container'><h1 style='color: #111; margin-bottom: 15px;'>{current_topic}</h1><div class='meta' style='color: #666; font-size: 14px; margin-bottom: 20px; border-bottom: 1px solid #eee; padding-bottom: 10px; font-weight: bold;'>Date: {today_date} | Author: Mohit (The AI Millionaire)</div><img src='{main_img_url}' onerror=\"this.onerror=null; this.src='https://placehold.co/1200x600/da251c/ffffff?text=Digital+Kamai+Hub';\" style='width: 100%; border-radius: 10px; margin-bottom: 25px; box-shadow: 0 5px 15px rgba(0,0,0,0.1); object-fit: cover;'><div style='background: #fffafa; border-left: 4px solid #da251c; padding: 15px; border-radius: 4px; margin-bottom: 25px;'><p style='margin: 0; color: #da251c; font-weight: bold; font-size: 15px;'>Note: Niche diye gaye laal button ko dabakar poora article audio mein sunein.</p></div><div id='article-body'>{blog_content}</div><div style='margin-top: 40px; padding: 25px; background: #fff; border: 1px solid #eee; border-radius: 8px; border-left: 5px solid #111;'><h3 style='margin: 0 0 10px 0; color: #111; font-size: 18px;'>Lekhak: Mohit | The AI Millionaire</h3><p style='margin: 0; color: #555; font-size: 15px; line-height: 1.6;'>Namaste! Main Mohit hoon. Mera mission aapko AI ki taqat se vittiya azaadi dilana aur 2026 mein smart tareeke se online kamai ke advance secrets sikhana hai.</p></div><div style='margin-top: 30px;'>{related_html}</div><audio id='premium-audio' src='{audio_filename}'></audio><button id='floating-tts-btn' onclick='toggleAudio()' style='display: block; width: 100%; background: #da251c; color: white; border: none; padding: 15px; font-size: 18px; font-weight: bold; border-radius: 8px; cursor: pointer; margin-top: 30px; box-shadow: 0 4px 15px rgba(218,37,28,0.3);'>Play Audio</button></div>{footer_html}</body></html>"
    with open(post_filename, "w", encoding="utf-8") as f: f.write(article_page)
    #
    card_template = lambda p: f"<div class='card' style='background: #fff; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.05); overflow: hidden; margin-bottom: 20px;'><img src='{p['img']}' onerror=\"this.onerror=null; this.src='https://placehold.co/800x400/111/fff?text=Digital+Kamai+Hub';\" style='width: 100%; height: 200px; object-fit: cover;'><div style='padding: 20px;'><p style='color: #888; font-size: 13px; margin-bottom: 10px;'>📅 {p['date']}</p><h3 style='margin-bottom: 15px; font-size: 18px; line-height: 1.4;'><a href='{p['file']}' style='color: #111; text-decoration: none;'>{p['title']}</a></h3><a href='{p['file']}' style='color: #da251c; font-weight: bold; text-decoration: none; font-size: 15px;'>Read More →</a></div></div>"
    home_cards = "".join([card_template(p) for p in posts_db[:10]])
    all_cards = "".join([card_template(p) for p in posts_db])
    with open("index.html", "w", encoding="utf-8") as f: f.write(f"<!DOCTYPE html><html lang='hi'><head><meta charset='UTF-8'><meta name='viewport' content='width=device-width, initial-scale=1.0'><title>Digital Kamai Hub</title>{premium_css}</head><body>{header_html}<div class='container'><h1 style='text-align: center; margin-bottom: 40px;'>Naye Hacks aur Tricks</h1>{home_cards}<div style='text-align: center; margin-top: 40px;'><a href='all-posts.html' style='background: #111; color: #fff; padding: 12px 25px; text-decoration: none; border-radius: 5px; font-weight: bold;'>Sabhi Posts Dekhein</a></div></div>{footer_html}</body></html>")
    with open("all-posts.html", "w", encoding="utf-8") as f: f.write(f"<!DOCTYPE html><html lang='hi'><head><meta charset='UTF-8'><meta name='viewport' content='width=device-width, initial-scale=1.0'><title>All Posts - Digital Kamai Hub</title>{premium_css}</head><body>{header_html}<div class='container'><h1 style='margin-bottom: 30px;'>Sabhi Articles</h1>{all_cards}</div>{footer_html}</body></html>")
    #
    pages = {
        "about": ("About Us", "<h2 style='color: var(--main-red); margin-bottom: 15px; font-size: 28px;'>Hamari Kahani (Our Story)</h2><p style='font-size: 18px; margin-bottom: 25px; color: #333;'>Namaste! <strong>Digital Kamai Hub</strong> mein aapka swagat hai. Yeh sirf ek blog nahi, balki ek digital revolution hai.</p><h2 style='color: var(--main-red); margin-bottom: 15px; font-size: 24px;'>🎯 Mission & Vision</h2><p style='font-size: 18px; margin-bottom: 25px; color: #333;'>Hamara mission bilkul saaf hai: <strong>\"Bacchon ka khel nahi, Smart Work!\"</strong></p><h2 style='color: var(--main-red); margin-bottom: 15px; font-size: 24px;'>👨‍💻 Meet The Founder: Mohit (The AI Millionaire)</h2><div style='background: #fafafa; padding: 25px; border-left: 5px solid var(--main-red); border-radius: 8px; margin-bottom: 30px;'><p style='font-size: 17px; margin-bottom: 15px; color: #222;'>Mohit ek <strong>Full-Stack Web Developer aur Visionary Entrepreneur</strong> hain.</p></div>"),
        "privacy": ("Privacy Policy", "<h2 style='color: var(--main-red); margin-bottom: 15px; font-size: 28px;'>Privacy Policy</h2><p style='font-size: 18px; margin-bottom: 15px; color: #333;'>Aapki privacy hamare liye sabse zyada zaroori hai.</p><ul><li><strong>Cookies:</strong> Hum website ka experience behtar banane ke liye cookies ka istemal karte hain.</li></ul>"),
        "disclaimer": ("Disclaimer", "<h2 style='color: var(--main-red); margin-bottom: 15px; font-size: 28px;'>Disclaimer (Chetawani)</h2><p style='font-size: 18px; margin-bottom: 15px; color: #333;'>Sabhi jankari keval shikhsha ke liye hai.</p><ul><li><strong>Risk (Jokhim):</strong> Trading aur investment mein jokhim hota hai.</li></ul>"),
        "contact": ("Contact Us", "<div style='background-color: #f9f9f9; padding: 40px 15px; text-align: center;'><h1 style='color: #C00000;'>Contact Us</h1><p>Humse sampark karein!</p><form action='https://formsubmit.co/ajax/ramesh.chandra89056@gmail.com' method='POST'><input type='email' name='email' placeholder='Email' required style='padding: 10px; width: 80%; margin-bottom: 10px;'><br><textarea name='message' placeholder='Message' required style='padding: 10px; width: 80%; height: 100px; margin-bottom: 10px;'></textarea><br><button type='submit' style='padding: 10px 20px; background: #C00000; color: white; border: none;'>Send</button></form></div>")
    }
    for p_file, (p_title, p_content) in pages.items():
        premium_legal_html = f"<!DOCTYPE html><html lang='hi'><head><meta charset='UTF-8'><meta name='viewport' content='width=device-width, initial-scale=1.0'><title>{p_title} - Digital Kamai Hub</title><style>body {{ font-family: 'Segoe UI', Tahoma, sans-serif; background: #f0f2f5; margin: 0; color: #111; }} header {{ background: white; border-bottom: 2px solid #eee; display: flex; justify-content: space-between; align-items: center; padding: 15px 20px; }} .logo {{ font-size: 24px; font-weight: 900; color: #da251c; text-decoration: none; text-transform: uppercase; }} .nav-links {{ display: flex; gap: 20px; }} .nav-links a {{ text-decoration: none; color: #111; font-weight: bold; font-size: 16px; transition: 0.3s; }} .nav-links a:hover {{ color: #da251c; }} .menu-btn {{ display: none; font-size: 28px; cursor: pointer; color: #da251c; user-select: none; }} @media (max-width: 600px) {{ .nav-links {{ display: none; flex-direction: column; position: absolute; top: 65px; left: 0; width: 100%; background: white; padding: 15px 20px; box-shadow: 0 10px 20px rgba(0,0,0,0.1); z-index: 1000; border-top: 1px solid #eee; }} .nav-links.active {{ display: flex !important; }} .nav-links a {{ padding-bottom: 10px; border-bottom: 1px solid #f0f0f0; margin-bottom: 10px; display: block; }} .menu-btn {{ display: block; }} }}</style></head><body><header><a href='index.html' class='logo'>Digital Kamai Hub</a><div class='menu-btn' onclick=\"document.getElementById('mobile-menu').classList.toggle('active')\">&#9776;</div><div class='nav-links' id='mobile-menu'><a href='index.html'>Home</a><a href='about.html'>About</a><a href='privacy.html'>Privacy</a><a href='disclaimer.html'>Disclaimer</a><a href='contact.html'>Contact</a></div></header><div style='max-width: 850px; margin: 40px auto; background: white; padding: 40px; border-radius: 12px; box-shadow: 0 5px 20px rgba(0,0,0,0.05); line-height: 1.7;'>{p_content}</div></body></html>"
        with open(f"{p_file}.html", "w", encoding="utf-8") as f: f.write(premium_legal_html)
    #
    ist_time = datetime.utcnow() + timedelta(hours=5, minutes=30)
    time_str = ist_time.strftime("%I:%M %p (IST)")
    total_posts = len(posts_db)
    blog_url = f"https://rameshchandra89056-bloger.github.io/AI-Autoblogger-Engine/{post_filename}"
    send_telegram_msg(f"✅ SUCCESS: Naya blog post publish ho gaya!\n⏰ Samay: {time_str}\n📝 Kul Post: {total_posts}\n🌐 Link: {blog_url}")
    send_push_notification(current_topic, blog_url)
    print("✅ Website 100% safalta ke sath ban gayi hai!")
except Exception as e:
    print(f"❌ Error: {e}")
    sys.exit(1)

# ==========================================
# 🚀 AUTO-SITEMAP GENERATOR (ZERO-TOUCH)
# ==========================================
def generate_auto_sitemap():
    try:
        base_url = "https://rameshchandra89056-bloger.github.io/AI-Autoblogger-Engine"
        html_files = [f for f in os.listdir() if f.endswith('.html')]
        sitemap_content = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        today_date_sm = datetime.now().strftime("%Y-%m-%d")
        for file in html_files: sitemap_content += f'  <url>\n    <loc>{base_url}/{file}</loc>\n    <lastmod>{today_date_sm}</lastmod>\n    <changefreq>daily</changefreq>\n  </url>\n'
        sitemap_content += '</urlset>'
        with open('sitemap.xml', 'w', encoding='utf-8') as f: f.write(sitemap_content)
    except: pass
generate_auto_sitemap()
