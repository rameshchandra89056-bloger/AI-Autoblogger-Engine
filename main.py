import urllib.request
import json
import os
import sys
import time
import random

# ==========================================
# DIGITAL KAMAI HUB - MULTI-PAGE ENGINE v13.0
# ==========================================

raw_key = os.environ.get("GEMINI_API_KEY", "")
API_KEY = raw_key.strip()

if not API_KEY:
    print("❌ ERROR: API Key गायब है!")
    sys.exit(1)

# गुरु के 5 शानदार टॉपिक्स (रोबोट हर बार इनमें से कोई एक नया टॉपिक खुद चुनेगा)
topics = [
    "2026 में यूट्यूब से पैसे कैसे कमाएं - फुल गाइड",
    "फ्रीलांसिंग से घर बैठे महीने का 1 लाख कैसे कमाएं",
    "ब्लॉगिंग कैसे शुरू करें और AdSense से कमाई कैसे करें",
    "ऑनलाइन एफिलिएट मार्केटिंग के सबसे बड़े सीक्रेट्स",
    "AI टूल्स (ChatGPT, Gemini) से पैसे कमाने के 5 तरीके"
]
current_topic = random.choice(topics)

def get_ai_blog(topic):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={API_KEY}"
    prompt = f"तुम एक प्रो ब्लॉगर हो। '{topic}' पर एक शानदार और विस्तृत हिंदी लेख लिखो। सिर्फ HTML tags (h2, p, ul, strong) देना।"
    data = {"contents": [{"parts": [{"text": prompt}]}]}

    print(f"🚀 AI से '{topic}' पर लेख लिखवा रहे हैं...")
    try:
        req = urllib.request.Request(url, data=json.dumps(data).encode('utf-8'), headers={'Content-Type': 'application/json'})
        with urllib.request.urlopen(req, timeout=50) as response:
            res = json.loads(response.read().decode('utf-8'))
            return res['candidates'][0]['content']['parts'][0]['text']
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

blog_content = get_ai_blog(current_topic)

if not blog_content:
    sys.exit(1)

blog_content = blog_content.replace("```html", "").replace("```", "").strip()

# 1. डेटाबेस (posts.json) को अपडेट करना - यह हमारी याददाश्त है!
posts_db = []
if os.path.exists("posts.json"):
    with open("posts.json", "r", encoding="utf-8") as f:
        posts_db = json.load(f)

# नई फाइल का नाम (Timestamp के हिसाब से ताकि कभी एक जैसा नाम न हो)
post_id = int(time.time())
post_filename = f"post_{post_id}.html"
today_date = time.strftime("%d %B %Y")

# नया डेटा लिस्ट में सबसे ऊपर जोड़ें
new_post = {"title": current_topic, "file": post_filename, "date": today_date}
posts_db.insert(0, new_post)

with open("posts.json", "w", encoding="utf-8") as f:
    json.dump(posts_db, f, ensure_ascii=False, indent=4)

# 2. नए ब्लॉग का HTML पेज बनाना (अंदर का पन्ना)
nav_menu = """
    <nav style="background: #1a1a1a; padding: 15px; text-align: center; position: sticky; top: 0; box-shadow: 0 2px 10px rgba(0,0,0,0.5);">
        <a href="index.html" style="color: white; text-decoration: none; margin: 0 15px; font-weight: bold;">🏠 Home</a>
        <a href="about.html" style="color: white; text-decoration: none; margin: 0 15px; font-weight: bold;">👤 About Us</a>
        <a href="privacy.html" style="color: white; text-decoration: none; margin: 0 15px; font-weight: bold;">🔒 Privacy Policy</a>
        <a href="disclaimer.html" style="color: white; text-decoration: none; margin: 0 15px; font-weight: bold;">⚠️ Disclaimer</a>
    </nav>
"""

