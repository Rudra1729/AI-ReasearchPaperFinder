import google.generativeai as genai
from dotenv import load_dotenv
import os
from API_KEY import API_KEY
from Search_Papers import search_most_cited_papers

# Load environment variables
load_dotenv()

# Configure the API key
genai.configure(api_key=API_KEY)

model = genai.GenerativeModel(
    'gemini-1.5-flash-latest',
    generation_config=genai.GenerationConfig(
        temperature=0.7,
        top_p=1,
        max_output_tokens=100,
    ))

def generate_short_query(long_prompt):
    query_prompt = f"""Given the following long prompt, generate a concise 5-10 word query that captures the main topic for searching on Google Scholar:

Long Prompt: {long_prompt}

Short Query (5-10 words):"""

    response = model.generate_content(query_prompt)
    return response.text.strip()

# Example usage
long_prompt = """I am looking for a research paper in the field of protein manufacturing that explores the role of Artificial Intelligence (AI) in optimizing protein design, synthesis, or large-scale production. The paper should discuss key AI-driven approaches such as deep learning models for protein folding (e.g., AlphaFold), generative models for protein engineering, or AI-based process optimization in biopharmaceutical manufacturing.

It should highlight advancements in AI methodologies applied to protein structure prediction, sequence optimization, or yield improvement in bioprocessing. The research should also discuss challenges such as computational efficiency, data limitations, and real-world implementation in industrial settings. If available, I would like insights into how AI is used to enhance precision, reduce production costs, or accelerate drug discovery through protein manufacturing.

The paper should come from a reputable source, such as journals like Nature Biotechnology, Science, Cell, or conferences like NeurIPS, ICML, or ISMB. It should be published within the last five years (2020-present) to ensure it reflects the latest advancements in the field.

Additionally, if possible, include information on the authors affiliations, methodology, experimental validation, and key findings. A link to the paper or DOI reference would be appreciated."""

short_query = generate_short_query(long_prompt)
print(f"Short Query: {short_query}")

search_most_cited_papers(short_query)
