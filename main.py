import urllib.request
import json
import os
import sys

# ==========================================
# DIGITAL KAMAI HUB - AUTO-NAV ENGINE v12.0
# ==========================================

raw_key = os.environ.get("GEMINI_API_KEY", "")
API_KEY = raw_key.strip()

if not API_KEY:
    print("❌ ERROR: API Key गायब है!")
    sys.exit(1)

def get_ai_blog():
    models_2026 = ["gemini-2.5-flash", "gemini-2.0-flash", "gemini-1.5-pro-latest", "gemini-pro", "gemini-1.5-flash"]
    prompt = "तुम एक प्रो ब्लॉगर हो। 'ऑनलाइन इंटरनेट से पैसे कैसे कमाएं' पर एक शानदार हिंदी लेख लिखो। सिर्फ HTML tags (h2, p, ul) देना।"
    data = {"contents": [{"parts": [{"text": prompt}]}]}

    for model in models_2026:
        print(f"🚀 कोशिश कर रहे हैं: {model}...")
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={API_KEY}"
        try:
            req = urllib.request.Request(url, data=json.dumps(data).encode('utf-8'), headers={'Content-Type': 'application/json'})
            with urllib.request.urlopen(req, timeout=30) as response:
                res = json.loads(response.read().decode('utf-8'))
                return res['candidates'][0]['content']['parts'][0]['text']
        except Exception as e:
            continue
    return None

def build_final_website(blog_text):
    blog_text = blog_text.replace("```html", "").replace("```", "").strip()
    
    # गुरु का नया डिज़ाइन: जिसमें नेविगेशन मेनू जुड़ा हुआ है!
    return f"""<!DOCTYPE html>
<html lang="hi">
<head>
    <meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Digital Kamai Hub | Home</title>
    <style>
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #eef2f5; margin: 0; color: #2c3e50; }}
        header {{ background: linear-gradient(135deg, #0f2027, #203a43, #2c5364); color: white; padding: 40px 20px; text-align: center; box-shadow: 0 4px 15px rgba(0,0,0,0.2); }}
        header h1 {{ margin: 0; font-size: 40px; color: #f1c40f; }}
        
        /* नया नेविगेशन मेनू (The Magic Links) */
        nav {{ background: #1a1a1a; padding: 15px; text-align: center; position: sticky; top: 0; z-index: 100; box-shadow: 0 2px 10px rgba(0,0,0,0.5); }}
        nav a {{ color: white; text-decoration: none; margin: 0 15px; font-size: 16px; font-weight: bold; transition: 0.3s; padding: 5px 10px; border-radius: 5px; }}
        nav a:hover {{ background: #f1c40f; color: #1a1a1a; }}
        
        .container {{ max-width: 850px; margin: 40px auto; background: white; padding: 50px; border-radius: 16px; box-shadow: 0 10px 30px rgba(0,0,0,0.08); line-height: 1.8; font-size: 18px; }}
        h2 {{ color: #203a43; margin-top: 40px; border-left: 5px solid #f1c40f; padding-left: 15px; }}
        img {{ width: 100%; border-radius: 15px; margin: 25px 0; box-shadow: 0 5px 15px rgba(0,0,0,0.2); }}
        footer {{ text-align: center; padding: 30px; background: #1a1a1a; color: #ecf0f1; margin-top: 50px; }}
        footer a {{ color: #f1c40f; text-decoration: none; margin: 0 10px; }}
        footer a:hover {{ text-decoration: underline; }}
    </style>
</head>
<body>
    <header>
        <h1>🚀 Digital Kamai Hub</h1>
        <p>भारत का No.1 AI ऑटोमेशन ब्लॉग</p>
    </header>
    
    <nav>
        <a href="index.html">🏠 Home</a>
        <a href="about.html">👤 About Us</a>
        <a href="privacy.html">🔒 Privacy Policy</a>
        <a href="disclaimer.html">⚠️ Disclaimer</a>
    </nav>

    <div class="container">
        <img src="https://image.pollinations.ai/prompt/success_digital_business_2026_aesthetic" alt="Success">
        {blog_text}
    </div>
    
    <footer>
        <p>&copy; 2026 Ramesh Chandra Enterprise | Never Give Up!</p>
        <p>
            <a href="about.html">About</a> | 
            <a href="privacy.html">Privacy</a> | 
            <a href="disclaimer.html">Disclaimer</a>
        </p>
    </footer>
</body>
</html>"""

print("🛠️ Starting Engine v12.0...")
article = get_ai_blog()

if article:
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(build_final_website(article))
    print("🎉 SUCCESS! होमपेज पर मेनू (Menu) जोड़ दिया गया है!")
else:
    sys.exit(1)
    
