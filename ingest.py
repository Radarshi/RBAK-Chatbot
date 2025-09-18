import os
from langchain_community.document_loaders import TextLoader
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from config import PERSIST_DIR
from utils import normalize_collection_name

SOURCE_DIR = "sample_docs"
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

def ingest_documents():
    """Ingests documents from SOURCE_DIR and organizes them into Chroma collections by inferred role."""
    
    role_mapping = {
        "hr_policies": "hr",
        "finance_budget": "finance",
        "tech_onboarding": "tech"
    }
    
    docs_by_collection = {normalize_collection_name(role): [] for role in role_mapping.values()}

    print(f"Loading documents from {SOURCE_DIR}...")
    
    for filename in os.listdir(SOURCE_DIR):
        file_path = os.path.join(SOURCE_DIR, filename)
        
        role = None
        for prefix, inferred_role in role_mapping.items():
            if filename.startswith(prefix):
                role = inferred_role
                break
        
        if not role:
            print(f"Skipping {filename}: No role mapping found.")
            continue
            
        collection_name = normalize_collection_name(role)
        
        print(f"Loading {filename} for collection '{collection_name}'...")
        loader = TextLoader(file_path)
        documents = loader.load()
        
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
        texts = text_splitter.split_documents(documents)
        docs_by_collection[collection_name].extend(texts)
    
    for collection_name, texts in docs_by_collection.items():
        if texts:
            print(f"\nProcessing {len(texts)} chunks for collection '{collection_name}'...")
            Chroma.from_documents(
                documents=texts,
                embedding=embeddings,
                collection_name=collection_name,
                persist_directory=PERSIST_DIR
            )
            print(f"Collection '{collection_name}' created successfully!")
        else:
            print(f"\nNo documents found for collection '{collection_name}'. Skipping.")
            
    print("\nDocument ingestion complete.")

if __name__ == "__main__":
    ingest_documents()