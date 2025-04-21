# === Full Flask App with Chatbot & Text Analysis (Enhanced UI with Toggle & Chat History) ===

from flask import Flask, render_template_string, jsonify, request
import fitz  # PyMuPDF
import base64
import os
import rag
import sys
import os
from pathlib import Path
from flask_cors import CORS
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import flask_implementation
from pdf_from_link import download_arxiv_pdf

app = Flask(__name__)
CORS(app)

# Global state
current_pdf_link = flask_implementation.link
downloaded_path = download_arxiv_pdf(current_pdf_link)
current_pdf_path = str(Path(downloaded_path).resolve())

# ==== Utility Functions ====

def process_text(selection):
    return {
        "analysis": rag.get_contextual_definition(selection)
    }

def pdf_to_images(pdf_path):
    try:
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF file not found at {pdf_path}")

        doc = fitz.open(pdf_path)
        pages = []
        for page in doc:
            pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
            img_data = {
                "image": base64.b64encode(pix.tobytes("png")).decode("utf-8"),
                "width": pix.width,
                "height": pix.height
            }
            pages.append(img_data)
        return pages
    except Exception as e:
        print(f"PDF Processing Error: {str(e)}")
        return []

# ==== Flask Routes ====

@app.route('/process-selection', methods=['POST'])
def handle_selection():
    try:
        data = request.json
        selection = data.get('text', '').strip()
        if not selection:
            return jsonify({"error": "Empty selection"}), 400
        result = process_text(selection)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/ask', methods=['POST'])
def ask_question():
    try:
        data = request.json
        question = data.get('question', '').strip()
        if not question:
            return jsonify({"error": "Question cannot be empty"}), 400
        response = rag.chat_with_doc(question)
        return jsonify({"answer": response})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/update-pdf', methods=['POST', 'OPTIONS'])
