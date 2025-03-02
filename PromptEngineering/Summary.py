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

# Test Function
if __name__ == "__main__":
    api_key = "AIzaSyCltlvD2095OCXy1P8PzlTynoO9NIsUCaQ"  
#    paper_content = """
#     Title: Advances in Artificial Intelligence for Medical Diagnosis

# Abstract:
# Artificial Intelligence (AI) has seen rapid growth in the medical field, particularly in disease diagnosis, personalized treatment, and patient monitoring. AI-based models, particularly deep learning architectures, have shown superior accuracy in detecting diseases from medical imaging, electronic health records, and genetic data. However, challenges such as data privacy, model interpretability, and clinical adoption remain significant hurdles. This paper explores the latest advancements in AI for medical diagnosis, the role of machine learning in predictive healthcare, and the challenges faced in real-world implementation.

# Introduction:
# The integration of AI into medical diagnosis has revolutionized the way healthcare professionals detect and treat diseases. Traditionally, disease diagnosis relied on human expertise and laboratory testing, which, while effective, had limitations in speed and accuracy. AI-powered models, particularly deep learning-based approaches, have demonstrated remarkable improvements in automating diagnostic tasks. For instance, convolutional neural networks (CNNs) have surpassed human radiologists in detecting lung cancer and breast tumors from X-ray and MRI scans.

# Machine learning algorithms, including support vector machines (SVMs) and random forests, are being used to analyze vast amounts of patient data to detect patterns that indicate early symptoms of diseases such as Alzheimer's, diabetes, and cardiovascular disorders. Moreover, reinforcement learning has been applied to optimize treatment plans and predict patient outcomes.

# Despite these advancements, the adoption of AI in medical diagnosis faces numerous challenges. Data privacy concerns arise due to the sensitive nature of patient information. Furthermore, the lack of interpretability in deep learning models makes it difficult for clinicians to trust AI-based recommendations. The need for regulatory approval and extensive clinical validation further delays the integration of AI into mainstream medical practice.

# This paper reviews recent breakthroughs in AI-driven medical diagnosis, focusing on image-based diagnostics, natural language processing in electronic health records, and predictive analytics in personalized medicine. We also discuss ethical considerations, data security, and the future potential of AI in transforming healthcare.

#     """

#     summary = summarize_research_paper(api_key, paper_content)
#     print("Generated Summary:\n", summary)
