import urllib.request
import json
import os
import sys

# ==========================================
# DIGITAL KAMAI HUB - THE ULTIMATE FIX v10.0
# ==========================================

# 1. गुरु का मास्टरस्ट्रोक: चाबी के आगे-पीछे का अदृश्य कचरा (Space/Enter) साफ़ करना
raw_key = os.environ.get("GEMINI_API_KEY", "")
API_KEY = raw_key.strip() # यह फंक्शन सारे अदृश्य स्पेस काट देगा

if not API_KEY:
    print("❌ ERROR: API Key गायब है!")
    sys.exit(1)

# Debugging: हम चेक करेंगे कि चाबी सही से लोड हुई या नहीं
print(f"🔍 Debug Info: आपकी चाबी एकदम सुरक्षित है और उसकी लंबाई {len(API_KEY)} अक्षर है।")

def get_ai_blog():
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={API_KEY}"
    prompt = "तुम एक प्रो ब्लॉगर हो। 'ऑनलाइन इंटरनेट से पैसे कैसे कमाएं' पर एक शानदार हिंदी लेख लिखो। सिर्फ HTML tags (h2, p, ul) देना।"
    data = {"contents": [{"parts": [{"text": prompt}]}]}

    print("🚀 गूगल के सर्वर से जुड़ रहे हैं...")
    try:
        req = urllib.request.Request(url, data=json.dumps(data).encode('utf-8'), headers={'Content-Type': 'application/json'})
        with urllib.request.urlopen(req, timeout=30) as response:
            res = json.loads(response.read().decode('utf-8'))
            print("✅ SUCCESS! गूगल ने सही जवाब दे दिया है!")
            return res['candidates'][0]['content']['parts'][0]['text']
    except urllib.error.HTTPError as e:
        print(f"❌ HTTP Error {e.code}: {e.reason}")
        return None
    except Exception as e:
        print(f"❌ Other Error: {e}")
        return None

def build_final_website(blog_text):
    blog_text = blog_text.replace("```html", "").replace("```", "").strip()
    
    return f"""<!DOCTYPE html>
<html lang="hi">
<head>
    <meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Digital Kamai Hub</title>
    <style>
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #eef2f5; margin: 0; color: #2c3e50; }}
        header {{ background: linear-gradient(135deg, #1e3c72, #2a5298); color: white; padding: 50px 20px; text-align: center; box-shadow: 0 4px 15px rgba(0,0,0,0.2); }}
        header h1 {{ margin: 0; font-size: 40px; letter-spacing: 1px; }}
        header p {{ font-size: 18px; opacity: 0.9; margin-top: 10px; }}
        .container {{ max-width: 850px; margin: 40px auto; background: white; padding: 50px; border-radius: 16px; box-shadow: 0 10px 30px rgba(0,0,0,0.08); line-height: 1.8; font-size: 18px; }}
        h2 {{ color: #1e3c72; margin-top: 40px; border-left: 5px solid #f39c12; padding-left: 15px; }}
        img {{ width: 100%; border-radius: 15px; margin: 25px 0; box-shadow: 0 8px 25px rgba(0,0,0,0.1); }}
        footer {{ text-align: center; padding: 30px; background: #1a1a1a; color: #ecf0f1; margin-top: 50px; font-size: 15px; }}
    </style>
</head>
<body>
    <header>
        <h1>🚀 Digital Kamai Hub</h1>
        <p>एक सफल सॉफ्टवेयर इंजीनियर का ड्रीम प्रोजेक्ट</p>
    </header>
    <div class="container">
        <img src="https://image.pollinations.ai/prompt/wealth_digital_lifestyle_2026_professional" alt="Digital Money">
        {blog_text}
    </div>
    <footer>&copy; 2026 Ramesh Chandra Enterprise | All Rights Reserved</footer>
</body>
</html>"""

# Main Execution
print("🛠️ Starting Engine v10.0...")
article = get_ai_blog()

if article:
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(build_final_website(article))
    print("🎉 MISSION ACCOMPLISHED! वेबसाइट 100% तैयार है!")
else:
    print("❌ Critical Failure.")
    sys.exit(1)
    
