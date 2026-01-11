import os
from flask import Flask, render_template, request
import google.generativeai as genai
from PIL import Image

app = Flask(__name__)

# Render-এর গোপন ভল্ট থেকে চাবি নেওয়া হচ্ছে
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")

genai.configure(api_key=GOOGLE_API_KEY)

# ফাস্ট এবং ফ্রি মডেল
model = genai.GenerativeModel('gemini-2.5-flash-lite-preview-09-2025')

@app.route('/', methods=['GET', 'POST'])
def index():
    report = None
    error = None

    if request.method == 'POST':
        if 'xray_image' not in request.files:
            return render_template('index.html', error="ফাইল পাওয়া যায়নি।")
        
        file = request.files['xray_image']
        if file.filename == '':
            return render_template('index.html', error="কোনো ছবি সিলেক্ট করা হয়নি।")

        if file:
            try:
                img = Image.open(file)
                
                # ==================================================
                # 👇 এইখানে আমরা AI-কে নির্দেশ দিচ্ছি আলাদা করে রোগ দেখাতে
                # ==================================================
                prompt = """
                Act as a senior specialist Doctor/Radiologist. Analyze this X-ray image.
                Output MUST be in BENGALI (বাংলা).
                
                Please follow this exact format for the output:

                🔴 মূল সমস্যা (Diagnosis): [Write the main disease name here in 2-4 words clearly. Example: বাম পা ভেঙেছে / নিউমোনিয়া / যক্ষ্মা / নরমাল রিপোর্ট]

                ------------------------------------------------

                📋 বিস্তারিত রিপোর্ট:
                ১. পর্যবেক্ষণ (Findings): [Details here]
                ২. পরামর্শ (Advice): [Medicine or test suggestions]
                
                Do NOT mention 'AI' or 'Bot'. Keep it purely medical.
                """
                
                response = model.generate_content([prompt, img])
                report = response.text.replace('*', '') # স্টার চিহ্ন সরিয়ে পরিষ্কার করা
            
            except Exception as e:
                # এরর হ্যান্ডলিং
                error_msg = str(e)
                if "429" in error_msg:
                    error = "সার্ভার খুব ব্যস্ত। দয়া করে ১ মিনিট পর চেষ্টা করুন।"
                elif "403" in error_msg:
                    error = "API Key সমস্যা। ডেভেলপারকে জানান।"
                else:
                    error = "রিপোর্ট তৈরি করা যায়নি। আবার চেষ্টা করুন।"

    return render_template('index.html', report=report, error=error)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
