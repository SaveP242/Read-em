import os
import fitz
from summarizer import Summarizer
from flask import Flask, request, render_template, send_file
import pyttsx3

app = Flask(__name__)

#BERT-based extractive summarizer
bert_model = Summarizer()

def extract_text_from_pdf(pdf_path):
    text = ""
    doc = fitz.open(pdf_path)
    for page_num in range(doc.page_count):
        page = doc.load_page(page_num)
        text += page.get_text()
    doc.close()
    return text

def summarize_text(text, max_length=150):
    summary = bert_model(text, ratio=0.2)
    return summary


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        if "file" not in request.files:
            return render_template("index.html", message="No file part")

        file = request.files["file"]
        translate = request.form.get("translate")
        summarize = request.form.get("summarize")
        read_out = request.form.get("read_out")

        if file and file.filename.endswith(".pdf"):
            pdf_path = "temp.pdf"
            file.save(pdf_path)

            #Extracting text from the PDF
            pdf_text = extract_text_from_pdf(pdf_path)

            #Performing translation if requested
            if translate == "yes":
                from googletrans import Translator
                translator = Translator()
                pdf_text = translator.translate(pdf_text, dest="en").text

            #Performing summarization if requested
            if summarize == "yes":
                pdf_text = summarize_text(pdf_text)

                #Reading out the result if requested
                if read_out == "yes":
                    tts = pyttsx3.init()

                    #Processing the text
                    if summarize == "yes":
                        pdf_text = summarize_text(pdf_text)

                    tts.say(pdf_text)

                    tts.runAndWait()

            # Deleting the temporary file
            os.remove(pdf_path)

            return render_template("result.html", content=pdf_text, enable_read_out=True)

    return render_template("index.html")

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)