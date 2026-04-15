import urllib.request
import urllib.parse
import json
import os
import sys
import time

# ==========================================
# THE IMMORTAL SYSTEM - MASTER PLAN EDITION (v20.0)
# Day 10: AI Image Engine (Pollinations)
# Day 11-14: Advanced SEO & Meta Tags
# ==========================================

raw_key = os.environ.get("GEMINI_API_KEY", "")
API_KEY = raw_key.strip()

if not API_KEY:
    print("❌ ERROR: API Key गायब है!")
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

print("🔍 DIAGNOSTIC MODE: मॉडल ढूंढ रहे हैं...")
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
            sys.exit(1)
except Exception as e:
    sys.exit(1)

# ---------------------------------------------------------
# STEP 1: THE BRAIN (नया टॉपिक सोचना)
# ---------------------------------------------------------
topic_prompt = f"तुम एक SEO एक्सपर्ट हो। 'मेक मनी ऑनलाइन', 'AI टूल्स' या 'फ्रीलांसिंग' पर साल {current_year} का एक नया और वायरल ब्लॉग टाइटल (हिंदी में) दो। यह इन पुराने टाइटल्स से अलग होना चाहिए: {past_titles}। जवाब में सिर्फ 'टाइटल' लिखना।"
topic_data = {"contents": [{"parts": [{"text": topic_prompt}]}]}
topic_url = f"https://generativelanguage.googleapis.com/v1beta/{available_model}:generateContent?key={API_KEY}"

current_topic = ""
try:
    req = urllib.request.Request(topic_url, data=json.dumps(topic_data).encode('utf-8'), headers={'Content-Type': 'application/json'})
    with urllib.request.urlopen(req, timeout=50) as response:
        res = json.loads(response.read().decode('utf-8'))
        current_topic = res['candidates'][0]['content']['parts'][0]['text'].strip().replace('"', '').replace("'", "")
except:
    sys.exit(1)

if not current_topic:
    sys.exit(1)

# ---------------------------------------------------------
# STEP 2: DAY 10 - AI IMAGE ENGINE (Pollinations Fix)
# रोबोट पहले टॉपिक को इंग्लिश में ट्रांसलेट करेगा ताकि Pollinations क्रैश न हो!
# ---------------------------------------------------------
print("📸 AI Image Engine: Pollinations के लिए इंग्लिश प्रॉम्प्ट बना रहे हैं...")
img_prompt_req = f"Translate this blog title into a highly descriptive, futuristic 5-word English prompt for an AI image generator: '{current_topic}'. Return ONLY the English words, no extra text."
img_data = {"contents": [{"parts": [{"text": img_prompt_req}]}]}

english_img_prompt = "futuristic digital technology success" # Default fallback
try:
    req = urllib.request.Request(topic_url, data=json.dumps(img_data).encode('utf-8'), headers={'Content-Type': 'application/json'})
    with urllib.request.urlopen(req, timeout=30) as response:
        res = json.loads(response.read().decode('utf-8'))
        english_img_prompt = res['candidates'][0]['content']['parts'][0]['text'].strip()
except:
    pass

safe_keyword = urllib.parse.quote(english_img_prompt)
dynamic_img_url = f"https://image.pollinations.ai/prompt/{safe_keyword}?width=800&height=400&nologo=true"

# ---------------------------------------------------------
# STEP 3: DAY 11-14 - ADVANCED SEO & CONTENT
# ---------------------------------------------------------
print("✍️ SEO Engine: कंटेंट और Meta Tags लिख रहे हैं...")
content_prompt = f"""तुम एक प्रो ब्लॉगर और SEO एक्सपर्ट हो। 
विषय: '{current_topic}'
नियम: 
1. यह साल {current_year} है, हर जानकारी {current_year} की होनी चाहिए।
2. मुझे जवाब इस फॉर्मेट में चाहिए (बिना किसी अतिरिक्त बातचीत के):
META_DESC: (यहाँ 2 लाइन का धांसू SEO डिस्क्रिप्शन लिखें)
KEYWORDS: (यहाँ 5-6 SEO कीवर्ड्स कॉमा लगाकर लिखें)
CONTENT: (यहाँ से पूरा HTML ब्लॉग h2, p, ul, strong के साथ शुरू करें)"""

content_data = {"contents": [{"parts": [{"text": content_prompt}]}]}

full_response = ""
try:
    req = urllib.request.Request(topic_url, data=json.dumps(content_data).encode('utf-8'), headers={'Content-Type': 'application/json'})
    with urllib.request.urlopen(req, timeout=60) as response:
        res = json.loads(response.read().decode('utf-8'))
        full_response = res['candidates'][0]['content']['parts'][0]['text']
except:
    sys.exit(1)

# AI के जवाब को 3 हिस्सों में काटना (SEO और Content)
meta_desc = "Digital Kamai Hub - भारत का No.1 AI ऑटोमेशन ब्लॉग"
meta_keywords = "AI, Make Money, Technology, 2026"
blog_content = full_response

try:
    parts = full_response.split("CONTENT:")
    seo_part = parts[0]
    blog_content = parts[1].replace("```html", "").replace("```", "").strip()
    
    if "META_DESC:" in seo_part:
        meta_desc = seo_part.split("META_DESC:")[1].split("KEYWORDS:")[0].strip()
    if "KEYWORDS:" in seo_part:
        meta_keywords = seo_part.split("KEYWORDS:")[1].strip()
except:
    pass

# ---------------------------------------------------------
# STEP 4: DATABASE & PROFESSIONAL HTML DESIGN
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

# HTML में SEO Tags जोड़े गए हैं (<meta name="description" ...>)
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
        img {{ width: 100%; border-radius: 8px; margin: 20px 0; object-fit: cover; box-shadow: 0 4px 10px rgba(0,0,0,0.1); background-color: #0f2027; min-height: 250px; }}
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
        <img src="{dynamic_img_url}" alt="AI Generated Image from Pollinations">
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
