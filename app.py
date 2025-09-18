import os
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
from config import PERSIST_DIR
from utils import normalize_collection_name
from auth import get_current_user, create_access_token
from users import MOCK_USERS, UserInDB
from fastapi.middleware.cors import CORSMiddleware
from langchain_core.documents import Document
from datetime import datetime

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY not set in .env")

app = FastAPI()

origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",
    api_key=GEMINI_API_KEY
)

class QueryRequest(BaseModel):
    question: str

class AdminQueryRequest(BaseModel):
    question: str
    target_role: str

def handle_generic_questions(question: str, current_user: UserInDB):
    question_lower = question.lower()
    
    if "who am i" in question_lower or "my name" in question_lower:
        return f"You are authenticated as {current_user.username} with the role of {current_user.role}."
    
    if "time" in question_lower or "date" in question_lower:
        return f"The current time is {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}."
    
    if "hello" in question_lower or "hi" in question_lower or "hola" in question_lower:
        return "Hello! How can I assist you with your documents?"
    
    if "bye" in question_lower or "goodbye" in question_lower or "tata" in question_lower or "see you" in question_lower:
        return "See you next time buddy. I am always here for you🙌"
    
    if "thank you" in question_lower or "thanks" in question_lower:
        return "You're welcome"
    
    return None

@app.post("/token")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = MOCK_USERS.get(form_data.username)
    if not user or user.password != form_data.password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/query")
async def query(req: QueryRequest, current_user: UserInDB = Depends(get_current_user)):
    if current_user.role == "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin users must use the /admin_query endpoint."
        )

    print(f"Authenticated User: {current_user.username} (Role: {current_user.role})")
    user_role = current_user.role
    
    generic_answer = handle_generic_questions(req.question, current_user)
    if generic_answer:
        return {
            "question": req.question,
            "role": user_role,
            "answer": generic_answer,
            "sources": []
        }

    try:
        collection_name = normalize_collection_name(user_role)
        vectorstore = Chroma(
            collection_name=collection_name,
            embedding_function=embeddings,
            persist_directory=PERSIST_DIR
        )

        retriever = vectorstore.as_retriever(search_kwargs={"k": 3})
        source_documents = retriever.invoke(req.question)
        context = "\n\n".join([doc.page_content for doc in source_documents])

        final_prompt = f"""You are a helpful assistant. Use the following pieces of retrieved context to answer the question. If you don't know the answer, just say that you don't know. Use three sentences maximum and keep the answer concise.

Context:
{context}

Question:
{req.question}"""

        llm_response = llm.invoke(final_prompt)
        answer = llm_response.content

        sources = [
            {"content": doc.page_content, "metadata": doc.metadata}
            for doc in source_documents
        ]

        return {
            "question": req.question,
            "role": user_role,
            "answer": answer,
            "sources": sources
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/admin_query")
async def admin_query(req: AdminQueryRequest, current_user: UserInDB = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin users can access this endpoint."
        )

    print(f"Authenticated User: {current_user.username} (Role: {current_user.role}) querying as '{req.target_role}'")

    generic_answer = handle_generic_questions(req.question, current_user)
    if generic_answer:
        return {
            "question": req.question,
            "role": req.target_role,
            "answer": generic_answer,
            "sources": []
        }

    try:
        collection_name = normalize_collection_name(req.target_role)
        vectorstore = Chroma(
            collection_name=collection_name,
            embedding_function=embeddings,
            persist_directory=PERSIST_DIR
        )

        retriever = vectorstore.as_retriever(search_kwargs={"k": 3})
        source_documents = retriever.invoke(req.question)
        context = "\n\n".join([doc.page_content for doc in source_documents])

        final_prompt = f"""You are a helpful assistant. Use the following pieces of retrieved context to answer the question. If you don't know the answer, just say that you don't know. Use three sentences maximum and keep the answer concise.

Context:
{context}

Question:
{req.question}"""

        llm_response = llm.invoke(final_prompt)
        answer = llm_response.content

        sources = [
            {"content": doc.page_content, "metadata": doc.metadata}
            for doc in source_documents
        ]

        return {
            "question": req.question,
            "role": req.target_role,
            "answer": answer,
            "sources": sources
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))