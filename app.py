import os
from flask import Flask, render_template, request
import google.generativeai as genai
from PIL import Image

app = Flask(_name_)

# API Key সেটআপ
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")

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
                prompt = "Analyze this medical image and provide a report in Bengali. Start with 'Diagnosis:' in bold."
                
                response = model.generate_content([prompt, img])
                report = response.text.replace('*', '')
                
        except Exception as e:
            print(f"Error: {e}")
            error = "Server Error. Please try again."

    return render_template('index.html', report=report, error=error)

if _name_ == '_main_':
    # Render-এর জন্য এই পোর্ট সেটিং বাধ্যতামূলক
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
