import gradio as gr
import pdfplumber
import re
from transformers import pipeline
import requests  # for web fetch
import os

# ================= MODELS =================
qa_model = pipeline("question-answering", model="distilbert-base-uncased-distilled-squad")
rewriter = pipeline("text2text-generation", model="facebook/bart-large-cnn")

# ================= PDF =================
PDF_PATH = "Sudan_crises_updated.pdf"

def load_pdf(path):
    text = ""
    try:
        with pdfplumber.open(path) as pdf:
            for p in pdf.pages:
                t = p.extract_text()
                if t:
                    text += re.sub(r"\n+", "\n", t) + "\n"
        return text.lower()
    except:
        return ""

pdf_text = load_pdf(PDF_PATH)

# ================= LANGUAGE DETECTION =================
def detect_lang(q):
    if any('\u0600' <= c <= '\u06FF' for c in q):
        return "urdu"
    roman = ["kya","kab","ka","ki","ke","hai","kyun"]
    if any(w in q.lower() for w in roman):
        return "roman"
    return "english"

# ================= QUESTION REWRITE =================
def rewrite(q):
    return rewriter(f"Rewrite this Sudan related question clearly:\n{q}",
                    max_length=50, do_sample=False)[0]["generated_text"]

# ================= ANSWER ENGINE =================
def answer(q, context_text):
    clean_q = rewrite(q)
    result = qa_model(question=clean_q, context=context_text)
    if result["score"] < 0.25:
        return None
    main_answer = result["answer"]
    sentences = context_text.split(".")
    related = [s.strip() for s in sentences if main_answer.lower() in s][:3]
    return main_answer, related

# ================= WEB SEARCH (optional) =================
# Replace "YOUR_SERPAPI_KEY" with your SerpAPI key if you want web fetch
SERPAPI_KEY = os.environ.get("SERPAPI_KEY")  # store in Hugging Face Secrets

def web_fetch(query):
    if not SERPAPI_KEY:
        return "Answer not found in PDF and Web fetch not configured."
    try:
        url = f"https://serpapi.com/search.json?q={query}&api_key={SERPAPI_KEY}"
        r = requests.get(url, timeout=5).json()
        snippets = []
        if "organic_results" in r:
            for item in r["organic_results"][:3]:
                snippets.append(item.get("snippet",""))
        return "\n".join(snippets) if snippets else "No relevant info found online."
    except:
        return "Error fetching from web."

# ================= AUTO SUGGESTIONS =================
def auto_questions(context_text):
    qs = []
    for line in context_text.split("\n"):
        if len(line) > 80 and "?" not in line:
            qs.append("Why " + line[:60] + "?")
    return list(dict.fromkeys(qs))[:6]

suggestions = auto_questions(pdf_text)

# ================= CHAT FUNCTION =================
chat_history = []

def chatbot_fn(user_q, pdf_file=None):
    global chat_history
    chat_history = []  # clear previous chat for new question
    
    context_text = load_pdf(pdf_file.name) if pdf_file else pdf_text

    lang = detect_lang(user_q)
    res = answer(user_q, context_text)
    
    if not res:
        # Try web fetch if PDF fails
        reply = web_fetch(user_q)
    else:
        main, related = res
        reply = f"**Answer:** {main}"
        if related:
            reply += "\n\n**Related facts:**"
            for r in related:
                reply += f"\n• {r.strip()}."

    chat_history.append(("User", user_q))
    chat_history.append(("Bot", reply))

    formatted = ""
    for role, text in chat_history:
        color = "#ff4c4c" if role=="User" else "#ffd6d6"
        align = "right" if role=="User" else "left"
        formatted += f"<div style='background:{'#1a0000' if role=='User' else '#330000'}; color:{color}; padding:10px; border-radius:10px; margin:5px 0; text-align:{align};'>{text}</div>"
    
    return formatted

# ================= GRADIO UI =================
chat_history = []

with gr.Blocks(css="""
body { background-color: #0b0c10; color: #f5f5f5; font-family: 'Orbitron', 'Noto Nastaliq Urdu', sans-serif; }
.gr-button { background-color: red; color: black; border-radius:8px; }
.gr-textbox { background-color:#222; color:red; border:1px solid red; }
.gr-file { background-color:#222; color:red; border:1px solid red; }
""") as demo:
    gr.Markdown("<h2 style='color:red; text-align:center;'>🌍 Sudan Crisis AI - Mafia Style</h2>")
    
    with gr.Row():
        with gr.Column():
            user_input = gr.Textbox(label="Ask about Sudan crisis:", placeholder="English, Urdu, or Roman Urdu")
            pdf_file = gr.File(label="Upload PDF (optional)", file_types=[".pdf"])
            submit = gr.Button("Send")
            
            gr.Markdown("### 🔎 Suggested Questions")
            suggestion_buttons = []
            for q in suggestions:
                btn = gr.Button(q)
                suggestion_buttons.append(btn)
                
        with gr.Column():
            output = gr.HTML(label="Chat Output")
    
    # Connect submit button
    submit.click(fn=chatbot_fn, inputs=[user_input, pdf_file], outputs=[output])
    
    # Connect suggested question buttons
    for btn, q in zip(suggestion_buttons, suggestions):
        btn.click(fn=chatbot_fn, inputs=[gr.State(q), pdf_file], outputs=[output])

demo.launch()
