import urllib.request
import json
import os
import sys

# ==========================================
# DIGITAL KAMAI HUB - OMNI ENGINE v9.0 (MASTERKEY)
# ==========================================

API_KEY = os.environ.get("GEMINI_API_KEY")

if not API_KEY:
    print("❌ ERROR: API Key is missing!")
    sys.exit(1)

def call_gemini_smart():
    # गुरु की मास्टर-लिस्ट: 4 अलग-अलग दरवाज़े (Models)
    models_to_try = [
        "gemini-1.5-flash-latest", # सबसे नया
        "gemini-pro",              # सबसे पुराना और पक्का
        "gemini-1.0-pro",          # बैकअप 1
        "gemini-1.5-flash"         # बैकअप 2
    ]
    
    prompt = "तुम एक वर्ल्ड क्लास ब्लॉगर हो। 'ऑनलाइन पैसे कैसे कमाएं' पर एक शानदार हिंदी लेख लिखो। सिर्फ HTML tags (h2, p, ul) देना। [IMAGE] टैग 2 बार लगाओ।"
    data = {"contents": [{"parts": [{"text": prompt}]}]}

    # कोड एक-एक करके सारे दरवाज़े खटखटाएगा
    for model_name in models_to_try:
        print(f"🔄 दरवाज़ा खटखटा रहे हैं: {model_name}...")
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={API_KEY}"
        
        try:
            req = urllib.request.Request(url, data=json.dumps(data).encode('utf-8'), headers={'Content-Type': 'application/json'})
            with urllib.request.urlopen(req, timeout=30) as response:
                res_body = json.loads(response.read().decode('utf-8'))
                text = res_body['candidates'][0]['content']['parts'][0]['text']
                print(f"✅ SUCCESS! '{model_name}' ने दरवाज़ा खोल दिया!")
                return text
        except urllib.error.HTTPError as e:
            print(f"⚠️ फेल (Error {e.code}) - कोई बात नहीं, अगला मॉडल ट्राई कर रहे हैं...")
            continue # यह लाइन कोड को रुकने नहीं देगी, अगले मॉडल पर ले जाएगी
        except Exception as e:
            print(f"⚠️ फेल ({str(e)}) - अगला ट्राई कर रहे हैं...")
            continue
            
    return None # अगर चारों दरवाज़े बंद मिले (जो कि असंभव है)

def build_html(blog_text):
    blog_text = blog_text.replace("```html", "").replace("```", "").strip()
    img_tag = '<img src="https://image.pollinations.ai/prompt/wealth_digital_lifestyle_2026_professional" style="width:100%; border-radius:15px; margin:25px 0; box-shadow: 0 8px 25px rgba(0,0,0,0.1);">'
    final_content = blog_text.replace("[IMAGE]", img_tag)

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
        footer {{ text-align: center; padding: 30px; background: #1a1a1a; color: #ecf0f1; margin-top: 50px; font-size: 15px; }}
    </style>
</head>
<body>
    <header>
        <h1>🚀 Digital Kamai Hub</h1>
        <p>एक सफल सॉफ्टवेयर इंजीनियर का ड्रीम प्रोजेक्ट</p>
    </header>
    <div class="container">{final_content}</div>
    <footer>&copy; 2026 Ramesh Chandra Enterprise | All Rights Reserved</footer>
</body>
</html>"""

print("🛠️ Starting Masterkey Engine v9.0...")
article = call_gemini_smart()

if article:
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(build_html(article))
    print("🎉 MISSION ACCOMPLISHED! वेबसाइट तैयार है!")
else:
    print("❌ Critical Failure: चारों मॉडल्स ने जवाब नहीं दिया।")
    sys.exit(1)
    
