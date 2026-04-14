import urllib.request
import json
import os
import sys

# ==========================================
# DIGITAL KAMAI HUB - ENGINE v7.0 (ULTRASONIC)
# ==========================================

API_KEY = os.environ.get("GEMINI_API_KEY")

def call_ai():
    # 2026 के सबसे ताज़ा और स्टेबल पते (Endpoints)
    endpoints = [
        f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={API_KEY}",
        f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={API_KEY}"
    ]
    
    payload = {
        "contents": [{"parts": [{"text": "तुम एक प्रो ब्लॉगर हो। '2026 में ऑनलाइन पैसे कमाने के 5 बेस्ट तरीके' पर एक प्रीमियम हिंदी लेख लिखो। सिर्फ HTML tags (h2, p, ul) देना। [IMAGE] टैग 2 बार लगाओ।"}]}]
    }

    for url in endpoints:
        try:
            print(f"🔄 कोशिश कर रहा हूँ: {url.split('/')[3]}...")
            req = urllib.request.Request(url, data=json.dumps(payload).encode('utf-8'), headers={'Content-Type': 'application/json'})
            with urllib.request.urlopen(req, timeout=30) as response:
                res = json.loads(response.read().decode('utf-8'))
                return res['candidates'][0]['content']['parts'][0]['text']
        except Exception as e:
            print(f"⚠️ इस रास्ते पर दिक्कत आई: {e}")
            continue
    return None

# वेबसाइट का लग्जरी लुक (v7.0)
def build_site(body_text):
    body_text = body_text.replace("```html", "").replace("```", "").strip()
    img = '<img src="https://image.pollinations.ai/prompt/premium_digital_money_2026_aesthetic" style="width:100%; border-radius:25px; margin:30px 0; box-shadow: 0 10px 40px rgba(0,0,0,0.1);">'
    content = body_text.replace("[IMAGE]", img)

    return f"""<!DOCTYPE html>
<html lang="hi">
<head>
    <meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Digital Kamai Hub | 2026 Guide</title>
    <style>
        body {{ font-family: 'Inter', sans-serif; margin: 0; background: #ffffff; color: #1d1d1f; }}
        header {{ background: #000; color: #fff; padding: 20px; text-align: center; position: sticky; top: 0; z-index: 100; }}
        header h1 {{ margin: 0; font-size: 22px; font-weight: 600; letter-spacing: 1px; }}
        .hero {{ background: #f5f5f7; padding: 80px 20px; text-align: center; }}
        .hero h1 {{ font-size: 45px; font-weight: 800; margin: 0; }}
        .container {{ max-width: 750px; margin: -50px auto 50px; background: white; padding: 50px; border-radius: 30px; box-shadow: 0 20px 60px rgba(0,0,0,0.08); }}
        h2 {{ color: #0071e3; font-size: 28px; }}
        p {{ font-size: 19px; line-height: 1.8; color: #424245; }}
        footer {{ text-align: center; padding: 60px; background: #f5f5f7; color: #86868b; }}
    </style>
</head>
<body>
    <header><h1>🚀 DIGITAL KAMAI HUB</h1></header>
    <div class="hero">
        <h1>2026 की डिजिटल क्रांति</h1>
        <p>Ramesh Chandra की ओर से विशेष गाइड</p>
    </div>
    <div class="container">{content}</div>
    <footer>&copy; 2026 Digital Kamai Hub. All rights reserved.</footer>
</body>
</html>"""

# मुख्य इंजन
print("🛠️ Engine v7.0 Starting...")
article = call_ai()

if article:
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(build_site(article))
    print("✅ SUCCESS! अब अपनी वेबसाइट चेक करो!")
else:
    print("❌ Critical Failure: गूगल API जवाब नहीं दे रहा।")
    sys.exit(1)
    
