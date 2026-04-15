import urllib.request
import urllib.parse
import json
import os
import sys
import time

# ==========================================
# THE IMMORTAL SYSTEM - MASTER PLAN EDITION (v21.0)
# Multi-Image Support & Unbreakable SEO Parser
# ==========================================

raw_key = os.environ.get("GEMINI_API_KEY", "")
API_KEY = raw_key.strip()

if not API_KEY:
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
        except:
            pass

list_url = f"https://generativelanguage.googleapis.com/v1beta/models?key={API_KEY}"
available_model = None
try:
    req = urllib.request.Request(list_url)
    with urllib.request.urlopen(req, timeout=30) as response:
        res = json.loads(response.read().decode('utf-8'))
        for m in res.get('models', []):
            if 'generateContent' in m.get('supportedGenerationMethods', []) and 'gemini' in m.get('name', '').lower():
                available_model = m['name']
                if 'flash' in available_model: break
except: pass
if not available_model: sys.exit(1)

# ---------------------------------------------------------
# STEP 1: THE BRAIN (नया टॉपिक सोचना)
# ---------------------------------------------------------
topic_prompt = f"तुम एक SEO एक्सपर्ट हो। 'मेक मनी ऑनलाइन', 'AI टूल्स' या 'फ्रीलांसिंग' पर साल {current_year} का एक नया और वायरल ब्लॉग टाइटल (हिंदी में) दो। यह इन पुराने टाइटल्स से अलग होना चाहिए: {past_titles}। जवाब में सिर्फ 'टाइटल' लिखना।"
topic_url = f"https://generativelanguage.googleapis.com/v1beta/{available_model}:generateContent?key={API_KEY}"

try:
    req = urllib.request.Request(topic_url, data=json.dumps({"contents": [{"parts": [{"text": topic_prompt}]}]}).encode('utf-8'), headers={'Content-Type': 'application/json'})
    with urllib.request.urlopen(req, timeout=50) as response:
        res = json.loads(response.read().decode('utf-8'))
        current_topic = res['candidates'][0]['content']['parts'][0]['text'].strip().replace('"', '').replace("'", "")
except: sys.exit(1)
if not current_topic: sys.exit(1)

# ---------------------------------------------------------
# STEP 2: MULTI-IMAGE & SEO CONTENT GENERATOR
# ---------------------------------------------------------
content_prompt = f"""तुम एक प्रो ब्लॉगर हो। विषय: '{current_topic}'।
नियम:
1. लेख में जहाँ भी किसी नई चीज़ या उदाहरण की बात हो, वहाँ यह HTML कोड लगा देना: <img src="https://image.pollinations.ai/prompt/YOUR_KEYWORD?width=800&height=400&nologo=true" style="width:100%; border-radius:8px; margin:20px 0; box-shadow: 0 4px 10px rgba(0,0,0,0.1);"> (YOUR_KEYWORD की जगह उस पैराग्राफ से जुड़ा एक इंग्लिश शब्द डालना जैसे futuristic_robot, office_laptop)। लेख के अंदर कम से कम 2-3 फोटो डालना।
2. जवाब बिलकुल इसी फॉर्मेट में देना है (इन '~~~' निशानों को मत हटाना):

~~~MAIN_IMG~~~
(मुख्य फोटो के लिए 5 इंग्लिश शब्द)
~~~META_DESC~~~
(2 लाइन का हिंदी SEO डिस्क्रिप्शन)
~~~KEYWORDS~~~
(5 SEO कीवर्ड्स कॉमा लगाकर)
~~~HTML_CONTENT~~~
(यहाँ पूरा HTML लेख h2, p, ul, strong और अंदरूनी <img> टैग्स के साथ)"""

try:
    req = urllib.request.Request(topic_url, data=json.dumps({"contents": [{"parts": [{"text": content_prompt}]}]}).encode('utf-8'), headers={'Content-Type': 'application/json'})
    with urllib.request.urlopen(req, timeout=80) as response:
        res = json.loads(response.read().decode('utf-8'))
        full_text = res['candidates'][0]['content']['parts'][0]['text']
except: sys.exit(1)

# Parsing The Unbreakable Format
try:
    parts = full_text.split("~~~")
    main_img_words = parts[2].strip()
    meta_desc = parts[4].strip()
    meta_keywords = parts[6].strip()
    blog_content = parts[8].replace("```html", "").replace("```", "").strip()
except:
    sys.exit(1) # अगर AI ने गलती की, तो पोस्ट मत डालो

main_img_safe = urllib.parse.quote(main_img_words)
main_img_url = f"https://image.pollinations.ai/prompt/{main_img_safe}?width=800&height=400&nologo=true"

# ---------------------------------------------------------
# STEP 3: DATABASE & HTML PUBLISHING
# ---------------------------------------------------------
post_filename = f"post_{post_id}.html"
new_post = {"title": current_topic, "file": post_filename, "date": today_date}
posts_db.insert(0, new_post)

with open("posts.json", "w", encoding="utf-8") as f:
    json.dump(posts_db, f, ensure_ascii=False, indent=4)