def update_pdf():
    if request.method == "OPTIONS":
        return '', 200
    try:
        data = request.get_json()
        new_link = data.get("link")
        if not new_link:
            return jsonify({"error": "Missing 'link' in request data"}), 400

        result = download_arxiv_pdf(new_link)
        if not result or not os.path.exists(result):
            return jsonify({"error": "Failed to download PDF"}), 500

        global current_pdf_link, current_pdf_path
        current_pdf_link = new_link
        current_pdf_path = result
        rag.reload_rag_model(current_pdf_path)

        return jsonify({"message": "PDF and model updated successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/')
def pdf_viewer():
    global current_pdf_path
    pages = pdf_to_images(current_pdf_path)

    return render_template_string('''
    <!DOCTYPE html>
    <html>
    <head>
        <title>PDF Analyzer & Chatbot</title>
        <style>
            body {
                margin: 0;
                font-family: 'Segoe UI', sans-serif;
                background-color: #f8f9fb;
            }
            .container {
                display: grid;
                grid-template-columns: 2fr 1.8fr;
                height: 100vh;
            }
            .pdf-viewer {
                overflow-y: auto;
                padding: 10px 0 10px 30px;
                background: #f0f0f0;
                display: flex;
                flex-direction: column;
                align-items: center;
            }
            .sidebar {
                display: flex;
                flex-direction: column;
                background: #fff;
                padding: 0 20px;
            }
            .tabs {
                display: flex;
                margin-top: 10px;
            }
            .tab-btn {
                flex: 1;
                padding: 10px;
                text-align: center;
                cursor: pointer;
                background-color: #e0e0e0;
                border: 1px solid #ccc;
                border-bottom: none;
            }
            .tab-btn.active {
                background-color: #ffffff;
                font-weight: bold;
            }
            .tab-content {
                flex: 1;
                border: 1px solid #ccc;
                border-top: none;
                padding: 15px;
                overflow-y: auto;
            }
            .chat-input {
                display: flex;
                margin-top: 10px;
            }
            .chat-input input {
                flex: 1;
                padding: 10px;
                border: 1px solid #ccc;
                border-radius: 6px 0 0 6px;
            }
            .chat-input button {
                padding: 10px 20px;
                border: none;
                background: #007BFF;
                color: white;
                border-radius: 0 6px 6px 0;
                cursor: pointer;
            }
            .message {
                background: #e9ecef;
                border-radius: 8px;
                padding: 10px;
                margin-bottom: 10px;
            }
            .bot-message {
                background: #d0ebff;
            }
            img {
                max-width: 100%;
                margin-bottom: 25px;
                border-radius: 6px;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="pdf-viewer">
                {% for page in pages %}
                <img src="data:image/png;base64,{{ page.image }}" 
                     style="width: {{ page.width * 0.55 }}px; height: {{ page.height * 0.55 }}px">
                {% endfor %}
            </div>
            <div class="sidebar">
                <div class="tabs">
                    <div class="tab-btn active" onclick="switchTab('analysis')">Text Analysis</div>
                    <div class="tab-btn" onclick="switchTab('chat')">Chatbot</div>
                </div>
                <div id="analysis" class="tab-content">
                    <div id="results">Select text in the PDF to see analysis results</div>
                </div>
                <div id="chat" class="tab-content" style="display:none;">
                    <div id="chatHistory"></div>
                    <div class="chat-input">
                        <input id="chatInput" type="text" placeholder="Ask a question...">
                        <button onclick="askBot()">Ask</button>
                    </div>
                </div>
            </div>
        </div>

        <script>
            const resultsDiv = document.getElementById('results');
            const chatInput = document.getElementById('chatInput');
            const chatHistory = document.getElementById('chatHistory');
            let currentSelection = '';

            function switchTab(tabName) {
                document.getElementById('analysis').style.display = tabName === 'analysis' ? 'block' : 'none';
                document.getElementById('chat').style.display = tabName === 'chat' ? 'block' : 'none';
                document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
                document.querySelector(`.tab-btn[onclick*="${tabName}"]`).classList.add('active');
            }

            async function updateAnalysis(selection) {
                try {
                    const response = await fetch('/process-selection', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({text: selection})
                    });
                    const data = await response.json();
                    resultsDiv.innerHTML = `
                        <div class="message bot-message">
                            <strong>Selected Text:</strong>
                            <p style="font-style: italic; color: #555;">${selection}</p>
                            <div style="margin-top: 10px;">
                                ${data.analysis
                                    .replace(/\*\*Operational Context\*\*/g, '<h4 style=\"margin:10px 0 5px;color:#007BFF;\">Operational Context</h4>')
                                    .replace(/\*\*Other Use-cases\*\*/g, '<h4 style=\"margin:15px 0 5px;color:#007BFF;\">Other Use-cases</h4>')
                                }
                            </div>
                        </div>`;
                } catch(error) {
                    resultsDiv.innerHTML = `<div>Error: ${error}</div>`;
                }
            }

            async function askBot() {
                const question = chatInput.value.trim();
                if (!question) return;
                const userMsg = `<div class='message'><strong>You:</strong> ${question}</div>`;
                chatHistory.innerHTML += userMsg;
                chatInput.value = '';
                const res = await fetch('/ask', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ question })
                });
                const data = await res.json();
                const botMsg = `<div class='message bot-message'><strong>Bot:</strong> ${data.answer}</div>`;
                chatHistory.innerHTML += botMsg;
                chatHistory.scrollTop = chatHistory.scrollHeight;
            }

            document.addEventListener('selectionchange', () => {
                const selection = window.getSelection().toString().trim();
                if (selection && selection !== currentSelection) {
                    currentSelection = selection;
                    updateAnalysis(selection);
                }
            });
        </script>
    </body>
    </html>
    ''', pages=pages)

# ==== App Startup ====

if __name__ == '__main__':
    if not current_pdf_path or not os.path.exists(current_pdf_path):
        print("❌ Could not download the PDF. Exiting Flask server startup.")
        exit(1)
    rag.reload_rag_model(current_pdf_path)
    app.run(host='0.0.0.0', port=5001, debug=True)
