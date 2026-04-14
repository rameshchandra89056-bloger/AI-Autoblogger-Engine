import urllib.request
import json
import urllib.error
import os
from datetime import datetime

# मशीन सीधे तिजोरी (Secrets) से चाबी निकालेगी
API_KEY = os.environ.get("GEMINI_API_KEY")

print("एआई खुद फोटो लगा रहा है और डिज़ाइन कर रहा है... कृपया इंतज़ार करें...\n")

url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-lite:generateContent?key={API_KEY}"

master_prompt = """
तुम एक प्रोफेशनल वेब डेवलपर और SEO ब्लॉगर हो। 'ब्लॉगिंग से पैसे कैसे कमाएं' पर एक शानदार हिंदी ब्लॉग लिखो।
सख्त नियम (STRICT RULES):
1. सिर्फ और सिर्फ HTML कोड देना। शुरुआत या अंत में ```html या ``` मत लिखना।
2. एक शानदार <style> टैग लगाओ ताकि वेबसाइट मोबाइल पर बहुत सुंदर (Responsive) दिखे। बैकग्राउंड हल्का ग्रे, टेक्स्ट डार्क, हेडिंग्स नीले रंग की हों।
3. **ऑटोमैटिक इमेजेस:** ब्लॉग में 3 जगह फोटो लगाओ। फोटो लगाने के लिए इस <img> टैग का इस्तेमाल करो:
<img src="https://image.pollinations.ai/prompt/YOUR_ENGLISH_PROMPT_HERE" style="width:100%; border-radius:10px; margin:20px 0;">
ध्यान रहे: 'YOUR_ENGLISH_PROMPT_HERE' की जगह तुम्हें उस फोटो का अंग्रेजी में एक छोटा डिस्क्रिप्शन लिखना है (जैसे: modern_laptop_with_money). कोई भी पीला बक्सा मत बनाना!
"""

data = {
    "contents": [{"parts": [{"text": master_prompt}]}]
}

req = urllib.request.Request(url, data=json.dumps(data).encode('utf-8'), headers={'Content-Type': 'application/json'})

try:
    with urllib.request.urlopen(req) as response:
        result = json.loads(response.read().decode('utf-8'))
        ai_response = result['candidates'][0]['content']['parts'][0]['text']
        
        clean_html = ai_response.replace("```html", "").replace("```", "").strip()
        
        current_time = datetime.now().strftime("%I_%M_%p")
        file_name = f"Auto_Blog_{current_time}.html"
        
        with open(file_name, "w", encoding="utf-8") as f:
            f.write(clean_html)
        
        print(f"✅ सफलता! आपका ऑटोमैटिक फोटो वाला ब्लॉग '{file_name}' में सेव हो गया है।")

except Exception as e:
    print("❌ कुछ गड़बड़ हुई:", e)
    
