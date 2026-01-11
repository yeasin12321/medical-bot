import os
from flask import Flask, render_template, request
import google.generativeai as genai
from PIL import Image

app = Flask(__name__)

# API Key সেটআপ
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")

# API Key না থাকলে এরর দেখাবে (সার্ভার ক্র্যাশ করবে না)
if not GOOGLE_API_KEY:
    print("⚠️ WARNING: GOOGLE_API_KEY not found! Check Render Environment settings.")

genai.configure(api_key=GOOGLE_API_KEY)

# সবথেকে স্টেবল মডেল ব্যবহার করা হচ্ছে (যাতে মডেল নিয়ে এরর না হয়)
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
                
                # প্রম্পট (নির্দেশনা)
                prompt = """
                Act as a specialized Doctor. Analyze this X-ray/Medical Image.
                Output MUST be in BENGALI (বাংলা).
                
                Format:
                🔴 রোগ নির্ণয় (Diagnosis): [Main disease name in 2-3 words]
                -----------------------------------
                📋 বিস্তারিত রিপোর্ট:
                ১. পর্যবেক্ষণ (Findings): [Details]
                ২. পরামর্শ (Advice): [Medicine/Test]
                
                If it's not a medical image, say 'এটি কোনো মেডিকেল রিপোর্ট নয়।'
                """
                
                response = model.generate_content([prompt, img])
                report = response.text.replace('*', '')
                
        except Exception as e:
            # আসল সমস্যাটি টার্মিনালে প্রিন্ট হবে
            print(f"❌ Error: {e}") 
            error = "সার্ভারে সমস্যা হয়েছে। দয়া করে অন্য ছবি দিন বা ২ মিনিট পর চেষ্টা করুন।"

    return render_template('index.html', report=report, error=error)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
