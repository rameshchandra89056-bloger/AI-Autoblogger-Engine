import urllib.request
import json
import urllib.error
import os

# Digital Kamai Hub Engine v2.0
API_KEY = os.environ.get("GEMINI_API_KEY")

print("AI naya branded blog likh raha hai...\n")

url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-lite:generateContent?key={API_KEY}"

master_prompt = """
तुम एक प्रोफेशनल वेब डेवलपर हो। 'घर बैठे पैसे कमाने के 5 तरीके' पर एक शानदार हिंदी ब्लॉग लिखो।
नियम:
1. सिर्फ HTML Content देना (<h2>, <p>, <ul> टैग्स)।
2. [PHOTO_1], [PHOTO_2], [PHOTO_3] का इस्तेमाल सही जगह पर करो।
"""

data = {"contents": [{"parts": [{"text": master_prompt}]}]}
req = urllib.request.Request(url, data=json.dumps(data).encode('utf-8'), headers={'Content-Type': 'application/json'})

try:
    with urllib.request.urlopen(req) as response:
        result = json.loads(response.read().decode('utf-8'))
        ai_content = result['candidates'][0]['content']['parts'][0]['text']
        ai_content = ai_content.replace("```html", "").replace("```", "").strip()
        
        # Images Replacement
        img1 = '<img src="https://image.pollinations.ai/prompt/man_working_on_laptop_at_home_money" style="width:100%; border-radius:10px; margin:20px 0;">'
        ai_content = ai_content.replace("[PHOTO_1]", img1).replace("[PHOTO_2]", img1).replace("[PHOTO_3]", img1)
        
        # SEO Template
        website_template = f"""<!DOCTYPE html>
<html lang="hi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Digital Kamai Hub | Ghar Baithe Paisa</title>
    <style>
        body {{ font-family: sans-serif; margin: 0; background: #f4f4f4; }}
        header {{ background: #0056b3; color: white; padding: 30px; text-align: center; }}
        nav {{ background: #004494; padding: 10px; text-align: center; }}
        nav a {{ color: white; margin: 0 15px; text-decoration: none; font-weight: bold; }}
        .content {{ max-width: 800px; margin: 20px auto; background: white; padding: 30px; border-radius: 10px; }}
        footer {{ background: #222; color: white; text-align: center; padding: 20px; margin-top: 40px; }}
    </style>
</head>
<body>
    <header><h1>🚀 Digital Kamai Hub</h1><p>Internet se kamai ka sach</p></header>
    <nav><a href="#">Home</a><a href="#">About</a><a href="#">Privacy</a></nav>
    <div class="content">{ai_content}</div>
    <footer><p>&copy; 2026 Digital Kamai Hub</p></footer>
</body>
</html>"""

        with open("index.html", "w", encoding="utf-8") as f:
            f.write(website_template)
        print("✅ Success! index.html updated with Header/Footer.")

except Exception as e:
    print("❌ Error:", e)
   
