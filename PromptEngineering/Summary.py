import requests
import json

def summarize_research_paper(api_key: str, paper_content: str) -> str:
    """
    Summarizes a research paper using the Gemini-1.5-Flash model via Google API.
    """

    # Correct API endpoint for Gemini-1.5-Flash
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"

    # Headers for the request
    headers = {
        "Content-Type": "application/json"
    }

    # Zero-shot prompt for summary generation
    payload = {
        "contents": [{
            "parts": [{"text": f"Summarize the following research paper in 200 words:\n\n{paper_content}"}]
        }]
    }

    try:
        # Send request to the API
        response = requests.post(url, headers=headers, json=payload)

        # Check if the response is successful
        if response.status_code != 200:
            return f"API Error: {response.status_code}, {response.text}"

        response_data = response.json()

        # Extracting the generated text properly
        if "candidates" in response_data and response_data["candidates"]:
            summary = response_data["candidates"][0]["content"]["parts"][0]["text"]
            return summary
        else:
            return "No summary generated. Check API response format."

    except Exception as e:
        return f"An error occurred: {str(e)}"

