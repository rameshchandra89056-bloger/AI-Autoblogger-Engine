import urllib.request
import json
import os
import sys

# ==========================================
# DIGITAL KAMAI HUB - 2026 OMNI-SEARCHER v11.0
# ==========================================

raw_key = os.environ.get("GEMINI_API_KEY", "")
API_KEY = raw_key.strip()

if not API_KEY:
    print("❌ ERROR: API Key गायब है!")
    sys.exit(1)

print(f"🔍 Debug: चाबी परफेक्ट है (लंबाई: {len(API_KEY)})")

def get_ai_blog():
    # गुरु का नया मास्टरस्ट्रोक: 2026 के सबसे ताज़ा मॉडल्स की लिस्ट
    models_2026 = [
        "gemini-2.5-flash",    # सबसे नया
        "gemini-2.0-flash",    # 2026 का स्टेबल
        "gemini-1.5-pro-latest", # प्रो वर्शन
        "gemini-pro"           # एवरग्रीन मॉडल
    ]
    
    prompt = "तुम एक प्रो ब्लॉगर हो। 'ऑनलाइन इंटरनेट से पैसे कैसे कमाएं' पर एक शानदार हिंदी लेख लिखो। सिर्फ HTML tags (h2, p, ul) देना।"
    data = {"contents": [{"parts": [{"text": prompt}]}]}

    # हमारा रोबोट एक-एक करके नए दरवाज़े चेक करेगा
    for model in models_2026:
        print(f"🚀 कोशिश कर रहे हैं: {model}...")
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={API_KEY}"
        
        try:
            req = urllib.request.Request(url, data=json.dumps(data).encode('utf-8'), headers={'Content-Type': 'application/json'})
            with urllib.request.urlopen(req, timeout=30) as response:
                res = json.loads(response.read().decode('utf-8'))
                print(f"✅ SUCCESS! '{model}' ने जवाब दे दिया है!")
                return res['candidates'][0]['content']['parts'][0]['text']
        except urllib.error.HTTPError as e:
            # यह लाइन गूगल का असली मैसेज पढ़ लेगी
            error_details = e.read().decode('utf-8')
            print(f"⚠️ फेल ({model}): {e.code} -> {error_details}")
            continue # अगले मॉडल पर जाओ
        except Exception as e:
            print(f"⚠️ फेल ({model}): {e}")
            continue
            
    return None

def build_final_website(blog_text):
    blog_text = blog_text.replace("```html", "").replace("```", "").strip()
    
    return f"""<!DOCTYPE html>
<html lang="hi">
<head>
    <meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Digital Kamai Hub | 2026 Edition</title>
    <style>
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #eef2f5; margin: 0; color: #2c3e50; }}
        header {{ background: linear-gradient(135deg, #0f2027, #203a43, #2c5364); color: white; padding: 50px 20px; text-align: center; box-shadow: 0 4px 15px rgba(0,0,0,0.2); }}
        header h1 {{ margin: 0; font-size: 40px; letter-spacing: 1px; color: #f1c40f; }}
        header p {{ font-size: 18px; opacity: 0.9; margin-top: 10px; }}
        .container {{ max-width: 850px; margin: 40px auto; background: white; padding: 50px; border-radius: 16px; box-shadow: 0 10px 30px rgba(0,0,0,0.08); line-height: 1.8; font-size: 18px; }}
        h2 {{ color: #203a43; margin-top: 40px; border-left: 5px solid #f1c40f; padding-left: 15px; }}
        img {{ width: 100%; border-radius: 15px; margin: 25px 0; box-shadow: 0 8px 25px rgba(0,0,0,0.1); }}
        footer {{ text-align: center; padding: 30px; background: #1a1a1a; color: #ecf0f1; margin-top: 50px; font-size: 15px; }}
    </style>
</head>
<body>
    <header>
        <h1>🚀 Digital Kamai Hub</h1>
        <p>22वें प्रयास की सफलता - एक इंजीनियर की कहानी</p>
    </header>
    <div class="container">
        <img src="https://image.pollinations.ai/prompt/success_digital_business_2026" alt="Success">
        {blog_text}
    </div>
    <footer>&copy; 2026 Ramesh Chandra Enterprise | Never Give Up!</footer>
</body>
</html>"""

# Main Execution
print("🛠️ Starting Omni-Searcher v11.0...")
article = get_ai_blog()

if article:
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(build_final_website(article))
    print("🎉 MISSION ACCOMPLISHED! वेबसाइट 100% लाइव है!")
else:
    print("❌ Critical Failure: सारे मॉडल फेल हो गए।")
    sys.exit(1)
    
