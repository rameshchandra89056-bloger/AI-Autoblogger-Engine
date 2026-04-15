import urllib.request
import urllib.parse
import json
import os
import sys
import time

# ==========================================
# THE IMMORTAL SYSTEM - HYBRID ENGINE (v26.0)
# Unbreakable Text Parser + TTS + Auto Video
# ==========================================

raw_key = os.environ.get("GEMINI_API_KEY", "")
API_KEY = raw_key.strip()
if not API_KEY: sys.exit(1)

current_year = time.strftime("%Y")
today_date = time.strftime("%d %B %Y")
post_id = int(time.time())

# 1. डेटाबेस लोड
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
            if 'generateContent' in m.get('supportedGenerationMethods', []) and 'gemini' in m.get('name', '').lower():
                available_model = m['name']
                if 'flash' in available_model: break
except: pass
if not available_model: sys.exit(1)

api_url = f"https://generativelanguage.googleapis.com/v1beta/{available_model}:generateContent?key={API_KEY}"

# ---------------------------------------------------------
# STEP 1: TOPIC RESEARCH (नया टॉपिक खोजना)
# ---------------------------------------------------------
topic_prompt = f"तुम एक ट्रेंड-एनालिस्ट हो। {current_year} में ऑनलाइन कमाई और AI के क्षेत्र में एक नया वायरल ब्लॉग टाइटल (हिंदी में) दो। पुराने टाइटल्स: {past_titles} से अलग हो। सिर्फ 'टाइटल' लिखना।"

try:
    req = urllib.request.Request(api_url, data=json.dumps({"contents": [{"parts": [{"text": topic_prompt}]}]}).encode('utf-8'), headers={'Content-Type': 'application/json'})
    with urllib.request.urlopen(req, timeout=50) as response:
        res = json.loads(response.read().decode('utf-8'))
        current_topic = res['candidates'][0]['content']['parts'][0]['text'].strip().replace('"', '').replace("'", "")
except: sys.exit(1)

if not current_topic: sys.exit(1)

# ---------------------------------------------------------
# STEP 2: MULTIMEDIA TERMINATOR LOOP
# ---------------------------------------------------------
success = False
main_img_words = ""
meta_desc = ""
meta_keywords = ""
blog_content = ""

for attempt in range(10):
    print(f"\n🔄 [ATTEMPT {attempt + 1}/10] रोबोट मल्टीमीडिया आर्टिकल लिख रहा है...")
    try:
        content_prompt = f"""तुम एक प्रो ब्लॉगर हो। विषय: '{current_topic}'।
नियम:
1. लेख में 2-3 फोटो के लिए यह कोड लगाओ: <img src="https://image.pollinations.ai/prompt/YOUR_KEYWORD?width=800&height=400&nologo=true" class="article-img"> (YOUR_KEYWORD की जगह कोई 1 इंग्लिश शब्द लिखो)।
2. लेख के बीच में 1 यूट्यूब वीडियो के लिए यह कोड लगाओ: <iframe class="article-video" src="https://www.youtube.com/embed?listType=search&list=ENGLISH_SEARCH_QUERY" frameborder="0" allowfullscreen></iframe> (ENGLISH_SEARCH_QUERY की जगह टॉपिक से जुड़ा इंग्लिश शब्द डालो)।
3. जवाब सिर्फ नीचे दिए गए 4 बॉक्स में देना:

[MAIN_IMG]
(मुख्य फोटो के लिए 3 इंग्लिश शब्द)
[/MAIN_IMG]

[META_DESC]
(2 लाइन का SEO डिस्क्रिप्शन)
[/META_DESC]

[KEYWORDS]
(5 SEO कीवर्ड्स)
[/KEYWORDS]

[HTML_CONTENT]
(यहाँ पूरा HTML लेख फोटो और वीडियो कोड के साथ)
[/HTML_CONTENT]"""
        
        req = urllib.request.Request(api_url, data=json.dumps({"contents": [{"parts": [{"text": content_prompt}]}]}).encode('utf-8'), headers={'Content-Type': 'application/json'})
        with urllib.request.urlopen(req, timeout=90) as response:
            res = json.loads(response.read().decode('utf-8'))
            full_text = res['candidates'][0]['content']['parts'][0]['text']

        # बुलेटप्रूफ टेक्स्ट पार्सर
        def get_section(start_tag, end_tag):
            if start_tag in full_text and end_tag in full_text:
                return full_text.split(start_tag)[1].split(end_tag)[0].strip()
            return ""

        main_img_words = get_section("[MAIN_IMG]", "[/MAIN_IMG]")
        meta_desc = get_section("[META_DESC]", "[/META_DESC]")
        meta_keywords = get_section("[KEYWORDS]", "[/KEYWORDS]")
        blog_content = get_section("[HTML_CONTENT]", "[/HTML_CONTENT]")

        if not blog_content or len(blog_content) < 300:
            print("⚠️ कंटेंट सही नहीं आया। दोबारा कोशिश...")
            time.sleep(10)
            continue

        blog_content = blog_content.replace("```html", "").replace("```", "").strip()
        print("✅ 100% परफेक्ट कंटेंट मिल गया!")
        success = True
        break

    except Exception as e:
        print(f"⚠️ एरर: {e}। रिकवर कर रहा हूँ...")
        time.sleep(10)

