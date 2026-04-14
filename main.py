import urllib.request
import json
import urllib.error
import os

# मशीन सीधे तिजोरी से चाबी निकालेगी
API_KEY = os.environ.get("GEMINI_API_KEY")

print("AI naya blog likh raha hai aur SEO template set kar raha hai...\n")

url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-lite:generateContent?key={API_KEY}"

# AI को सिर्फ कंटेंट लिखने का आदेश (डिज़ाइन का नहीं)
master_prompt = """
तुम एक प्रोफेशनल वेब डेवलपर और SEO ब्लॉगर हो। 'ऑनलाइन पैसे कैसे कमाएं - 3 सबसे आसान तरीके' पर एक शानदार हिंदी ब्लॉग लिखो।
सख्त नियम (STRICT RULES):
1. सिर्फ और सिर्फ HTML कोड देना (जैसे <h2>, <p>, <ul>)। शुरुआत या अंत में ```html मत लिखना।
2. कोई <style>, <html>, <head>, या <body> टैग मत लगाना। वो मैं खुद लगाऊंगा।
3. **फोटो के लिए सख्त निर्देश:** अपनी तरफ से कोई भी <img> टैग या लिंक मत बनाना! तुम्हें बस सही जगह पर ये तीन कोड वर्ड लिखने हैं:
   - पहले तरीके के बाद लिखो: [PHOTO_1]
   - दूसरे तरीके के बाद लिखो: [PHOTO_2]
   - तीसरे तरीके के बाद लिखो: [PHOTO_3]
"""

data = {"contents": [{"parts": [{"text": master_prompt}]}]}
req = urllib.request.Request(url, data=json.dumps(data).encode('utf-8'), headers={'Content-Type': 'application/json'})

try:
    with urllib.request.urlopen(req) as response:
        result = json.loads(response.read().decode('utf-8'))
        ai_content = result['candidates'][0]['content']['parts'][0]['text']
        ai_content = ai_content.replace("```html", "").replace("```", "").strip()
        
        # Python खुद फोटो लगाएगा
        img1 = '<img src="[https://image.pollinations.ai/prompt/freelancer_earning_money_online_laptop](https://image.pollinations.ai/prompt/freelancer_earning_money_online_laptop)" style="width:100%; border-radius:10px; margin:20px 0;">'
        img2 = '<img src="[https://image.pollinations.ai/prompt/youtube_creator_recording_video_setup](https://image.pollinations.ai/prompt/youtube_creator_recording_video_setup)" style="width:100%; border-radius:10px; margin:20px 0;">'
        img3 = '<img src="[https://image.pollinations.ai/prompt/affiliate_marketing_money_growth_chart](https://image.pollinations.ai/prompt/affiliate_marketing_money_growth_chart)" style="width:100%; border-radius:10px; margin:20px 0;">'
        
        ai_content = ai_content.replace("[PHOTO_1]", img1)
        ai_content = ai_content.replace("[PHOTO_2]", img2)
        ai_content = ai_content.replace("[PHOTO_3]", img3)
        
        # ----- GURUJI KA SEO TEMPLATE (Header/Footer/Menu) -----
        # यहाँ वेबसाइट का असली ढांचा है
        website_template = f"""<!DOCTYPE html>
<html lang="hi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="Digital Kamai Hub - इंटरनेट से पैसे कमाने के असली तरीके, ब्लॉगिंग और यूट्यूब की जानकारी।">
    <title>Digital Kamai Hub | ऑनलाइन पैसे कैसे कमाएं</title>
    <style>
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; padding: 0; background-color: #f4f7f6; color: #333; line-height: 1.6; }}
        header {{ background-color: #0056b3; color: white; padding: 25px 20px; text-align: center; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }}
        header h1 {{ margin: 0; font-size: 32px; letter-spacing: 1px; font-weight: 800; }}
        header p {{ margin: 5px 0 0 0; font-size: 15px; opacity: 0.9; }}
        nav {{ background-color: #004494; padding: 12px; text-align: center; display: flex; justify-content: center; flex-wrap: wrap; gap: 15px; }}
        nav a {{ color: white; text-decoration: none; font-weight: 600; font-size: 15px; transition: 0.3s; }}
        nav a:hover {{ color: #ffdd57; }}
        .container {{ max-width: 800px; margin: 30px auto; background: white; padding: 40px; border-radius: 12px; box-shadow: 0 5px 15px rgba(0,0,0,0.05); }}
        h1, h2, h3 {{ color: #0056b3; margin-top: 30px; }}
        footer {{ background-color: #1a1a1a; color: white; text-align: center; padding: 20px; margin-top: 50px; font-size: 14px; }}
        footer a {{ color: #4da6ff; text-decoration: none; margin: 0 10px; }}
        footer a:hover {{ text-decoration: underline; }}
    </style>
</head>
<body>

    <header>
        <h1>🚀 Digital Kamai Hub</h1>
        <p>इंटरनेट से पैसे कमाने का सबसे भरोसेमंद रास्ता</p>
    </header>

    <nav>
        <a href="#">Home</a>
        <a href="#">About Us</a>
        <a href="#">Privacy Policy</a>
        <a href="#">Disclaimer</a>
    </nav>

    <div class="container">
        {ai_content}
    </div>

    <footer>
        <p>&copy; 2026 Digital Kamai Hub. All rights reserved.</p>
        <p>
            <a href="#">Privacy Policy</a> | 
            <a href="#">Disclaimer</a> | 
            <a href="#">Contact Us</a>
        </p>
    </footer>

</body>
</html>"""

        file_name = "index.html"
        with open(file_name, "w", encoding="utf-8") as f:
            f.write(website_template)
            
        print(f"✅ Safalta! SEO aur Header/Footer ke saath blog '{file_name}' mein save ho gaya.")

except Exception as e:
    print("❌ Kuch gadbad hui:", e)
   
