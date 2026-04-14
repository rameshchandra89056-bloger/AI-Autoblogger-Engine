import urllib.request
import json
import urllib.error
import os
from datetime import datetime

# मशीन सीधे तिजोरी (Secrets) से चाबी निकालेगी
API_KEY = os.environ.get("GEMINI_API_KEY")

print("AI blog likh raha hai... kripya intezaar karein...\n")

url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-lite:generateContent?key={API_KEY}"

# गुरु का नया प्रॉम्प्ट: AI से फोटो की पावर छीन ली गई है
master_prompt = """
तुम एक प्रोफेशनल वेब डेवलपर और SEO ब्लॉगर हो। 'यूट्यूब से पैसे कैसे कमाएं' पर एक शानदार हिंदी ब्लॉग लिखो।
सख्त नियम (STRICT RULES):
1. सिर्फ और सिर्फ HTML कोड देना। शुरुआत या अंत में ```html मत लिखना।
2. एक शानदार <style> टैग लगाओ ताकि वेबसाइट मोबाइल पर बहुत सुंदर (Responsive) दिखे। बैकग्राउंड हल्का ग्रे, टेक्स्ट डार्क, हेडिंग्स नीले रंग की हों।
3. **फोटो के लिए सख्त निर्देश (NO IMAGES):** अपनी तरफ से कोई भी <img> टैग या लिंक मत बनाना! तुम्हें बस सही जगह पर ये तीन कोड वर्ड (Tags) लिखने हैं:
   - जहाँ पहली फोटो आनी चाहिए वहाँ हूबहू लिखो: [PHOTO_1]
   - जहाँ दूसरी फोटो आनी चाहिए वहाँ हूबहू लिखो: [PHOTO_2]
   - जहाँ तीसरी फोटो आनी चाहिए वहाँ हूबहू लिखो: [PHOTO_3]
बस ये कोड वर्ड लिख दो, तुम्हें कोई लिंक नहीं बनाना है।
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
        
        # Python खुद AI की जगह असली फोटो लगाएगा (100% Foolproof)
        img1 = '<img src="[https://image.pollinations.ai/prompt/youtube_creator_earning_money_laptop_setup](https://image.pollinations.ai/prompt/youtube_creator_earning_money_laptop_setup)" style="width:100%; border-radius:10px; margin:20px 0;">'
        img2 = '<img src="[https://image.pollinations.ai/prompt/affiliate_marketing_graphs_on_laptop_screen](https://image.pollinations.ai/prompt/affiliate_marketing_graphs_on_laptop_screen)" style="width:100%; border-radius:10px; margin:20px 0;">'
        img3 = '<img src="[https://image.pollinations.ai/prompt/selling_digital_products_on_online_store](https://image.pollinations.ai/prompt/selling_digital_products_on_online_store)" style="width:100%; border-radius:10px; margin:20px 0;">'
        
        # कोड वर्ड्स को असली फोटो से बदल रहे हैं
        clean_html = clean_html.replace("[PHOTO_1]", img1)
        clean_html = clean_html.replace("[PHOTO_2]", img2)
        clean_html = clean_html.replace("[PHOTO_3]", img3)
        
        # फाइल हमेशा index.html बनेगी
        file_name = "index.html"
        
        with open(file_name, "w", encoding="utf-8") as f:
            f.write(clean_html)
        
        print(f"✅ Safalta! Aapka automatic blog '{file_name}' mein save ho gaya hai.")

except Exception as e:
    print("❌ Kuch gadbad hui:", e)
    