if not success: sys.exit(1)

# ---------------------------------------------------------
# STEP 3: PUBLISHING & TEXT-TO-SPEECH
# ---------------------------------------------------------
main_img_safe = urllib.parse.quote(main_img_words)
main_img_url = f"https://image.pollinations.ai/prompt/{main_img_safe}?width=800&height=400&nologo=true"

post_filename = f"post_{post_id}.html"
posts_db.insert(0, {"title": current_topic, "file": post_filename, "date": today_date})

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
        <p>&copy; 2026 Digital Kamai Hub</p>
    </footer>
"""

full_html = f"""<!DOCTYPE html>
<html lang="hi">
<head>
    <meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{current_topic} | Digital Kamai Hub</title>
    <meta name="description" content="{meta_desc}">
    <meta name="keywords" content="{meta_keywords}">
    <style>
        body {{ font-family: 'Segoe UI', Tahoma, sans-serif; background: #f4f7f9; margin: 0; color: #333; }}
        header {{ background: #1a2a3a; color: white; padding: 40px 20px; text-align: center; }}
        nav {{ background: white; padding: 15px; text-align: center; position: sticky; top: 0; box-shadow: 0 2px 5px rgba(0,0,0,0.1); z-index: 100; }}
        nav a {{ color: #1a2a3a; text-decoration: none; margin: 0 15px; font-weight: bold; }}
        .container {{ max-width: 850px; margin: 30px auto; background: white; padding: 40px; border-radius: 10px; box-shadow: 0 5px 20px rgba(0,0,0,0.05); }}
        .article-img, .article-video {{ width: 100%; border-radius: 10px; margin: 25px 0; box-shadow: 0 4px 12px rgba(0,0,0,0.1); }}
        .article-video {{ height: 400px; }}
        h1 {{ color: #1a2a3a; font-size: 34px; line-height: 1.4; }}
        h2 {{ color: #2c3e50; border-left: 5px solid #3498db; padding-left: 15px; margin-top: 35px; }}
        p {{ line-height: 1.8; font-size: 18px; color: #444; }}
        .tts-btn {{ background: linear-gradient(135deg, #3498db, #2980b9); color: white; border: none; padding: 12px 25px; border-radius: 50px; cursor: pointer; font-size: 16px; font-weight: bold; display: inline-flex; align-items: center; gap: 10px; box-shadow: 0 4px 10px rgba(52, 152, 219, 0.3); transition: 0.3s; margin-bottom: 20px; }}
        .tts-btn:hover {{ transform: scale(1.05); }}
        @media (max-width: 600px) {{ .article-video {{ height: 250px; }} }}
    </style>
</head>
<body>
    <header><h1>🚀 Digital Kamai Hub</h1><p>The Future of AI Automation</p></header>
    {header_menu}
    <div class="container">
        <h1>{current_topic}</h1>
        <p style="color:#999;">📅 {today_date}</p>
        
        <button class="tts-btn" onclick="speakArticle()" id="speakBtn">🔊 लेख सुनें (Listen)</button>
        <img src="{main_img_url}" class="article-img" alt="Main Header">
        
        <div id="article-content">
            {blog_content}
        </div>
    </div>
    {footer_html}

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
                speech.lang = 'hi-IN';
                speech.rate = 0.9;
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

post_links = "".join([f'<div style="background:white; padding:20px; margin-bottom:20px; border-radius:10px; border:1px solid #eee;"><h3><a href="{p["file"]}" style="color:#1a2a3a; text-decoration:none;">{p["title"]}</a></h3><p style="color:#666;">📅 {p["date"]}</p></div>' for p in posts_db])
with open("index.html", "w", encoding="utf-8") as f:
    f.write(f'<!DOCTYPE html><html lang="hi"><head><meta charset="UTF-8"><title>Digital Kamai Hub</title><style>body{{font-family:sans-serif; background:#f4f7f9; margin:0;}} header{{background:#1a2a3a; color:white; padding:50px; text-align:center;}} .container{{max-width:800px; margin:30px auto; padding:20px;}}</style></head><body><header><h1>🚀 Digital Kamai Hub</h1></header>{header_menu}<div class="container"><h2>ताज़ा लेख</h2>{post_links}</div>{footer_html}</body></html>')
