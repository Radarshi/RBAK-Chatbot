# Inadev.ai Chatbot: A RAG System with Authentication and RBAC 🤖

This project is a full-stack, retrieval-augmented generation (RAG) chatbot designed to answer questions based on a specific set of documents. It features a secure backend API built with FastAPI and an interactive frontend created with Streamlit.

-----

### Key Features ✨

  * **Retrieval-Augmented Generation (RAG):** The chatbot retrieves relevant information from a vector database (ChromaDB) before generating an answer using Google's Gemini LLM, ensuring responses are grounded in your data.
  * **User Authentication:** A secure login system using JWT (JSON Web Tokens) to protect the API.
  * **Role-Based Access Control (RBAC):** Users can only query documents relevant to their assigned role (e.g., HR, Finance, Tech), preventing unauthorized data access.
  * **Intelligent Routing:** The API has two distinct endpoints to handle different user types, ensuring a clean and secure design.
  * **Hybrid Logic:** The chatbot can answer generic questions (like "What is the time?") without needing to perform a database search.
  * **Interactive Frontend:** A modern, clean user interface built with Streamlit for a great chat experience.

-----

### Project Structure 📂

```
.
├── .env                  # Environment variables and API keys
├── app.py                # FastAPI backend server
├── auth.py               # Authentication and JWT logic
├── config.py             # Global configuration settings
├── ingest.py             # Script to load documents into the vector database
├── streamlit_app.py      # Streamlit frontend application
├── users.py              # Mock user data for development
├── utils.py              # Utility functions for the project
└── sample_docs/          # Folder containing source documents for ingestion
    ├── finance_budget.txt
    ├── hr_policies.txt
    └── tech_onboarding.txt
```

-----

### Prerequisites 🛠️

Before running the application, make sure you have Python 3.9+ installed.

  * **API Keys:**
      * A **Google Gemini API Key** for the LLM. You can get one from [Google AI Studio](https://ai.google.dev/).
      * A **JWT Secret Key**. This is a long, random string you create yourself.
  * **A virtual environment:** Recommended to keep dependencies isolated.

-----

### Installation and Setup 🚀

1.  **Clone the project files:** Create the folder structure above and place the provided code into each file.
2.  **Install dependencies:** Navigate to your project directory in the terminal and run:
    ```bash
    pip install fastapi "uvicorn[standard]" langchain-chroma langchain-huggingface langchain-google-genai python-dotenv "passlib[bcrypt]" "python-jose[cryptography]" streamlit requests
    ```
3.  **Set up the `.env` file:** Create a file named `.env` in your project's root directory and add your API keys.
    ```ini
    GEMINI_API_KEY="your-gemini-api-key-here"
    JWT_SECRET_KEY="a-very-long-and-random-string-for-jwt-signing"
    ```
4.  **Ingest Documents:** Run the ingestion script to populate your vector database. This only needs to be done once.
    ```bash
    python ingest.py
    ```
5.  **Run the FastAPI Backend:** In your first terminal, start the backend server.
    ```bash
    uvicorn app:app --reload
    ```
6.  **Run the Streamlit Frontend:** In a **separate** terminal, start the frontend application.
    ```bash
    streamlit run streamlit_app.py
    ```

-----

### Usage 💬

Access the application by navigating to `http://localhost:8501` in your web browser. You can log in with the following mock credentials:

| Username | Password | Role |
| :--- | :--- | :--- |
| `admin` | `test-password` | `admin` |
| `hr_user` | `test-password` | `hr` |
| `finance_user` | `test-password` | `finance` |
| `tech_user` | `test-password` | `tech` |

  * **Regular Users** (e.g., `hr_user`): After logging in, you can only ask questions about HR-related documents.
  * **Admin User**: After logging in, you can query documents from any role by selecting it from the sidebar. You can also ask generic questions like "What is the time?".
