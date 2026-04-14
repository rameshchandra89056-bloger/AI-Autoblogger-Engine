import urllib.request
import json
import urllib.error
import os
import sys

# Digital Kamai Hub Engine v3.0 (2026 Powerful Edition)
API_KEY = os.environ.get("GEMINI_API_KEY")

if not API_KEY:
    print("❌ ERROR: API_KEY missing in Secrets!")
    sys.exit(1)

# 2026 ka sabse fast aur stable model (Gemini 3 Flash)
url = f"https://generativelanguage.googleapis.com/v1/models/gemini-3-flash:generateContent?key={API_KEY}"

print("🚀 Digital Kamai Hub ka naya version 3.0 taiyar ho raha hai...")

master_prompt = """
तुम एक प्रोफेशनल SEO ब्लॉगर हो। '2026 में ऑनलाइन पैसे कमाने के 5 सबसे नए तरीके' पर एक शानदार हिंदी ब्लॉग लिखो।
नियम: 
1. सिर्फ HTML टैग्स (<h2>, <p>, <ul>) देना।
2. शुरुआत में [PHOTO_1] और अंत में [PHOTO_2] ज़रूर लिखना।
"""

data = {"contents": [{"parts": [{"text": master_prompt}]}]}

try:
    req = urllib.request.Request(url, data=json.dumps(data).encode('utf-8'), headers={'Content-Type': 'application/json'})
    with urllib.request.urlopen(req) as response:
        result = json.loads(response.read().decode('utf-8'))
        ai_content = result['candidates'][0]['content']['parts'][0]['text']
        ai_content = ai_content.replace("```html", "").replace("```", "").strip()
        
        # Super Sharp AI Images
        img1 = '<img src="https://image.pollinations.ai/prompt/futuristic_digital_money_earning_2026_professional" style="width:100%; border-radius:15px; margin:25px 0; box-shadow: 0 5px 15px rgba(0,0,0,0.2);">'
        ai_content = ai_content.replace("[PHOTO_1]", img1).replace("[PHOTO_2]", img1)
        
        # Professional SEO Branding Template
        full_html = f"""<!DOCTYPE html>
<html lang="hi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Digital Kamai Hub | 2026 Online Earnings</title>
    <style>
        body {{ font-family: 'Segoe UI', sans-serif; margin: 0; background: #f0f2f5; color: #333; }}
        header {{ background: linear-gradient(135deg, #0056b3, #00a2ff); color: white; padding: 50px 20px; text-align: center; border-bottom: 8px solid #ffdd57; }}
        header h1 {{ margin: 0; font-size: 38px; text-shadow: 2px 2px 4px rgba(0,0,0,0.3); }}
        nav {{ background: #004494; padding: 15px; text-align: center; position: sticky; top: 0; z-index: 100; }}
        nav a {{ color: white; margin: 0 20px; text-decoration: none; font-weight: bold; font-size: 16px; }}
        .container {{ max-width: 850px; margin: 40px auto; background: white; padding: 50px; border-radius: 20px; box-shadow: 0 15px 40px rgba(0,0,0,0.08); }}
        h2 {{ color: #0056b3; border-left: 5px solid #ffdd57; padding-left: 15px; margin-top: 40px; }}
        footer {{ background: #1a1a1a; color: #ccc; text-align: center; padding: 40px; margin-top: 60px; }}
    </style>
</head>
<body>
    <header>
        <h1>🚀 Digital Kamai Hub</h1>
        <p>2026 में इंटरनेट से कामयाबी का असली पता</p>
    </header>
    <nav>
        <a href="#">Home</a>
        <a href="#">AdSense Guide</a>
        <a href="#">Privacy Policy</a>
    </nav>
    <div class="container">{ai_content}</div>
    <footer>
        <p>&copy; 2026 Digital Kamai Hub - Ramesh Chandra Enterprises</p>
        <p>Aapki Digital Pragati, Hamara Lakshya</p>
    </footer>
</body>
</html>"""

        with open("index.html", "w", encoding="utf-8") as f:
            f.write(full_html)
        print("✅ SUCCESS: index.html has been updated with v3.0 branding!")

except Exception as e:
    print(f"❌ CRITICAL ERROR: {str(e)}")
    sys.exit(1)
    
