import urllib.request
import urllib.parse
import json
import os
import sys
import time

# ==========================================
# THE IMMORTAL SYSTEM - X-RAY EDITION (v29.0)
# Advanced Error Logging & Premium UI
# ==========================================

raw_key = os.environ.get("GEMINI_API_KEY", "")
API_KEY = raw_key.strip()
if not API_KEY: 
    print("❌ API Key गायब है!")
    sys.exit(1)

current_year = time.strftime("%Y")
today_date = time.strftime("%d %B %Y")
post_id = int(time.time())

posts_db = []
past_titles = []
if os.path.exists("posts.json"):
    with open("posts.json", "r", encoding="utf-8") as f:
        try:
            posts_db = json.load(f)
            past_titles = [post["title"] for post in posts_db][:20] 
        except: pass

list_url = f"https://generativelanguage.googleapis.com/v1beta/models?key={API_KEY}"
available_model = "models/gemini-1.5-flash"
try:
    req = urllib.request.Request(list_url)
    with urllib.request.urlopen(req, timeout=30) as response:
        res = json.loads(response.read().decode('utf-8'))
        for m in res.get('models', []):
            if 'generateContent' in m.get('supportedGenerationMethods', []) and 'gemini-1.5-flash' in m.get('name', '').lower():
                available_model = m['name']; break
except Exception as e: pass

api_url = f"https://generativelanguage.googleapis.com/v1beta/{available_model}:generateContent?key={API_KEY}"

# मास्टर AI फंक्शन (X-Ray Scanner के साथ)
def ask_ai(prompt, retries=5):
    for i in range(retries):
        try:
            data = json.dumps({"contents": [{"parts": [{"text": prompt}]}]}).encode('utf-8')
            req = urllib.request.Request(api_url, data=data, headers={'Content-Type': 'application/json'})
            with urllib.request.urlopen(req, timeout=60) as response:
                res = json.loads(response.read().decode('utf-8'))
                return res['candidates'][0]['content']['parts'][0]['text'].strip()
        except urllib.error.HTTPError as e:
            err_msg = e.read().decode('utf-8')
            print(f"❌ GOOGLE API ERROR: {err_msg}")
            print(f"⏳ 15 सेकंड इंतज़ार कर रहे हैं... ({i+1}/{retries})")
            time.sleep(15)
        except Exception as e:
            print(f"⚠️ Network Error: {e}")
            print(f"⏳ 15 सेकंड इंतज़ार कर रहे हैं... ({i+1}/{retries})")
            time.sleep(15)
    return ""

print("🚀 रोबोट चालू हो गया है...")

# --- AGENT 1: TOPIC ---
print("🧠 एजेंट 1: टॉपिक ढूँढ रहा है...")
topic_prompt = f"तुम एक ट्रेंड एनालिस्ट हो। {current_year} में मेक मनी ऑनलाइन या AI से जुड़ा एक वायरल ब्लॉग टाइटल (हिंदी में) दो। पुराने टाइटल्स: {past_titles} से अलग हो। सिर्फ 'टाइटल' लिखना।"
topic_res = ask_ai(topic_prompt)
if not topic_res: 
    print("❌ AI ने कोई जवाब नहीं दिया (फेल)।")
    sys.exit(1)

current_topic = topic_res.replace('"', '').replace("'", "").replace("*", "")
print(f"🎯 टॉपिक मिला: {current_topic}")

# --- AGENT 2: SEO ---
print("📊 एजेंट 2: SEO डेटा बना रहा है...")
seo_prompt = f"विषय: '{current_topic}'। सिर्फ इस एक लाइन के फॉर्मेट में जवाब दो: MAIN_IMAGE_ENGLISH_KEYWORD | HINDI_SEO_DESCRIPTION | 5_SEO_KEYWORDS_COMMA_SEPARATED. कोई और शब्द मत लिखना।"
seo_raw = ask_ai(seo_prompt)

main_img_words = "futuristic digital technology"
meta_desc = f"{current_year} का बेस्ट ब्लॉग पोस्ट।"
meta_keywords = f"AI, Make Money, {current_year}"
try:
    if "|" in seo_raw:
        parts = seo_raw.split("|")
        if len(parts) >= 3:
            main_img_words = parts[0].strip(); meta_desc = parts[1].strip(); meta_keywords = parts[2].strip()
except: pass

