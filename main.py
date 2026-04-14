import urllib.request
import json
import os
import sys
import time

# ==========================================
# DIGITAL KAMAI HUB - FULLY AUTONOMOUS ENGINE
# ==========================================

raw_key = os.environ.get("GEMINI_API_KEY", "")
API_KEY = raw_key.strip()

if not API_KEY:
    print("❌ ERROR: API Key गायब है!")
    sys.exit(1)

# 1. रोबोट की याददाश्त (Memory) लोड करना
posts_db = []
past_titles = []
if os.path.exists("posts.json"):
    with open("posts.json", "r", encoding="utf-8") as f:
        try:
            posts_db = json.load(f)
            # पिछले 20 आर्टिकल्स की लिस्ट निकाल रहे हैं ताकि AI को बता सकें कि क्या नहीं लिखना है
            past_titles = [post["title"] for post in posts_db][:20] 
        except:
            pass

print("🔍 DIAGNOSTIC MODE: सबसे अच्छा AI मॉडल ढूंढ रहे हैं...")
list_url = f"https://generativelanguage.googleapis.com/v1beta/models?key={API_KEY}"
available_model = None

try:
    req = urllib.request.Request(list_url)
    with urllib.request.urlopen(req, timeout=30) as response:
        res = json.loads(response.read().decode('utf-8'))
        models = res.get('models', [])
        for m in models:
            if 'generateContent' in m.get('supportedGenerationMethods', []) and 'gemini' in m.get('name', '').lower():
                available_model = m['name']
                if 'flash' in available_model:
                    break
        if not available_model:
            print("❌ ERROR: कोई मॉडल नहीं मिला।")
            sys.exit(1)
except Exception as e:
    print(f"❌ API Error: {e}")
    sys.exit(1)

# 2. THE BRAIN: खुद इंटरनेट/डेटाबेस से ट्रेंडिंग टॉपिक सोचना
print("🧠 रोबोट खुद एक नया और ट्रेंडिंग टॉपिक सोच रहा है...")
topic_prompt = f"""तुम एक एक्सपर्ट SEO रिसर्चर हो। 'मेक मनी ऑनलाइन', 'AI टूल्स', 'फ्रीलांसिंग' या 'यूट्यूब ग्रोथ' से जुड़ा आज का सबसे ट्रेंडिंग और वायरल ब्लॉग टाइटल (हिंदी में) बताओ। 
नियम: यह टाइटल इन पुराने टाइटल्स से बिल्कुल अलग होना चाहिए: {past_titles}। 
जवाब में सिर्फ और सिर्फ एक 'टाइटल' लिखना, कोई और शब्द नहीं।"""

topic_data = {"contents": [{"parts": [{"text": topic_prompt}]}]}
topic_url = f"https://generativelanguage.googleapis.com/v1beta/{available_model}:generateContent?key={API_KEY}"

current_topic = ""
try:
    req = urllib.request.Request(topic_url, data=json.dumps(topic_data).encode('utf-8'), headers={'Content-Type': 'application/json'})
    with urllib.request.urlopen(req, timeout=50) as response:
        res = json.loads(response.read().decode('utf-8'))
        current_topic = res['candidates'][0]['content']['parts'][0]['text'].strip()
        current_topic = current_topic.replace('"', '').replace("'", "") # फालतू निशान हटाना
        print(f"🎯 रोबोट ने नया ट्रेंडिंग टॉपिक चुना: {current_topic}")
except Exception as e:
    print(f"❌ टॉपिक चुनने में एरर: {e}")
    sys.exit(1)

if not current_topic:
    sys.exit(1)

# 3. कंटेंट लिखना
print("✍️ रोबोट ब्लॉग लिख रहा है...")
content_prompt = f"तुम एक प्रो ब्लॉगर हो। '{current_topic}' पर एक शानदार और विस्तृत हिंदी लेख लिखो। सिर्फ HTML tags (h2, p, ul, strong) देना। ```html या body tags मत लगाना।"
content_data = {"contents": [{"parts": [{"text": content_prompt}]}]}

blog_content = None
try:
    req = urllib.request.Request(topic_url, data=json.dumps(content_data).encode('utf-8'), headers={'Content-Type': 'application/json'})
    with urllib.request.urlopen(req, timeout=60) as response:
        res = json.loads(response.read().decode('utf-8'))
        blog_content = res['candidates'][0]['content']['parts'][0]['text']
        print("✅ SUCCESS! ब्लॉग लिख लिया गया है।")
except Exception as e:
    print(f"❌ कंटेंट लिखने में एरर: {e}")
    sys.exit(1)

if not blog_content:
    sys.exit(1)

blog_content = blog_content.replace("```html", "").replace("```", "").strip()

# 4. डेटाबेस सेव करना
post_id = int(time.time())
post_filename = f"post_{post_id}.html"
today_date = time.strftime("%d %B %Y")

new_post = {"title": current_topic, "file": post_filename, "date": today_date}
posts_db.insert(0, new_post)

with open("posts.json", "w", encoding="utf-8") as f:
    json.dump(posts_db, f, ensure_ascii=False, indent=4)

# ==========================================
# 5. PROFESSIONAL UI/UX DESIGN (आपका बताया हुआ)
# ==========================================

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

# आर्टिकल का पन्ना
article_html = f"""<!DOCTYPE html>
<html lang="hi">
<head>
    <meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{current_topic} | Digital Kamai Hub</title>
    <style>
        body {{ font-family: 'Segoe UI', Tahoma, sans-serif; background: #f8f9fa; margin: 0; color: #333; }}
        header {{ background: linear-gradient(135deg, #0f2027, #203a43, #2c5364); color: white; padding: 40px 20px; text-align: center; }}
        .container {{ max-width: 800px; margin: 40px auto; background: white; padding: 40px; border-radius: 8px; box-shadow: 0 2px 15px rgba(0,0,0,0.05); line-height: 1.8; font-size: 18px; }}
        h1 {{ color: #f1c40f; margin: 0; }}
        h2 {{ color: #203a43; border-left: 4px solid #f1c40f; padding-left: 15px; margin-top: 30px; }}
        img {{ width: 100%; border-radius: 8px; margin: 20px 0; }}
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
        <img src="[https://image.pollinations.ai/prompt/digital_growth_chart_laptop_2026](https://image.pollinations.ai/prompt/digital_growth_chart_laptop_2026)" alt="Blog Image">
        {blog_content}
    </div>
    {footer_html}
</body>
</html>"""

with open(post_filename, "w", encoding="utf-8") as f:
    f.write(article_html)

# होमपेज
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
    
