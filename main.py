import urllib.request
import json
import os
import sys

# Digital Kamai Hub - Hyper-Engine v5.0 (Super Stable)
API_KEY = os.environ.get("GEMINI_API_KEY")

if not API_KEY:
    print("❌ ERROR: API_KEY missing!")
    sys.exit(1)

def ask_ai():
    # हम दो अलग-अलग रास्तों की लिस्ट बना रहे हैं
    urls = [
        f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={API_KEY}",
        f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={API_KEY}"
    ]
    
    prompt = "तुम एक एक्सपर्ट ब्लॉगर हो। '2026 में ऑनलाइन पैसे कमाने के 5 गुप्त तरीके' पर एक जबरदस्त हिंदी ब्लॉग लिखो। नियम: सिर्फ HTML tags (h2, p, ul) देना। [PHOTO_1] और [PHOTO_2] सही जगह लगा देना।"
    data = {"contents": [{"parts": [{"text": prompt}]}]}

    for url in urls:
        try:
            print(f"🔄 AI से संपर्क करने की कोशिश (Path: {url.split('/')[3]})...")
            req = urllib.request.Request(url, data=json.dumps(data).encode('utf-8'), headers={'Content-Type': 'application/json'})
            with urllib.request.urlopen(req, timeout=30) as response:
                result = json.loads(response.read().decode('utf-8'))
                return result['candidates'][0]['content']['parts'][0]['text']
        except Exception as e:
            print(f"⚠️ Is raste par error aaya: {e}")
            continue # Agla rasta try karo
    return None

# जादू यहाँ शुरू होता है
blog_body = ask_ai()

if blog_body:
    blog_body = blog_body.replace("```html", "").replace("```", "").strip()
    img = '<img src="https://image.pollinations.ai/prompt/future_money_2026_digital_income" style="width:100%; border-radius:15px; margin:20px 0;">'
    blog_body = blog_body.replace("[PHOTO_1]", img).replace("[PHOTO_2]", img)

    final_page = f"""<!DOCTYPE html>
<html lang="hi">
<head>
    <meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Digital Kamai Hub</title>
    <style>
        body {{ font-family: sans-serif; margin: 0; background: #f0f2f5; }}
        header {{ background: linear-gradient(to right, #0056b3, #00a2ff); color: white; padding: 40px; text-align: center; border-bottom: 5px solid #ffdd57; }}
        nav {{ background: #004494; padding: 10px; text-align: center; }}
        nav a {{ color: white; margin: 0 15px; text-decoration: none; font-weight: bold; }}
        .box {{ max-width: 800px; margin: 30px auto; background: white; padding: 30px; border-radius: 15px; box-shadow: 0 5px 20px rgba(0,0,0,0.1); }}
        footer {{ background: #1a1a1a; color: white; text-align: center; padding: 30px; margin-top: 40px; }}
    </style>
</head>
<body>
    <header><h1>🚀 Digital Kamai Hub</h1><p>इंटरनेट से कमाई का असली अड्डा</p></header>
    <nav><a href="#">Home</a><a href="#">About</a><a href="#">Privacy</a></nav>
    <div class="box">{blog_body}</div>
    <footer><p>&copy; 2026 Digital Kamai Hub | Created by Ramesh Chandra</p></footer>
</body>
</html>"""

    with open("index.html", "w", encoding="utf-8") as f:
        f.write(final_page)
    print("✅ MUBARAK HO! Website update ho gayi!")
else:
    print("❌ Critical Error: AI ne jawab nahi diya.")
    sys.exit(1)
    
