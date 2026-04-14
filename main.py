import urllib.request
import json
import os
import sys

# ==========================================
# DIGITAL KAMAI HUB - PRO ENGINE v8.1 (Final)
# ==========================================

API_KEY = os.environ.get("GEMINI_API_KEY")

def call_gemini_api():
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={API_KEY}"
    prompt_text = "तुम एक प्रो ब्लॉगर हो। 'ऑनलाइन पैसे कैसे कमाएं' पर एक प्रीमियम हिंदी लेख लिखो। सिर्फ HTML tags (h2, p, ul) देना। [IMAGE] टैग 2 बार लगाओ।"
    data = {"contents": [{"parts": [{"text": prompt_text}]}]}

    try:
        req = urllib.request.Request(url, data=json.dumps(data).encode('utf-8'), headers={'Content-Type': 'application/json'})
        with urllib.request.urlopen(req) as response:
            res_body = json.loads(response.read().decode('utf-8'))
            return res_body['candidates'][0]['content']['parts'][0]['text']
    except urllib.error.HTTPError as e:
        if e.code == 429:
            print("❌ ERROR 429: गूगल कह रहा है बहुत जल्दी-जल्दी कोशिश मत करो। 1 घंटा रुक जाओ।")
        elif e.code == 404:
            print("❌ ERROR 404: रास्ता नहीं मिला।")
        else:
            print(f"❌ API ERROR: {e.code} - {e.reason}")
        return None
    except Exception as e:
        print(f"❌ UNKNOWN ERROR: {str(e)}")
        return None

def build_html(blog_text):
    blog_text = blog_text.replace("```html", "").replace("```", "").strip()
    img_tag = '<img src="https://image.pollinations.ai/prompt/digital_money_making_2026_professional" style="width:100%; border-radius:20px; margin:20px 0; box-shadow: 0 4px 15px rgba(0,0,0,0.1);">'
    final_content = blog_text.replace("[IMAGE]", img_tag)

    return f"""<!DOCTYPE html>
<html lang="hi">
<head>
    <meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Digital Kamai Hub</title>
    <style>
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #f4f7f6; margin: 0; color: #333; }}
        header {{ background: linear-gradient(135deg, #0056b3, #00a2ff); color: white; padding: 40px 20px; text-align: center; }}
        header h1 {{ margin: 0; font-size: 36px; }}
        .container {{ max-width: 800px; margin: 30px auto; background: white; padding: 40px; border-radius: 12px; box-shadow: 0 5px 20px rgba(0,0,0,0.05); line-height: 1.6; }}
        h2 {{ color: #0056b3; margin-top: 30px; }}
        footer {{ text-align: center; padding: 30px; background: #222; color: #aaa; margin-top: 40px; }}
    </style>
</head>
<body>
    <header><h1>🚀 Digital Kamai Hub</h1><p>भविष्य की कमाई, आज से शुरू</p></header>
    <div class="container">{final_content}</div>
    <footer>&copy; 2026 Ramesh Chandra Enterprise | All Rights Reserved</footer>
</body>
</html>"""

print("🛠️ Starting Digital Kamai Engine v8.1...")
article = call_gemini_api()

if article:
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(build_html(article))
    print("✅ SUCCESS! आपकी ब्रांडेड वेबसाइट तैयार है।")
else:
    sys.exit(1)
    
