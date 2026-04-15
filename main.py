import urllib.request
import urllib.parse
import json
import os
import sys
import time

# ==========================================
# THE IMMORTAL SYSTEM - MULTIMEDIA AGENT (v25.0)
# Text-to-Speech (TTS) & Auto Video Embedding
# ==========================================

raw_key = os.environ.get("GEMINI_API_KEY", "")
API_KEY = raw_key.strip()
if not API_KEY: sys.exit(1)

current_year = time.strftime("%Y")
today_date = time.strftime("%d %B %Y")
post_id = int(time.time())

# 1. Memory Load
posts_db = []
past_titles = []
if os.path.exists("posts.json"):
    with open("posts.json", "r", encoding="utf-8") as f:
        try:
            posts_db = json.load(f)
            past_titles = [post["title"] for post in posts_db][:20] 
        except: pass

list_url = f"https://generativelanguage.googleapis.com/v1beta/models?key={API_KEY}"
available_model = None
try:
    req = urllib.request.Request(list_url)
    with urllib.request.urlopen(req, timeout=30) as response:
        res = json.loads(response.read().decode('utf-8'))
        for m in res.get('models', []):
            if 'generateContent' in m.get('supportedGenerationMethods', []) and 'gemini-1.5' in m.get('name', '').lower():
                available_model = m['name']
                break
        if not available_model: available_model = "models/gemini-1.5-flash"
except: available_model = "models/gemini-1.5-flash"

api_url = f"https://generativelanguage.googleapis.com/v1beta/{available_model}:generateContent?key={API_KEY}"

# ---------------------------------------------------------
# STEP 1: TOPIC RESEARCH
# ---------------------------------------------------------
topic_prompt = f"तुम एक ट्रेंड-एनालिस्ट AI हो। {current_year} में ऑनलाइन कमाई और AI के क्षेत्र में क्या सबसे ज्यादा सर्च हो रहा है? एक वायरल ब्लॉग टाइटल दो जो इनसे अलग हो: {past_titles}। सिर्फ टाइटल लिखना।"

try:
    req = urllib.request.Request(api_url, data=json.dumps({"contents": [{"parts": [{"text": topic_prompt}]}]}).encode('utf-8'), headers={'Content-Type': 'application/json'})
    with urllib.request.urlopen(req, timeout=50) as response:
        res = json.loads(response.read().decode('utf-8'))
        current_topic = res['candidates'][0]['content']['parts'][0]['text'].strip().replace('"', '').replace("'", "")
except: sys.exit(1)

# ---------------------------------------------------------
# STEP 2: MULTIMEDIA AUTONOMOUS LOOP
# ---------------------------------------------------------
success = False
final_data = {}

for attempt in range(10):
    print(f"🤖 [मल्टीमीडिया एजेंट] कोशिश {attempt+1}: वीडियो और टेक्स्ट सेट कर रहा हूँ...")
    
    master_prompt = f"""तुम एक प्रोफेशनल AI एजेंट हो। विषय: '{current_topic}'।
तुम्हें इस आर्टिकल का पूरा लॉजिक, SEO, इमेजेज और वीडियो खुद तय करना है।

नियम:
1. फोटो के लिए: <img src="https://image.pollinations.ai/prompt/DYNAMIC_KEYWORD?width=800&height=400&nologo=true" class="article-img"> (2-3 बार लगाओ)
2. वीडियो के लिए: लेख में जहाँ वीडियो की ज़रूरत हो, वहाँ यह कोड लगाओ: <iframe width="100%" height="315" src="https://www.youtube.com/embed?listType=search&list=ENGLISH_KEYWORD" frameborder="0" allowfullscreen class="article-video"></iframe> (ENGLISH_KEYWORD में टॉपिक से जुड़ा इंग्लिश शब्द डालो)।
3. लेख {current_year} के हिसाब से एकदम आधुनिक होना चाहिए।

मुझे सिर्फ इस JSON फॉर्मेट में जवाब दो:
{{
  "meta_desc": "SEO के लिए 150 शब्दों का हिंदी डिस्क्रिप्शन",
  "keywords": "5-6 कॉमा सेपरेटेड कीवर्ड्स",
  "main_img_prompt": "मुख्य फोटो के लिए 3-4 इंग्लिश शब्द",
  "html_body": "पूरा HTML कंटेंट (h2, p, ul, tags, तस्वीरें और वीडियो)"
}}"""

    try:
        req = urllib.request.Request(api_url, data=json.dumps({"contents": [{"parts": [{"text": master_prompt}]}], "generationConfig": {"response_mime_type": "application/json"}}).encode('utf-8'), headers={'Content-Type': 'application/json'})
        with urllib.request.urlopen(req, timeout=90) as response:
            res = json.loads(response.read().decode('utf-8'))
            raw_json = res['candidates'][0]['content']['parts'][0]['text']
            final_data = json.loads(raw_json)
            
            if all(k in final_data for k in ["meta_desc", "keywords", "main_img_prompt", "html_body"]) and len(final_data["html_body"]) > 500:
                success = True
                break
    except Exception as e:
        print(f"⚠️ सुधार हो रहा है: {e}")
        time.sleep(10)

if not success: sys.exit(1)

