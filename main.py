import urllib.request
import json
import os
import sys

# Digital Kamai Hub - Hyper-Engine v4.0 (2026 Stable)
API_KEY = os.environ.get("GEMINI_API_KEY")

def generate_blog():
    # इस बार हम 100% वर्किंग 'v1beta' रास्ते का इस्तेमाल कर रहे हैं
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={API_KEY}"
    
    print("🚀 AI Engine v4.0 chalu ho raha hai...")
    
    prompt = """
    तुम एक एक्सपर्ट ब्लॉगर हो। '2026 में ऑनलाइन पैसे कमाने के 5 गुप्त तरीके' पर एक जबरदस्त हिंदी ब्लॉग लिखो।
    नियम: सिर्फ HTML (<h2>, <p>, <ul>) देना। [PHOTO_1] और [PHOTO_2] सही जगह लगा देना।
    """
    
    data = {"contents": [{"parts": [{"text": prompt}]}]}
    
    try:
        req = urllib.request.Request(url, data=json.dumps(data).encode('utf-8'), headers={'Content-Type': 'application/json'})
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode('utf-8'))
            content = result['candidates'][0]['content']['parts'][0]['text']
            return content.replace("```html", "").replace("```", "").strip()
    except Exception as e:
        print(f"❌ API Error: {e}")
        return None

# मुख्य काम यहाँ शुरू होता है
blog_body = generate_blog()

if blog_body:
    # प्रोफेशनल ब्रांडेड डिज़ाइन (2026 Edition)
    img = '<img src="https://image.pollinations.ai/prompt/future_digital_money_2026_concept" style="width:100%; border-radius:15px; margin:20px 0; box-shadow: 0 5px 15px rgba(0,0,0,0.2);">'
    blog_body = blog_body.replace("[PHOTO_1]", img).replace("[PHOTO_2]", img)

    full_html = f"""<!DOCTYPE html>
<html lang="hi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Digital Kamai Hub | 2026 Passive Income</title>
    <style>
        body {{ font-family: 'Segoe UI', sans-serif; margin: 0; background: #f4f7f6; color: #333; }}
        header {{ background: linear-gradient(135deg, #0056b3, #00a2ff); color: white; padding: 60px 20px; text-align: center; border-bottom: 8px solid #ffdd57; }}
        nav {{ background: #004494; padding: 15px; text-align: center; position: sticky; top: 0; }}
        nav a {{ color: white; margin: 0 20px; text-decoration: none; font-weight: bold; }}
        .main-content {{ max-width: 800px; margin: 40px auto; background: white; padding: 40px; border-radius: 20px; box-shadow: 0 10px 30px rgba(0,0,0,0.1); }}
        footer {{ background: #1a1a1a; color: white; text-align: center; padding: 40px; margin-top: 60px; }}
    </style>
</head>
<body>
    <header><h1>🚀 Digital Kamai Hub</h1><p>2026 की डिजिटल क्रांति में आपका स्वागत है</p></header>
    <nav><a href="#">Home</a><a href="#">Earning Guide</a><a href="#">Contact</a></nav>
    <div class="main-content">{blog_body}</div>
    <footer><p>&copy; 2026 Digital Kamai Hub - Ramesh Chandra</p></footer>
</body>
</html>"""

    with open("index.html", "w", encoding="utf-8") as f:
        f.write(full_html)
    print("✅ MUBARAK HO! index.html update ho gayi hai!")
else:
    print("❌ Critical Failure: Blog generate nahi ho paya.")
    sys.exit(1)
    