header_menu = """
    <nav style="background: white; padding: 15px; text-align: center; position: sticky; top: 0; box-shadow: 0 2px 10px rgba(0,0,0,0.05); z-index: 100;">
        <a href="index.html" style="color: #203a43; text-decoration: none; margin: 0 15px; font-weight: bold; font-size: 18px;">🏠 होम</a>
        <a href="index.html" style="color: #203a43; text-decoration: none; margin: 0 15px; font-weight: bold; font-size: 18px;">🔥 लेटेस्ट न्यूज़</a>
    </nav>
"""

footer_html = """
    <footer style="text-align: center; padding: 40px 20px; background: #111; color: #aaa; margin-top: 50px; font-size: 14px;">
        <div style="margin-bottom: 20px;">
            <a href="about.html" style="color: #aaa; text-decoration: none; margin: 0 15px;">About Us</a> |
            <a href="privacy.html" style="color: #aaa; text-decoration: none; margin: 0 15px;">Privacy Policy</a> |
            <a href="disclaimer.html" style="color: #aaa; text-decoration: none; margin: 0 15px;">Disclaimer</a>
        </div>
        <p>&copy; 2026 Digital Kamai Hub. All Rights Reserved.</p>
    </footer>
"""

article_html = f"""<!DOCTYPE html>
<html lang="hi">
<head>
    <meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{current_topic} | Digital Kamai Hub</title>
    <meta name="description" content="{meta_desc}">
    <meta name="keywords" content="{meta_keywords}">
    <style>
        body {{ font-family: 'Segoe UI', Tahoma, sans-serif; background: #f8f9fa; margin: 0; color: #333; }}
        header {{ background: linear-gradient(135deg, #0f2027, #203a43, #2c5364); color: white; padding: 40px 20px; text-align: center; }}
        .container {{ max-width: 800px; margin: 40px auto; background: white; padding: 40px; border-radius: 8px; box-shadow: 0 2px 15px rgba(0,0,0,0.05); line-height: 1.8; font-size: 18px; }}
        h1 {{ color: #f1c40f; margin: 0; }}
        h2 {{ color: #203a43; border-left: 4px solid #f1c40f; padding-left: 15px; margin-top: 30px; }}
        .main-img {{ width: 100%; border-radius: 8px; margin: 20px 0; object-fit: cover; box-shadow: 0 4px 10px rgba(0,0,0,0.1); background-color: #0f2027; min-height: 250px; }}
    </style>
</head>
<body>
    <header>
        <h1 style="font-size: 36px; letter-spacing: 1px;">🚀 Digital Kamai Hub</h1>
        <p style="font-size: 18px; color: #ddd;">भारत का No.1 AI ऑटोमेशन ब्लॉग</p>
    </header>
    {header_menu}
    <div class="container">
        <h1 style="color: #111; font-size: 32px; border-bottom: 1px solid #eee; padding-bottom: 15px;">{current_topic}</h1>
        <p style="color: #777; font-size: 14px; text-transform: uppercase; letter-spacing: 1px;">📅 Published: {today_date}</p>
        <img src="{main_img_url}" class="main-img" alt="Blog Main Image">
        {blog_content}
    </div>
    {footer_html}
</body>
</html>"""

with open(post_filename, "w", encoding="utf-8") as f:
    f.write(article_html)

post_links = ""
for post in posts_db:
    post_links += f"""
    <div style="background: white; padding: 25px; margin-bottom: 25px; border-radius: 8px; border: 1px solid #eee; transition: 0.3s; display: flex; flex-direction: column;">
        <h3 style="margin: 0 0 10px 0; font-size: 22px;"><a href="{post['file']}" style="color: #203a43; text-decoration: none;">{post['title']}</a></h3>
        <p style="color: #777; margin: 0 0 15px 0; font-size: 14px;">📅 {post['date']}</p>
        <a href="{post['file']}" style="background: #203a43; color: white; padding: 10px 20px; text-decoration: none; font-weight: bold; border-radius: 5px; width: fit-content;">📖 पूरा लेख पढ़ें</a>
    </div>
    """

homepage_html = f"""<!DOCTYPE html>
<html lang="hi">
<head>
    <meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Digital Kamai Hub | Home</title>
    <style>
        body {{ font-family: 'Segoe UI', Tahoma, sans-serif; background: #f8f9fa; margin: 0; color: #333; }}
        header {{ background: linear-gradient(135deg, #0f2027, #203a43, #2c5364); color: white; padding: 50px 20px; text-align: center; }}
        header h1 {{ margin: 0; font-size: 42px; color: #f1c40f; }}
        .container {{ max-width: 850px; margin: 40px auto; padding: 20px; }}
    </style>
</head>
<body>
    <header>
        <h1>🚀 Digital Kamai Hub</h1>
        <p style="font-size: 20px; color: #ddd;">भारत का No.1 AI ऑटोमेशन ब्लॉग</p>
    </header>
    {header_menu}
    <div class="container">
        <h2 style="color: #203a43; border-left: 4px solid #f1c40f; padding-left: 15px; font-size: 28px; margin-bottom: 30px;">ताज़ा लेख (Latest Posts)</h2>
        {post_links}
    </div>
    {footer_html}
</body>
</html>"""

with open("index.html", "w", encoding="utf-8") as f:
    f.write(homepage_html)
