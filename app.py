import os
from flask import Flask, render_template, request
import google.generativeai as genai
from PIL import Image

app = Flask(__name__)

# Render-এর গোপন ভল্ট থেকে চাবি নেওয়া হচ্ছে
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")

# চাবি ঠিকমতো আছে কি না চেক করা (Error prevention)
if not GOOGLE_API_KEY:
    print("Error: GOOGLE_API_KEY not found in environment variables!")

genai.configure(api_key=GOOGLE_API_KEY)

# ফাস্ট এবং ফ্রি মডেল
model = genai.GenerativeModel('gemini-2.5-flash-lite-preview-09-2025')

@app.route('/', methods=['GET', 'POST'])
def index():
    report = None
    error = None

    if request.method == 'POST':
        # ফাইল আছে কি না চেক করা
        if 'xray_image' not in request.files:
            return render_template('index.html', error="ফাইল পাওয়া যায়নি।")
        
        file = request.files['xray_image']
        
        if file.filename == '':
            return render_template('index.html', error="কোনো ছবি সিলেক্ট করা হয়নি।")

        if file:
            try:
                img = Image.open(file)
                
                # AI-কে নির্দেশ দেওয়া (Prompt)
                prompt = """
                Act as a professional medical imaging expert. Analyze this image.
                Output MUST be in BENGALI (বাংলা).
                
                Strict Output Format:
                
                🔴 মূল সমস্যা (Diagnosis): [Identify the main disease/issue in 2-4 words]

                ------------------------------------------------

                📋 বিস্তারিত রিপোর্ট:
                ১. পর্যবেক্ষণ (Findings): [Detailed findings]
                ২. পরামর্শ (Advice): [General suggestions]
                
                If the image is not an X-ray/MRI, say "এটি কোনো মেডিকেল রিপোর্ট নয়।"
                """
                
                response = model.generate_content([prompt, img])
                report = response.text.replace('*', '') # ফরম্যাটিং ঠিক করা
            
            except Exception as e:
                # এরর লগ প্রিন্ট করা (Render Logs-এ দেখার জন্য)
                print(f"Error occurred: {e}")
                error_msg = str(e)
                
                if "429" in error_msg:
                    error = "সার্ভার ব্যস্ত। ২ মিনিট পর চেষ্টা করুন।"
                elif "403" in error_msg:
                    error = "API Key সমস্যা। চাবি পরিবর্তন করুন।"
                else:
                    error = "রিপোর্ট তৈরি করা যায়নি। আবার চেষ্টা করুন।"

    return render_template('index.html', report=report, error=error)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
