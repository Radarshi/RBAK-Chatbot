from pathlib import Path

BASE_DIR = Path(__file__).parent
PERSIST_DIR = BASE_DIR / "chroma_db"
CHROMA_COLLECTION = "rbak_collection"
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
JWT_SECRET_KEY = "rbak41"
ALGORITHM = "HS256"
JWT_EXPIRE_SECONDS = 3600

TOP_K = 5