# --- AGENT 3: HTML CODER ---
print("💻 एजेंट 3: HTML कोडिंग और मल्टीमीडिया लगा रहा है...")
html_prompt = f"""विषय: '{current_topic}'। एक विस्तृत हिंदी ब्लॉग पोस्ट लिखो।
नियम:
1. लेख के बीच में 2 जगह ये फोटो कोड लगाओ: <img src="https://image.pollinations.ai/prompt/ENG_KEYWORD?width=800&height=400&nologo=true" class="article-img"> (ENG_KEYWORD की जगह पैराग्राफ से जुड़ा इंग्लिश शब्द डालना)।
2. 1 जगह यूट्यूब वीडियो लगाओ: <div class="video-container"><iframe src="https://www.youtube.com/embed?listType=search&list=ENG_SEARCH_TERM" frameborder="0" allowfullscreen></iframe></div> (ENG_SEARCH_TERM में इंग्लिश कीवर्ड डालना)।
3. मुझे जवाब में सिर्फ HTML कोड (h2, p, ul) देना। कोई ```html मत लगाना।"""

blog_content = ask_ai(html_prompt, retries=8).replace("```html", "").replace("```", "").strip()
if not blog_content or len(blog_content) < 200: 
    print("❌ HTML कोडिंग फेल हो गई।")
    sys.exit(1)

print("✅ पोस्ट तैयार है! पब्लिश हो रही है...")

# --- PUBLISHING (PREMIUM RESPONSIVE UI) ---
main_img_safe = urllib.parse.quote(main_img_words)
main_img_url = f"[https://image.pollinations.ai/prompt/](https://image.pollinations.ai/prompt/){main_img_safe}?width=1200&height=600&nologo=true"

post_filename = f"post_{post_id}.html"
posts_db.insert(0, {"title": current_topic, "file": post_filename, "date": today_date, "img": main_img_url})
with open("posts.json", "w", encoding="utf-8") as f: json.dump(posts_db, f, ensure_ascii=False, indent=4)

premium_css = """
    <style>
        :root { --primary: #2563eb; --bg: #f8fafc; --text: #0f172a; --card: #ffffff; }
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { font-family: 'Segoe UI', system-ui, sans-serif; background: var(--bg); color: var(--text); line-height: 1.7; }
        header { background: rgba(255, 255, 255, 0.9); backdrop-filter: blur(10px); position: sticky; top: 0; z-index: 1000; border-bottom: 1px solid #e2e8f0; padding: 15px 20px; display: flex; justify-content: space-between; align-items: center; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05); }
        .logo { font-size: 24px; font-weight: 800; color: var(--primary); text-decoration: none; letter-spacing: -0.5px; }
        nav a { margin-left: 20px; text-decoration: none; color: var(--text); font-weight: 600; transition: 0.3s; }
        nav a:hover { color: var(--primary); }
        .main-container { max-width: 900px; margin: 40px auto; padding: 0 20px; }
        .article-header { text-align: center; margin-bottom: 40px; }
        .article-title { font-size: 42px; font-weight: 900; line-height: 1.2; margin-bottom: 15px; color: #1e293b; }
        .meta-data { color: #64748b; font-size: 15px; font-weight: 500; text-transform: uppercase; letter-spacing: 1px; }
        .hero-img { width: 100%; height: 450px; object-fit: cover; border-radius: 16px; box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1); margin-bottom: 40px; }
        .article-img { width: 100%; border-radius: 12px; margin: 30px 0; box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1); }
        .video-container { position: relative; padding-bottom: 56.25%; height: 0; overflow: hidden; max-width: 100%; border-radius: 12px; margin: 30px 0; box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1); }
        .video-container iframe { position: absolute; top: 0; left: 0; width: 100%; height: 100%; }
        #article-content { font-size: 19px; color: #334155; }
        #article-content h2 { font-size: 28px; color: #0f172a; margin: 40px 0 20px 0; border-bottom: 2px solid #e2e8f0; padding-bottom: 10px; }
        #article-content p { margin-bottom: 20px; }
        .tts-floating { position: fixed; bottom: 30px; right: 30px; background: var(--primary); color: white; border: none; padding: 15px 25px; border-radius: 50px; font-size: 16px; font-weight: bold; cursor: pointer; box-shadow: 0 10px 25px rgba(37, 99, 235, 0.4); transition: 0.3s ease; z-index: 999; display: flex; align-items: center; gap: 10px; }
        .tts-floating:hover { transform: translateY(-5px); box-shadow: 0 15px 30px rgba(37, 99, 235, 0.6); }
        footer { background: #0f172a; color: #94a3b8; text-align: center; padding: 50px 20px; margin-top: 60px; font-size: 15px; }
        footer a { color: #cbd5e1; text-decoration: none; margin: 0 15px; transition: 0.3s; }
        footer a:hover { color: white; }
        @media (max-width: 768px) {
            .article-title { font-size: 32px; }
            .hero-img { height: 250px; }
            #article-content { font-size: 17px; }
            .tts-floating { bottom: 20px; right: 20px; padding: 12px 20px; font-size: 14px; }
            header { flex-direction: column; gap: 15px; }
            nav a { margin: 0 10px; }
        }
    </style>
"""

