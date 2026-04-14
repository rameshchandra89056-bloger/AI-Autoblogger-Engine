import urllib.request
import json
import os
import sys

# ==========================================
# DIGITAL KAMAI HUB - ENGINE v6.0 (2026 PRO)
# ==========================================

API_KEY = os.environ.get("GEMINI_API_KEY")

def build_modern_blog():
    # 2026 ka sabse stable endpoint
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={API_KEY}"
    
    print("🚀 AI Engine v6.0 starts firing...")
    
    prompt = {
        "contents": [{
            "parts": [{
                "text": "तुम एक वर्ल्ड-क्लास ब्लॉगर हो। '2026 में बिना निवेश के पैसे कैसे कमाएं' पर एक प्रीमियम हिंदी लेख लिखो। सिर्फ HTML टैग्स (h2, p, ul) देना। [IMAGE] टैग का इस्तेमाल 2 बार करो।"
            }]
        }]
    }

    try:
        req = urllib.request.Request(url, data=json.dumps(prompt).encode('utf-8'), headers={'Content-Type': 'application/json'})
        with urllib.request.urlopen(req, timeout=30) as response:
            res_data = json.loads(response.read().decode('utf-8'))
            raw_text = res_data['candidates'][0]['content']['parts'][0]['text']
            return raw_text.replace("```html", "").replace("```", "").strip()
    except Exception as e:
        print(f"❌ Error during AI Call: {e}")
        return None

# वेबसाइट का नया और लग्जरी डिज़ाइन
def create_ui(content):
    img_tag = '<img src="https://image.pollinations.ai/prompt/wealth_luxury_digital_lifestyle_2026" style="width:100%; border-radius:20px; margin:30px 0; box-shadow: 0 10px 40px rgba(0,0,0,0.15);">'
    clean_content = content.replace("[IMAGE]", img_tag)

    html_code = f"""<!DOCTYPE html>
<html lang="hi">
<head>
    <meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Digital Kamai Hub | 2026 Money Guide</title>
    <style>
        :root {{ --primary: #0a84ff; --bg: #ffffff; --text: #1d1d1f; }}
        body {{ font-family: 'Inter', -apple-system, sans-serif; margin: 0; background: #f5f5f7; color: var(--text); }}
        header {{ background: rgba(255,255,255,0.8); backdrop-filter: blur(20px); padding: 20px; position: sticky; top: 0; z-index: 100; text-align: center; border-bottom: 1px solid #d2d2d7; }}
        header h1 {{ margin: 0; font-size: 24px; color: var(--primary); font-weight: 700; }}
        .hero {{ background: linear-gradient(135deg, #0071e3, #00c6fb); color: white; padding: 60px 20px; text-align: center; }}
        .container {{ max-width: 800px; margin: -40px auto 40px; background: white; padding: 50px; border-radius: 30px; box-shadow: 0 20px 60px rgba(0,0,0,0.05); }}
        h2 {{ color: var(--primary); font-size: 28px; margin-top: 40px; }}
        p {{ font-size: 18px; line-height: 1.8; color: #424245; }}
        footer {{ text-align: center; padding: 50px; color: #86868b; font-size: 14px; }}
    </style>
</head>
<body>
    <header><h1>🚀 Digital Kamai Hub</h1></header>
    <div class="hero">
        <h1 style="font-size: 48px;">इंटरनेट से कमाई का भविष्य</h1>
        <p style="color: rgba(255,255,255,0.9);">Ramesh Chandra की विशेष डिजिटल डायरी</p>
    </div>
    <div class="container">{clean_content}</div>
    <footer>
        <p>&copy; 2026 Digital Kamai Hub. All rights reserved.</p>
        <nav><a href="#" style="color:#0a84ff; text-decoration:none;">Privacy</a> | <a href="#" style="color:#0a84ff; text-decoration:none;">Terms</a></nav>
    </footer>
</body>
</html>"""
    return html_code

# Run Engine
article = build_modern_blog()
if article:
    final_web = create_ui(article)
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(final_web)
    print("✅ SUCCESS! Website is now Live and Branded.")
else:
    print("❌ Critical Failure. Please check API Key in GitHub Secrets.")
    sys.exit(1)
    
