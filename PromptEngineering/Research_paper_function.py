from flask import Flask, request, jsonify
from flask_cors import CORS  # Import CORS for cross-origin requests
import google.generativeai as genai
from dotenv import load_dotenv
import os
from API_KEY import API_KEY
from Search_Papers import search_most_cited_papers

# Load environment variables
load_dotenv()

# Configure the API key
genai.configure(api_key=API_KEY)

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Function to generate a short query
def generate_short_query(long_prompt):
    query_prompt = f"""Given the following long prompt, generate a concise 5-10 word query that captures the main topic for searching on Google Scholar:

Long Prompt: {long_prompt}

Short Query (5-10 words):"""

    response = genai.GenerativeModel(
        'gemini-1.5-flash-latest',
        generation_config=genai.GenerationConfig(
            temperature=0.7,
            top_p=1,
            max_output_tokens=100,
        )
    ).generate_content(query_prompt)
    
    return response.text.strip()

@app.route("/search", methods=["POST"])
def search_papers():
    try:
        data = request.get_json()
        search_term = data.get("searchTerm", "")

        if not search_term:
            return jsonify({"error": "No search term provided"}), 400

        print(f"Received search term: {search_term}")

        # Generate a short query based on input
        long_prompt = f"I am looking for a research paper related to {search_term}."
        short_query = generate_short_query(long_prompt)

        print(f"Generated Short Query: {short_query}")

        # Search for the most cited papers using the short query
        search_results = search_most_cited_papers(short_query)
        print(search_results)
        return jsonify({
            "message": "Search executed successfully",
            "query": short_query,
            "results": search_results  # Include the results from search_most_cited_papers
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, port=5000)