article_html = f"""<!DOCTYPE html>
<html lang="hi">
<head>
    <meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{current_topic} | Digital Kamai Hub</title>
    <meta name="description" content="{meta_desc}"><meta name="keywords" content="{meta_keywords}">
    {premium_css}
</head>
<body>
    <header><a href="index.html" class="logo">🚀 Digital Kamai Hub</a><nav><a href="index.html">Home</a> <a href="#">News</a></nav></header>
    <div class="main-container">
        <div class="article-header"><h1 class="article-title">{current_topic}</h1><p class="meta-data">🗓️ {today_date} &nbsp; | &nbsp; ⏱️ 5 Min Read</p></div>
        <img src="{main_img_url}" class="hero-img" alt="Hero Image">
        <div id="article-content">{blog_content}</div>
    </div>
    <button class="tts-floating" onclick="speakArticle()" id="speakBtn">🔊 लेख सुनें</button>
    <footer><div style="margin-bottom: 20px;"><a href="#">About Us</a> <a href="#">Privacy Policy</a> <a href="#">Disclaimer</a></div><p>&copy; {current_year} Digital Kamai Hub. All Rights Reserved.</p></footer>
    <script>
        let isPlaying = false; let speech = new SpeechSynthesisUtterance();
        function speakArticle() {{
            if (isPlaying) {{ window.speechSynthesis.cancel(); document.getElementById("speakBtn").innerHTML = "🔊 लेख सुनें"; isPlaying = false; }} 
            else {{
                let textToRead = document.getElementById("article-content").innerText;
                speech.text = textToRead; speech.lang = 'hi-IN'; speech.rate = 0.9;
                window.speechSynthesis.speak(speech);
                document.getElementById("speakBtn").innerHTML = "⏹️ बंद करें"; isPlaying = true;
                speech.onend = function() {{ document.getElementById("speakBtn").innerHTML = "🔊 लेख सुनें"; isPlaying = false; }};
            }}
        }}
    </script>
</body>
</html>"""

with open(post_filename, "w", encoding="utf-8") as f: f.write(article_html)

post_links = "".join([f'<div style="background:var(--card); border-radius:12px; overflow:hidden; box-shadow:0 4px 6px -1px rgba(0,0,0,0.1); transition:0.3s; border:1px solid #e2e8f0;"><img src="{p.get("img", "[https://via.placeholder.com/400x250](https://via.placeholder.com/400x250)")}" style="width:100%; height:200px; object-fit:cover;"><div style="padding:20px;"><p style="color:#64748b; font-size:13px; margin-bottom:10px; font-weight:bold;">{p["date"]}</p><h3 style="font-size:20px; line-height:1.4; margin-bottom:15px;"><a href="{p["file"]}" style="color:var(--text); text-decoration:none;">{p["title"]}</a></h3><a href="{p["file"]}" style="color:var(--primary); font-weight:bold; text-decoration:none;">Read More →</a></div></div>' for p in posts_db])

home_html = f"""<!DOCTYPE html><html lang="hi"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"><title>Digital Kamai Hub</title>{premium_css}<style>.grid-container {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 30px; margin-top: 40px; }}</style></head><body><header><a href="index.html" class="logo">🚀 Digital Kamai Hub</a><nav><a href="index.html">Home</a></nav></header><div class="main-container"><h2 style="font-size:32px; color:#1e293b; border-bottom:2px solid #e2e8f0; padding-bottom:10px;">🔥 ताज़ा लेख</h2><div class="grid-container">{post_links}</div></div><footer><p>&copy; {current_year} Digital Kamai Hub</p></footer></body></html>"""

with open("index.html", "w", encoding="utf-8") as f: f.write(home_html)
