import streamlit as st
import requests
import json
from users import MOCK_USERS 

st.set_page_config(page_title="RAG Chatbot", layout="wide")
st.title("Chatbot.ai")

FASTAPI_BASE_URL = "http://127.0.0.1:8000"

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "token" not in st.session_state:
    st.session_state.token = None
if "username" not in st.session_state:
    st.session_state.username = None
if "role" not in st.session_state:
    st.session_state.role = None
if "messages" not in st.session_state:
    st.session_state.messages = []
if "target_role" not in st.session_state:
    st.session_state.target_role = "hr" 

def login_user(username, password):
    try:
        response = requests.post(
            f"{FASTAPI_BASE_URL}/token",
            data={"username": username, "password": password}
        )
        response.raise_for_status()
        token_data = response.json()
        st.session_state.authenticated = True
        st.session_state.token = token_data.get("access_token")
        st.session_state.username = username
        
        from users import MOCK_USERS
        st.session_state.role = MOCK_USERS.get(username).role
        
        st.success(f"Welcome, {username}! You have been authenticated.")
        st.rerun()
    except requests.exceptions.RequestException as e:
        st.error(f"Login failed: {e}")
        st.session_state.authenticated = False

def logout_user():
    st.session_state.authenticated = False
    st.session_state.token = None
    st.session_state.username = None
    st.session_state.role = None
    st.session_state.messages = []
    st.rerun()

if not st.session_state.authenticated:
    st.header("Login")
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        login_button = st.form_submit_button("Login")
        if login_button:
            login_user(username, password)
else:
    st.sidebar.success(f"Logged in as: {st.session_state.username} ({st.session_state.role})")
    st.sidebar.button("Logout", on_click=logout_user)

    if st.session_state.role == "admin":
        st.sidebar.header("Admin Settings")
        roles = list(MOCK_USERS.values())
        role_options = [user.role for user in roles if user.role != "admin"]
        
        try:
            default_index = role_options.index(st.session_state.target_role)
        except ValueError:
            default_index = 0
            
        st.session_state.target_role = st.sidebar.selectbox(
            "Select target documents to query:",
            options=role_options,
            index=default_index
        )
        st.sidebar.info(f"Admin queries will be routed to the '{st.session_state.target_role}' documents.")
    
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("Ask a question about your documents..."):
        st.chat_message("user").markdown(prompt)
        
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        headers = {
            "Authorization": f"Bearer {st.session_state.token}",
            "Content-Type": "application/json"
        }

        if st.session_state.role == "admin":
            endpoint = "/admin_query"
            data = {
                "question": prompt,
                "target_role": st.session_state.target_role
            }
        else:
            endpoint = "/query"
            data = {"question": prompt}
        
        with st.spinner("Fetching response..."):
            try:
                response = requests.post(
                    f"{FASTAPI_BASE_URL}{endpoint}",
                    headers=headers,
                    data=json.dumps(data)
                )
                response.raise_for_status()
                response_data = response.json()
                answer = response_data.get("answer")
                
                bot_message = f"**Answer:**\n{answer}\n\n"
                
                with st.chat_message("assistant"):
                    st.markdown(bot_message)
                
                st.session_state.messages.append({"role": "assistant", "content": bot_message})
            
            except requests.exceptions.HTTPError as e:
                error_response = e.response.json()
                st.error(f"Error: {error_response.get('detail')}")
                st.session_state.messages.append({"role": "assistant", "content": f"Error: {error_response.get('detail')}"})
            except requests.exceptions.RequestException as e:
                st.error(f"An error occurred: {e}")
                st.session_state.messages.append({"role": "assistant", "content": f"An error occurred: {e}"})