# === Full Flask App with Embedded PDF Viewer & Chatbot/Text Analysis ===

from flask import Flask, render_template_string, jsonify, request, send_file
import os
import rag
import sys
from flask_cors import CORS
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import flask_implementation
from pdf_from_link import download_arxiv_pdf

app = Flask(__name__)
CORS(app)

from pathlib import Path

current_pdf_link = flask_implementation.link
downloaded_path = download_arxiv_pdf(current_pdf_link)
current_pdf_path = str(Path(downloaded_path).resolve())


def process_text(selection):
    return {
        "analysis": rag.get_contextual_definition(selection)
    }

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

@app.route('/get-pdf')
def get_pdf():
    return send_file(current_pdf_path)

@app.route('/')
def pdf_viewer():
    return render_template_string('''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Interactive RAG Reader</title>
        <style>
            body { margin: 0; font-family: sans-serif; background: #f4f4f4; }
            .container { display: grid; grid-template-columns: 2fr 2fr; height: 100vh; }
            .pdf-section iframe {
                width: 100%; height: 100%; border: none; background: #fff;
            }
            .sidebar { display: flex; flex-direction: column; background: #fff; padding: 0 20px; }
            .tabs { display: flex; margin-top: 10px; }
            .tab-btn {
                flex: 1; padding: 10px; text-align: center; cursor: pointer;
                background-color: #e0e0e0; border: 1px solid #ccc; border-bottom: none;
            }
            .tab-btn.active { background-color: #ffffff; font-weight: bold; }
            .tab-content {
                flex: 1; border: 1px solid #ccc; border-top: none;
                padding: 15px; overflow-y: auto;
            }
            .chat-input {
                display: flex; margin-top: 10px;
            }
            .chat-input input {
                flex: 1; padding: 10px; border: 1px solid #ccc;
                border-radius: 6px 0 0 6px;
            }
            .chat-input button {
                padding: 10px 20px; border: none;
                background: #007BFF; color: white;
                border-radius: 0 6px 6px 0;
                cursor: pointer;
            }
            .message {
                background: #e9ecef; border-radius: 8px; padding: 10px;
                margin-bottom: 10px;
            }
            .bot-message { background: #d0ebff; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="pdf-section">
                <iframe src="/get-pdf"></iframe>
            </div>
            <div class="sidebar">
                <div class="tabs">
                    <div class="tab-btn active" onclick="switchTab('analysis')">Text Analysis</div>
                    <div class="tab-btn" onclick="switchTab('chat')">Chatbot</div>
                </div>
                <div id="analysis" class="tab-content">
                    <textarea id="textInput" placeholder="Paste text from PDF here..." rows="4" style="width:100%;"></textarea>
                    <button onclick="analyzeText()">Analyze</button>
                    <div id="results" style="margin-top:10px;"></div>
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
            function switchTab(tabName) {
                document.getElementById('analysis').style.display = tabName === 'analysis' ? 'block' : 'none';
                document.getElementById('chat').style.display = tabName === 'chat' ? 'block' : 'none';
                document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
                document.querySelector(`.tab-btn[onclick*="${tabName}"]`).classList.add('active');
            }

            async function analyzeText() {
                const selection = document.getElementById('textInput').value.trim();
                if (!selection) return;
                const response = await fetch('/process-selection', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ text: selection })
                });
                const data = await response.json();
                const resultsDiv = document.getElementById('results');
                resultsDiv.innerHTML = `
                    <div class="message bot-message">
                        <strong>Selected Text:</strong>
                        <p style="font-style: italic; color: #555;">${selection}</p>
                        <div style="margin-top: 10px;">
                            ${data.analysis
                                .replace(/\*\*Operational Context\*\*/g, '<h4 style="margin:10px 0 5px;color:#007BFF;">Operational Context</h4>')
                                .replace(/\*\*Other Use-cases\*\*/g, '<h4 style="margin:15px 0 5px;color:#007BFF;">Other Use-cases</h4>')
                            }
                        </div>
                    </div>`;
            }

            async function askBot() {
                const chatInput = document.getElementById('chatInput');
                const question = chatInput.value.trim();
                if (!question) return;
                const chatHistory = document.getElementById('chatHistory');
                chatHistory.innerHTML += `<div class='message'><strong>You:</strong> ${question}</div>`;
                chatInput.value = '';
                const res = await fetch('/ask', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ question })
                });
                const data = await res.json();
                chatHistory.innerHTML += `<div class='message bot-message'><strong>Bot:</strong> ${data.answer}</div>`;
                chatHistory.scrollTop = chatHistory.scrollHeight;
            }
        </script>
    </body>
    </html>
    ''')

if __name__ == '__main__':
    if not current_pdf_path or not os.path.exists(current_pdf_path):
        print("❌ Could not download the PDF. Exiting Flask server startup.")
        exit(1)
    rag.reload_rag_model(current_pdf_path)
    app.run(host='0.0.0.0', port=5001, debug=True)