article_html = f"""<!DOCTYPE html>
<html lang="hi">
<head>
    <meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{current_topic} | Digital Kamai Hub</title>
    <style>
        body {{ font-family: 'Segoe UI', Tahoma, sans-serif; background: #eef2f5; margin: 0; color: #2c3e50; }}
        header {{ background: linear-gradient(135deg, #0f2027, #203a43, #2c5364); color: white; padding: 40px 20px; text-align: center; }}
        .container {{ max-width: 800px; margin: 40px auto; background: white; padding: 40px; border-radius: 12px; box-shadow: 0 5px 15px rgba(0,0,0,0.1); line-height: 1.8; font-size: 18px; }}
        h1 {{ color: #f1c40f; margin: 0; }}
        h2 {{ color: #203a43; border-left: 5px solid #f1c40f; padding-left: 15px; margin-top: 30px; }}
        img {{ width: 100%; border-radius: 12px; margin: 20px 0; }}
        footer {{ text-align: center; padding: 30px; background: #1a1a1a; color: #ecf0f1; margin-top: 50px; }}
    </style>
</head>
<body>
    <header>
        <h1>🚀 Digital Kamai Hub</h1>
        <p>भारत का No.1 AI ऑटोमेशन ब्लॉग</p>
    </header>
    {nav_menu}
    <div class="container">
        <h1 style="color: #203a43; font-size: 32px; border-bottom: 2px solid #eee; padding-bottom: 10px;">{current_topic}</h1>
        <p style="color: #7f8c8d; font-size: 14px;">📅 Published on: {today_date}</p>
        <img src="https://image.pollinations.ai/prompt/digital_marketing_laptop_2026_aesthetic" alt="Blog Image">
        {blog_content}
    </div>
    <footer>&copy; 2026 Ramesh Chandra Enterprise</footer>
</body>
</html>"""

with open(post_filename, "w", encoding="utf-8") as f:
    f.write(article_html)
print(f"✅ नया ब्लॉग पन्ना बन गया: {post_filename}")

# 3. होमपेज (index.html) को अपडेट करना (ताकि सारे ब्लॉग्स की लिस्ट दिखे)
post_links = ""
for post in posts_db:
    post_links += f"""
    <div style="background: white; padding: 25px; margin-bottom: 25px; border-radius: 12px; box-shadow: 0 4px 10px rgba(0,0,0,0.05); transition: 0.3s;">
        <h3 style="margin: 0 0 10px 0; font-size: 24px;"><a href="{post['file']}" style="color: #203a43; text-decoration: none;">{post['title']}</a></h3>
        <p style="color: #7f8c8d; margin: 0 0 15px 0; font-size: 15px;">📅 {post['date']}</p>
        <a href="{post['file']}" style="background: #f1c40f; color: #1a1a1a; padding: 10px 20px; text-decoration: none; font-weight: bold; border-radius: 5px; display: inline-block;">📖 पूरा लेख पढ़ें ➔</a>
    </div>
    """

homepage_html = f"""<!DOCTYPE html>
<html lang="hi">
<head>
    <meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Digital Kamai Hub | Home</title>
    <style>
        body {{ font-family: 'Segoe UI', Tahoma, sans-serif; background: #eef2f5; margin: 0; color: #2c3e50; }}
        header {{ background: linear-gradient(135deg, #0f2027, #203a43, #2c5364); color: white; padding: 60px 20px; text-align: center; }}
        header h1 {{ margin: 0; font-size: 45px; color: #f1c40f; }}
        .container {{ max-width: 850px; margin: 40px auto; padding: 20px; }}
        footer {{ text-align: center; padding: 30px; background: #1a1a1a; color: #ecf0f1; margin-top: 50px; }}
    </style>
</head>
<body>
    <header>
        <h1>🚀 Digital Kamai Hub</h1>
        <p style="font-size: 20px;">भारत का No.1 AI ऑटोमेशन ब्लॉग</p>
    </header>
    {nav_menu}
    <div class="container">
        <h2 style="color: #203a43; border-left: 5px solid #f1c40f; padding-left: 15px; font-size: 30px; margin-bottom: 30px;">ताज़ा लेख (Latest Posts)</h2>
        {post_links}
    </div>
    <footer>&copy; 2026 Ramesh Chandra Enterprise | Never Give Up!</footer>
</body>
</html>"""

with open("index.html", "w", encoding="utf-8") as f:
    f.write(homepage_html)
print("✅ SUCCESS! होमपेज पर लिस्ट अपडेट हो गई है!")
    
