from flask import Flask, render_template, request
import google.generativeai as genai
from PIL import Image

app = Flask(__name__)

# ==========================================
# আপনার সর্বশেষ সঠিক API Key বসানো হয়েছে
# ==========================================
GOOGLE_API_KEY = "AIzaSyAKnOK2qeqDSyPy41sC5ZXQ1-KxLU_8BNY"

genai.configure(api_key=GOOGLE_API_KEY)

# মডেলের নাম 'gemini-pro' ব্যবহার করা হয়েছে যাতে 404 এরর না আসে
model = genai.GenerativeModel('gemini-3-flash-preview')

@app.route('/', methods=['GET', 'POST'])
def index():
    report = None
    error = None

    if request.method == 'POST':
        # ছবি আছে কি না চেক করা হচ্ছে
        if 'xray_image' not in request.files:
            error = "ফাইল পাওয়া যায়নি।"
            return render_template('index.html', error=error)
        
        file = request.files['xray_image']
        
        if file.filename == '':
            error = "অনুগ্রহ করে একটি ছবি সিলেক্ট করুন।"
            return render_template('index.html', error=error)

        if file:
            try:
                # ছবি লোড করা হচ্ছে
                img = Image.open(file)
                
                # AI কে নির্দেশনা (Prompt)
                prompt = """
                Analyze this X-ray image strictly as a professional Radiologist.
                Do NOT mention you are an AI.
                Generate a medical report in BENGALI (বাংলা).
                Structure:
                1. পর্যবেক্ষণ (Findings)
                2. ইম্প্রেশন (Impression)
                3. পরামর্শ (Suggestion)
                
                If the image is not an X-ray, say: "ত্রুটি: এটি সঠিক এক্স-রে ইমেজ নয়।"
                """
                
                # রিপোর্ট তৈরি করা হচ্ছে
                response = model.generate_content([prompt, img])
                report = response.text.replace('*', '') # ক্লিন করা

            except Exception as e:
                error = f"সমস্যা হয়েছে: {str(e)}"

    return render_template('index.html', report=report, error=error)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')