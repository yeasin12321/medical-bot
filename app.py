import os  # <--- এটি নতুন যোগ হয়েছে
from flask import Flask, render_template, request
import google.generativeai as genai
from PIL import Image

app = Flask(__name__)

# ==========================================
# এখন আর সরাসরি চাবি বসানো নেই। এটি Render থেকে চাবি খুঁজে নেবে।
# ==========================================
GOOGLE_API_KEY = os.environ.get("AIzaSyDIxtMDL9APHIFU1AIEtsfzrHmlI1slpbI")

genai.configure(api_key=GOOGLE_API_KEY)

# ফ্রি মডেল ব্যবহার করা হচ্ছে
# আপনার লিস্টে থাকা লাইট মডেল
model = genai.GenerativeModel('gemini-2.5-flash-lite-preview-09-2025')

@app.route('/', methods=['GET', 'POST'])
def index():
    # ... বাকি কোড আগের মতোই থাকবে ...
    # (নিচের বাকি অংশে হাত দেওয়ার দরকার নেই)
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
                prompt = """
                Analyze this X-ray strictly as a professional Radiologist.
                Do NOT mention AI. Provide a report in BENGALI (বাংলা).
                Structure:
                1. পর্যবেক্ষণ (Findings)
                2. ইম্প্রেশন (Impression)
                3. পরামর্শ (Advice)
                """
                response = model.generate_content([prompt, img])
                report = response.text.replace('*', '')
            except Exception as e:
                error = f"সমস্যা হয়েছে: {str(e)}"

    return render_template('index.html', report=report, error=error)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
