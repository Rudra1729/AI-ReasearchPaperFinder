# RAG model implementation

import google.generativeai as genai
from chromadb import Documents, EmbeddingFunction, Embeddings
from google.api_core import retry
import chromadb
from data_extraction import extract_sections

GOOGLE_API_KEY = "ENTER YOUR API KEY"
genai.configure(api_key=GOOGLE_API_KEY)

def create_documents_from_dict(topic_text_dict):
    documents = []
    
    for topic, text in topic_text_dict.items():
        # Combine the topic with its content in a single document string
        document = f"{topic}\n{text}"
        documents.append(document)
    
    return documents

topic_text_dict = extract_sections("research.pdf")
# Generate list of documents
documents = create_documents_from_dict(topic_text_dict)

# Output
'''
for i, doc in enumerate(documents):
    print(f"Document {i+1}:\n{doc}\n")
'''

class GeminiEmbeddingFunction(EmbeddingFunction):
    # Specify whether to generate embeddings for documents, or queries
    document_mode = True

    def __call__(self, input: Documents) -> Embeddings:
        if self.document_mode:
            embedding_task = "retrieval_document"
        else:
            embedding_task = "retrieval_query"

        retry_policy = {"retry": retry.Retry(predicate=retry.if_transient_error)}

        response = genai.embed_content(
            model="models/text-embedding-004",
            content=input,
            task_type=embedding_task,
            request_options=retry_policy,
        )
        return response["embedding"]

# Initialize ChromaDB collection (keep existing DB setup code)
chroma_client = chromadb.Client()
db = chroma_client.get_or_create_collection(name="googlecardb", embedding_function=GeminiEmbeddingFunction())
db.add(documents=documents, ids=[str(i) for i in range(len(documents))])

def get_contextual_definition(highlighted_text):
    # Get user input
    
    search_term = highlighted_text.strip()
    
    # Query ChromaDB
    results = db.query(query_texts=[search_term], n_results=1)
    [[passage]] = results["documents"]
    
    # Create explanation prompt
    prompt = f"""Explain the specific meaning and context of the term '{search_term}' 
    based EXCLUSIVELY on this technical document passage and give a properly structured answer with proper line spacing and framework. Include:
    1. Operational context

    2. Other Use cases
    Give me the answer in a paragraph with two headings Operational context and other use-cases. Make sure that each of these paragraphs do not exceed 50 words.
    Passage: {passage.replace('\n', ' ')}"""
    
    # Generate and return answer
    model = genai.GenerativeModel("gemini-1.5-flash-latest")
    response = model.generate_content(prompt)
    s = f"\nContextual meaning of '{search_term}':"
    return(s + response.text)

# Run the interactive lookup
'''
for highlighted_text in clipboard_highight_monitor():
    print(get_contextual_definition(highlighted_text))
'''