import streamlit as st
import ollama
import os
import json
import datetime
import base64
from PIL import Image
import pytesseract
import fitz  # PyMuPDF
from security import verify_deployment

verify_deployment()

desiredModel = "deepseek-r1:8b"

# Set page config
st.set_page_config(
    page_title="Manas-GPT | AI Chat Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Enhanced CSS for Claude-like interface
st.markdown("""
    <style>
        .stTextArea textarea {
            border-radius: 15px;
            border: 1px solid #e0e0e0;
            padding: 15px;
            font-size: 16px;
            transition: all 0.3s ease;
        }
        .stTextArea textarea:focus {
            border-color: #1a73e8;
            box-shadow: 0 0 0 2px rgba(26, 115, 232, 0.2);
        }
        
        .chat-message {
            padding: 1.5rem;
            border-radius: 15px;
            margin-bottom: 1rem;
            animation: fadeIn 0.5s ease-in-out;
        }
        
        .user-message {
            background-color: #E3F2FD;
            margin-left: 2rem;
        }
        
        .assistant-message {
            background-color: #F5F5F5;
            margin-right: 2rem;
        }
        
        .stButton button {
            border-radius: 25px;
            padding: 0.5rem 1.5rem;
            font-weight: 500;
            transition: all 0.3s ease;
            border: none;
            background-color: #1a73e8;
            color: white;
        }
        
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        /* Hide default Streamlit elements */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if "chats" not in st.session_state:
    st.session_state.chats = {"Default Chat": []}
if "current_chat" not in st.session_state:
    st.session_state.current_chat = "Default Chat"
if "file_uploads" not in st.session_state:
    st.session_state.file_uploads = {}
if "waiting_for_response" not in st.session_state:
    st.session_state.waiting_for_response = False

def process_file(file):
    """Process uploaded files and extract text content."""
    file_type = file.type
    content = ""
    
    try:
        if file_type.startswith('image'):
            image = Image.open(file)
            content = pytesseract.image_to_string(image)
        elif file_type == 'application/pdf':
            pdf = fitz.open(stream=file.read(), filetype="pdf")
            for page in pdf:
                content += page.get_text()
        else:
            content = file.read().decode('utf-8')
        return content
    except Exception as e:
        return f"Error processing file: {str(e)}"

def generate_response(question, file_content=None):
    """Enhanced response generation with file content support."""
    response_container = st.empty()
    full_response = ""
    
    with st.spinner("Processing..."):
        if file_content:
            question = f"Context from uploaded file:\n{file_content}\n\nQuestion: {question}"
        
        chat_history = st.session_state.chats[st.session_state.current_chat]
        response = ollama.chat(
            model=desiredModel,
            messages=chat_history + [{'role': 'user', 'content': question}],
            stream=True
        )
        
        for chunk in response:
            full_response += chunk['message']['content']
            response_container.markdown(f"{full_response}", unsafe_allow_html=True)
    
    st.session_state.chats[st.session_state.current_chat].extend([
        {'role': 'user', 'content': question},
        {'role': 'assistant', 'content': full_response}
    ])
    st.session_state.waiting_for_response = False

# Sidebar
with st.sidebar:
    st.title("💬 Chat Management")
    
    new_chat = st.text_input("Create New Chat", placeholder="Enter chat name...")
    if st.button("Create Chat") and new_chat:
        st.session_state.chats[new_chat] = []
        st.session_state.current_chat = new_chat
        st.rerun()
    
    st.subheader("Select Chat")
    for chat in st.session_state.chats.keys():
        if st.sidebar.button(chat, key=f"select_{chat}"):
            st.session_state.current_chat = chat
            st.rerun()
    
    if st.button("Export Chat History"):
        chat_data = json.dumps(st.session_state.chats, indent=4)
        b64 = base64.b64encode(chat_data.encode()).decode()
        href = f'<a href="data:text/json;base64,{b64}" download="chat_history.json">Download Chat History</a>'
        st.markdown(href, unsafe_allow_html=True)

# Main chat interface
st.title(f"Current Chat: {st.session_state.current_chat}")

# Display chat history
chat_container = st.container()
with chat_container:
    for message in st.session_state.chats[st.session_state.current_chat]:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# Input form - only show at bottom if there are messages and we're not waiting for a response
if len(st.session_state.chats[st.session_state.current_chat]) == 0 or st.session_state.waiting_for_response:
    input_container = st.container()
else:
    # Create some space to push the input to the bottom
    st.markdown("<br>" * 3, unsafe_allow_html=True)
    input_container = st.container()

with input_container:
    with st.form(key="chat_form", clear_on_submit=True):
        uploaded_file = st.file_uploader("Upload a file", type=['png', 'jpg', 'jpeg', 'pdf', 'txt'])
        user_input = st.text_area("Message", key="user_input", height=100)
        col1, col2, col3 = st.columns([1, 1, 4])
        
        with col1:
            submit = st.form_submit_button("Send")
        with col2:
            clear = st.form_submit_button("Clear Chat")
        
        if submit and user_input:
            st.session_state.waiting_for_response = True
            file_content = None
            if uploaded_file:
                file_content = process_file(uploaded_file)
            
            with chat_container:
                with st.chat_message("user"):
                    st.markdown(user_input)
                
                with st.chat_message("assistant"):
                    generate_response(user_input, file_content)
            
        if clear:
            st.session_state.chats[st.session_state.current_chat] = []
            st.session_state.waiting_for_response = False
            st.rerun()