# ---------------------------------------------------------
# STEP 3: PUBLISHING WITH TEXT-TO-SPEECH (TTS) ENGINE
# ---------------------------------------------------------
main_img_url = f"https://image.pollinations.ai/prompt/{urllib.parse.quote(final_data['main_img_prompt'])}?width=800&height=400&nologo=true"
post_filename = f"post_{post_id}.html"

posts_db.insert(0, {"title": current_topic, "file": post_filename, "date": today_date})
with open("posts.json", "w", encoding="utf-8") as f:
    json.dump(posts_db, f, ensure_ascii=False, indent=4)

full_html = f"""<!DOCTYPE html>
<html lang="hi">
<head>
    <meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{current_topic} | Digital Kamai Hub</title>
    <meta name="description" content="{final_data['meta_desc']}">
    <meta name="keywords" content="{final_data['keywords']}">
    <style>
        body {{ font-family: 'Segoe UI', Tahoma, sans-serif; background: #f4f7f9; margin: 0; color: #333; }}
        header {{ background: #1a2a3a; color: white; padding: 40px 20px; text-align: center; }}
        nav {{ background: white; padding: 15px; text-align: center; position: sticky; top: 0; box-shadow: 0 2px 5px rgba(0,0,0,0.1); z-index: 100; }}
        nav a {{ color: #1a2a3a; text-decoration: none; margin: 0 15px; font-weight: bold; }}
        .container {{ max-width: 850px; margin: 30px auto; background: white; padding: 40px; border-radius: 10px; box-shadow: 0 5px 20px rgba(0,0,0,0.05); }}
        .article-img, .article-video {{ width: 100%; border-radius: 10px; margin: 25px 0; box-shadow: 0 4px 12px rgba(0,0,0,0.1); }}
        h1 {{ color: #1a2a3a; font-size: 34px; line-height: 1.4; }}
        h2 {{ color: #2c3e50; border-left: 5px solid #3498db; padding-left: 15px; margin-top: 35px; }}
        p {{ line-height: 1.8; font-size: 18px; color: #444; }}
        .tts-btn {{ background: linear-gradient(135deg, #3498db, #2980b9); color: white; border: none; padding: 12px 25px; border-radius: 50px; cursor: pointer; font-size: 16px; font-weight: bold; display: inline-flex; align-items: center; gap: 10px; box-shadow: 0 4px 10px rgba(52, 152, 219, 0.3); transition: 0.3s; margin-bottom: 20px; }}
        .tts-btn:hover {{ transform: scale(1.05); }}
        footer {{ background: #111; color: #888; text-align: center; padding: 40px; margin-top: 50px; }}
    </style>
</head>
<body>
    <header><h1>🚀 Digital Kamai Hub</h1><p>The Future of AI Automation</p></header>
    <nav><a href="index.html">🏠 होम</a><a href="index.html">🔥 लेटेस्ट न्यूज़</a></nav>
    <div class="container">
        <h1>{current_topic}</h1>
        <p style="color:#999;">📅 {today_date}</p>
        
        <button class="tts-btn" onclick="speakArticle()" id="speakBtn">🔊 लेख सुनें (Listen)</button>
        
        <img src="{main_img_url}" class="article-img" alt="Main Header">
        
        <div id="article-content">
            {final_data['html_body']}
        </div>
    </div>
    <footer>
        <p>&copy; 2026 Digital Kamai Hub</p>
    </footer>

    <script>
        let isPlaying = false;
        let speech = new SpeechSynthesisUtterance();
        
        function speakArticle() {{
            if (isPlaying) {{
                window.speechSynthesis.cancel();
                document.getElementById("speakBtn").innerHTML = "🔊 लेख सुनें (Listen)";
                isPlaying = false;
            }} else {{
                let textToRead = document.getElementById("article-content").innerText;
                speech.text = textToRead;
                speech.lang = 'hi-IN'; // हिंदी आवाज़
                speech.rate = 0.9; // पढ़ने की स्पीड (थोड़ी नेचुरल)
                window.speechSynthesis.speak(speech);
                document.getElementById("speakBtn").innerHTML = "⏹️ सुनना बंद करें (Stop)";
                isPlaying = true;

                speech.onend = function() {{
                    document.getElementById("speakBtn").innerHTML = "🔊 लेख सुनें (Listen)";
                    isPlaying = false;
                }};
            }}
        }}
    </script>
</body>
</html>"""

with open(post_filename, "w", encoding="utf-8") as f:
    f.write(full_html)

# Homepage Update
post_links = "".join([f'<div style="background:white; padding:20px; margin-bottom:20px; border-radius:10px; border:1px solid #eee;"><h3><a href="{p["file"]}" style="color:#1a2a3a; text-decoration:none;">{p["title"]}</a></h3><p style="color:#666;">📅 {p["date"]}</p></div>' for p in posts_db])
with open("index.html", "w", encoding="utf-8") as f:
    f.write(f'<!DOCTYPE html><html lang="hi"><head><meta charset="UTF-8"><title>Digital Kamai Hub</title><style>body{{font-family:sans-serif; background:#f4f7f9; margin:0;}} header{{background:#1a2a3a; color:white; padding:50px; text-align:center;}} .container{{max-width:800px; margin:30px auto; padding:20px;}}</style></head><body><header><h1>🚀 Digital Kamai Hub</h1></header><div class="container"><h2>ताज़ा लेख</h2>{post_links}</div></body></html>')
