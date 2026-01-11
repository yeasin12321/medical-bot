import os
from flask import Flask, render_template, request
import google.generativeai as genai
from PIL import Image

# 👇 ভুল ছিল এখানে: Flask(_name_) -> সঠিক: Flask(__name__)
app = Flask(__name__)

GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")

if not GOOGLE_API_KEY:
    print("⚠️ Error: GOOGLE_API_KEY not found!")

genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

@app.route('/', methods=['GET', 'POST'])
def index():
    report = None
    error = None

    if request.method == 'POST':
        try:
            if 'xray_image' not in request.files:
                return render_template('index.html', error="ফাইল পাওয়া যায়নি।")
            
            file = request.files['xray_image']
            if file.filename == '':
                return render_template('index.html', error="কোনো ছবি সিলেক্ট করা হয়নি।")

            if file:
                img = Image.open(file)
                prompt = """
                Act as a specialized Doctor. Analyze this X-ray/Medical Image.
                Output MUST be in BENGALI (বাংলা).
                Format:
                🔴 রোগ নির্ণয় (Diagnosis): [Main disease name]
                -----------------------------------
                📋 বিস্তারিত রিপোর্ট:
                ১. পর্যবেক্ষণ (Findings): [Details]
                ২. পরামর্শ (Advice): [Medicine/Test]
                """
                response = model.generate_content([prompt, img])
                report = response.text.replace('*', '')
                
        except Exception as e:
            print(f"❌ Error: {e}")
            error = "সার্ভারে সমস্যা হয়েছে। দয়া করে আবার চেষ্টা করুন।"

    return render_template('index.html', report=report, error=error)

# 👇 ভুল ছিল এখানেও: if _name_ == '_main_' -> সঠিক: if __name__ == '__main__'
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)