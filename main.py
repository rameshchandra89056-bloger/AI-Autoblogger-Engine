import urllib.request
import json
import urllib.error
import os
import sys

# Digital Kamai Hub Engine v2.1 (Stable)
API_KEY = os.environ.get("GEMINI_API_KEY")

if not API_KEY:
    print("❌ ERROR: API_KEY nahi mili! Secrets check karein.")
    sys.exit(1)

# Sabse stable model ka istemal
url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={API_KEY}"

print("AI blog likh raha hai... kripya 30 second intezaar karein...\n")

master_prompt = """
तुम एक प्रोफेशनल वेब डेवलपर हो। 'घर बैठे पैसे कमाने के 5 तरीके' पर एक शानदार हिंदी ब्लॉग लिखो।
नियम: सिर्फ HTML कंटेंट देना (<h2>, <p>, <ul>)। [PHOTO_1], [PHOTO_2], [PHOTO_3] का सही जगह इस्तेमाल करना।
"""

data = {"contents": [{"parts": [{"text": master_prompt}]}]}

try:
    req = urllib.request.Request(url, data=json.dumps(data).encode('utf-8'), headers={'Content-Type': 'application/json'})
    with urllib.request.urlopen(req) as response:
        result = json.loads(response.read().decode('utf-8'))
        ai_content = result['candidates'][0]['content']['parts'][0]['text']
        ai_content = ai_content.replace("```html", "").replace("```", "").strip()
        
        # Images Replacement
        img1 = '<img src="https://image.pollinations.ai/prompt/online_money_making_at_home_professional" style="width:100%; border-radius:10px; margin:20px 0;">'
        ai_content = ai_content.replace("[PHOTO_1]", img1).replace("[PHOTO_2]", img1).replace("[PHOTO_3]", img1)
        
        # SEO Template
        website_template = f"""<!DOCTYPE html>
<html lang="hi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Digital Kamai Hub | Ghar Baithe Kamai</title>
    <style>
        body {{ font-family: sans-serif; margin: 0; background: #f0f2f5; }}
        header {{ background: #0056b3; color: white; padding: 40px 20px; text-align: center; border-bottom: 5px solid #ffdd57; }}
        nav {{ background: #004494; padding: 15px; text-align: center; }}
        nav a {{ color: white; margin: 0 15px; text-decoration: none; font-weight: bold; }}
        .content {{ max-width: 800px; margin: 30px auto; background: white; padding: 40px; border-radius: 15px; box-shadow: 0 10px 30px rgba(0,0,0,0.1); }}
        footer {{ background: #1a1a1a; color: white; text-align: center; padding: 30px; margin-top: 50px; }}
    </style>
</head>
<body>
    <header><h1>🚀 Digital Kamai Hub</h1><p>डिजिटल दुनिया से पैसे कमाने का असली ज्ञान</p></header>
    <nav><a href="#">Home</a><a href="#">Privacy Policy</a><a href="#">Contact</a></nav>
    <div class="content">{ai_content}</div>
    <footer><p>&copy; 2026 Digital Kamai Hub - Aapki Kamai, Hamari Khushi</p></footer>
</body>
</html>"""

        with open("index.html", "w", encoding="utf-8") as f:
            f.write(website_template)
        print("✅ SUCCESS: index.html updated successfully!")

except Exception as e:
    print(f"❌ CRITICAL ERROR: {str(e)}")
    sys.exit(1) # Action ko fail dikhayega taki hum debug kar sakein
