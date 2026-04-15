import urllib.request
import urllib.parse
import json
import os
import sys
import time

# ==========================================
# THE IMMORTAL SYSTEM - FULL CONTENT FIX (v35.0)
# Aaj Tak Design + Guaranteed Article Generation
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
            posts_db = json.load(f)
        except: pass

available_model = "models/gemini-1.5-flash"

def ask_ai(prompt, retries=15):
    for i in range(retries):
        current_key = API_KEYS[i % len(API_KEYS)]
        url = f"https://generativelanguage.googleapis.com/v1beta/{available_model}:generateContent?key={current_key}"
        try:
            data = json.dumps({"contents": [{"parts": [{"text": prompt}]}]}).encode('utf-8')
            req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'})
            with urllib.request.urlopen(req, timeout=90) as response:
                res = json.loads(response.read().decode('utf-8'))
                content = res['candidates'][0]['content']['parts'][0]['text'].strip()
                if len(content) > 100: return content
        except: time.sleep(10)
    return ""

# --- AGENT WORK ---
print("🚀 टॉपिक और SEO बना रहा हूँ...")
topic_prompt = f"ऑनलाइन पैसे कमाने पर {current_year} का एक वायरल हिंदी टाइटल दो। पुराने: {[p['title'] for p in posts_db[:3]]} से अलग हो।"
current_topic = ask_ai(topic_prompt).replace('"', '')

# इमेजेज के लिए कीवर्ड्स
img_k = urllib.parse.quote(current_topic.split()[0] + " technology business")

print("✍️ पूरा आर्टिकल लिख रहा हूँ (इसमें समय लग सकता है)...")
html_prompt = f"""तुम एक प्रोफेशनल हिंदी पत्रकार हो। विषय: '{current_topic}'।
एक विस्तृत (1200+ शब्द) न्यूज़ आर्टिकल लिखो।
नियम:
1. आर्टिकल के बीच में कम से कम 3 बार <img src='https://image.pollinations.ai/prompt/{img_k}_scene?width=800&height=450&nologo=true' class='post-img'> डालें।
2. लेख के अंत में यह बटन लगाओ: <a href='https://www.youtube.com/results?search_query={urllib.parse.quote(current_topic)}' target='_blank' class='news-yt-btn'>📺 इससे जुड़ा वीडियो यहाँ देखें</a>
3. सिर्फ HTML (h2, p, strong, ul) का उपयोग करें।"""

blog_content = ask_ai(html_prompt)

if not blog_content:
    print("❌ AI ने कंटेंट नहीं दिया।")
    sys.exit(1)

# --- DATABASE ---
main_img_url = f"https://image.pollinations.ai/prompt/{img_k}_main_news?width=1200&height=600&nologo=true"
post_filename = f"post_{post_id}.html"
posts_db.insert(0, {"title": current_topic, "file": post_filename, "date": today_date, "img": main_img_url})
with open("posts.json", "w", encoding="utf-8") as f: json.dump(posts_db, f, ensure_ascii=False, indent=4)

# --- THE DESIGN ---
news_css = """
<style>
    :root { --main-red: #da251c; --dark-bg: #111; }
    body { font-family: 'Segoe UI', sans-serif; background: #f0f2f5; margin: 0; padding: 0; }
    header { background: white; border-top: 5px solid var(--main-red); box-shadow: 0 2px 10px rgba(0,0,0,0.1); padding: 15px; position: sticky; top:0; z-index:100;}
    .logo { font-size: 26px; font-weight: 900; color: var(--main-red); text-decoration: none; display: block; text-align: center; }
    .trending { background: var(--main-red); color: white; padding: 60px 10px; text-align: center; font-size: 13px; font-weight: bold; }
    .container { max-width: 850px; margin: 30px auto; background: white; padding: 40px; border-radius: 8px; box-shadow: 0 5px 25px rgba(0,0,0,0.05); }
    h1 { font-size: 36px; line-height: 1.3; margin-bottom: 20px; }
    .meta { color: #888; border-bottom: 1px solid #eee; padding-bottom: 15px; margin-bottom: 25px; font-size: 14px; }
    .post-img, .hero-img { width: 100%; border-radius: 10px; margin: 25px 0; }
    #article-body { font-size: 19px; line-height: 1.8; color: #333; }
    .news-yt-btn { display: block; background: #ff0000; color: white; text-align: center; padding: 18px; border-radius: 8px; text-decoration: none; font-weight: bold; margin-top: 40px; }
    .tts-btn { position: fixed; bottom: 30px; right: 30px; background: var(--main-red); color: white; border: none; padding: 15px 25px; border-radius: 50px; font-weight: bold; cursor: pointer; box-shadow: 0 5px 20px rgba(0,0,0,0.3); z-index: 999; }
    footer { background: var(--dark-bg); color: #888; padding: 50px 20px; text-align: center; margin-top: 50px; }
    .footer-links a { color: #ccc; text-decoration: none; margin: 0 15px; font-size: 14px; }
</style>
"""

article_page = f"""
<!DOCTYPE html>
<html lang="hi">
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"><title>{current_topic}</title>{news_css}</head>
<body>
    <div class="trending">🔥 TRENDING: AI Automation, Passive Wealth, Digital India 2026</div>
    <header><a href="index.html" class="logo">DIGITAL KAMAI HUB</a></header>
    <div class="container">
        <div class="meta">Published: {today_date} | by AI Expert</div>
        <h1>{current_topic}</h1>
        <img src="{main_img_url}" class="hero-img">
        <div id="article-body">{blog_content}</div>
    </div>
    <button class="tts-btn" onclick="readOut()">🔊 लेख सुनें</button>
    <footer>
        <div class="footer-links"><a href="about.html">About</a><a href="privacy.html">Privacy</a><a href="disclaimer.html">Disclaimer</a></div>
        <p>&copy; 2026 Digital Kamai Hub</p>
    </footer>
    <script>
        function readOut() {{
            let txt = document.getElementById('article-body').innerText;
            let ut = new SpeechSynthesisUtterance(txt);
            ut.lang = 'hi-IN'; ut.rate = 0.9;
            window.speechSynthesis.speak(ut);
        }}
    </script>
</body></html>
"""

with open(post_filename, "w", encoding="utf-8") as f: f.write(article_page)

# --- HOME PAGE FIX ---
home_cards = "".join([f"""
<div style="background:white; margin-bottom:30px; border-radius:12px; overflow:hidden; box-shadow:0 4px 15px rgba(0,0,0,0.08); display:flex; flex-wrap:wrap;">
    <img src="{p['img']}" style="width:350px; height:220px; object-fit:cover;">
    <div style="padding:25px; flex:1; min-width:300px;">
        <h2 style="font-size:24px; margin:0 0 15px 0;"><a href="{p['file']}" style="color:black; text-decoration:none;">{p['title']}</a></h2>
        <p style="color:#777;">🗓 {p['date']}</p>
        <a href="{p['file']}" style="color:var(--main-red); font-weight:bold; text-decoration:none; display:inline-block; margin-top:15px;">पूरा लेख पढ़ें →</a>
    </div>
</div>
""" for p in posts_db])

with open("index.html", "w", encoding="utf-8") as f:
    f.write(f"<!DOCTYPE html><html lang='hi'><head><meta charset='UTF-8'>{news_css}<title>Digital Kamai Hub</title></head><body><header><a href='index.html' class='logo'>DIGITAL KAMAI HUB</a></header><div class='container' style='max-width:1100px;'>{home_cards}</div></body></html>")
    
