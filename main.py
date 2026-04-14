import urllib.request
import json
import urllib.error
import os
from datetime import datetime

# मशीन सीधे तिजोरी (Secrets) से चाबी निकालेगी
API_KEY = os.environ.get("GEMINI_API_KEY")

print("AI khud photo laga raha hai aur design kar raha hai... kripya intezaar karein...\n")

url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-lite:generateContent?key={API_KEY}"

# गुरु का 100% Foolproof प्रॉम्प्ट
master_prompt = """
तुम एक प्रोफेशनल वेब डेवलपर और SEO ब्लॉगर हो। 'यूट्यूब से पैसे कैसे कमाएं' पर एक शानदार हिंदी ब्लॉग लिखो।
सख्त नियम (STRICT RULES):
1. सिर्फ और सिर्फ HTML कोड देना। शुरुआत या अंत में ```html या ``` मत लिखना।
2. एक शानदार <style> टैग लगाओ ताकि वेबसाइट मोबाइल पर बहुत सुंदर (Responsive) दिखे। बैकग्राउंड हल्का ग्रे, टेक्स्ट डार्क, हेडिंग्स नीले रंग की हों।
3. **ऑटोमैटिक इमेजेस (100% STRICT):** तुम्हें ब्लॉग में 3 जगह फोटो लगानी हैं। मैंने नीचे 3 फिक्स (Fixed) इमेज कोड दिए हैं, तुम्हें बस इन्हें हूबहू (Exact) कॉपी करके सही हेडिंग के नीचे पेस्ट करना है। अपनी तरफ से कोई लिंक मत बनाना!

Image 1 कोड (शुरुआत में, यूट्यूब पार्टनर प्रोग्राम के पास लगाएं):
<img src="https://image.pollinations.ai/prompt/happy_youtube_creator_earning_money_laptop" style="width:100%; border-radius:10px; margin:20px 0;">

Image 2 कोड (बीच में, एफिलिएट मार्केटिंग के पास लगाएं):
<img src="https://image.pollinations.ai/prompt/affiliate_marketing_concept_graphs_laptop" style="width:100%; border-radius:10px; margin:20px 0;">

Image 3 कोड (अंत में, डिजिटल प्रोडक्ट या मर्चेंडाइज के पास लगाएं):
<img src="https://image.pollinations.ai/prompt/selling_digital_products_online_store" style="width:100%; border-radius:10px; margin:20px 0;">
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
        
        # फाइल हमेशा index.html बनेगी
        file_name = "index.html"
        
        with open(file_name, "w", encoding="utf-8") as f:
            f.write(clean_html)
        
        print(f"✅ Safalta! Aapka automatic blog '{file_name}' mein save ho gaya hai.")

except Exception as e:
    print("❌ Kuch gadbad hui:", e)
    
