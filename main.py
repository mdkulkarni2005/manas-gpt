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

# Enhanced CSS for modern UI/UX design
st.markdown("""
    <style>
        /* Modern Chat Interface */
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
        
        /* Chat Messages */
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
        
        /* Buttons */
        .stButton button {
            border-radius: 25px;
            padding: 0.5rem 1.5rem;
            font-weight: 500;
            transition: all 0.3s ease;
            border: none;
            background-color: #1a73e8;
            color: white;
        }
        .stButton button:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
        }
        
        /* File Upload */
        .upload-container {
            border: 2px dashed #1a73e8;
            border-radius: 15px;
            padding: 20px;
            text-align: center;
            margin: 20px 0;
            transition: all 0.3s ease;
        }
        .upload-container:hover {
            background-color: rgba(26, 115, 232, 0.05);
        }
        
        /* Animations */
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        /* Sidebar */
        .css-1d391kg {
            background-color: #f8f9fa;
        }
        
        /* Chat Title */
        .chat-title {
            font-size: 1.2rem;
            color: #1a73e8;
            margin-bottom: 1rem;
            padding-bottom: 0.5rem;
            border-bottom: 2px solid #1a73e8;
        }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if "chats" not in st.session_state:
    st.session_state.chats = {"Default Chat": []}
if "current_chat" not in st.session_state:
    st.session_state.current_chat = "Default Chat"
if "file_uploads" not in st.session_state:
    st.session_state.file_uploads = {}

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
        # Prepare context with file content if available
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
    
    # Save to chat history
    st.session_state.chats[st.session_state.current_chat].extend([
        {'role': 'user', 'content': question},
        {'role': 'assistant', 'content': full_response}
    ])

# Sidebar for chat management
with st.sidebar:
    st.title("💬 Chat Management")
    
    # Create new chat
    new_chat = st.text_input("Create New Chat", placeholder="Enter chat name...")
    if st.button("Create Chat") and new_chat:
        st.session_state.chats[new_chat] = []
        st.session_state.current_chat = new_chat
        st.experimental_rerun()
    
    # Select chat
    st.subheader("Select Chat")
    for chat in st.session_state.chats.keys():
        if st.sidebar.button(chat, key=f"select_{chat}"):
            st.session_state.current_chat = chat
            st.experimental_rerun()
    
    # Export chat
    if st.button("Export Chat History"):
        chat_data = json.dumps(st.session_state.chats, indent=4)
        b64 = base64.b64encode(chat_data.encode()).decode()
        href = f'<a href="data:text/json;base64,{b64}" download="chat_history.json">Download Chat History</a>'
        st.markdown(href, unsafe_allow_html=True)

# Main chat interface
st.title(f"Current Chat: {st.session_state.current_chat}")

# Display chat history
for message in st.session_state.chats[st.session_state.current_chat]:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# File upload
uploaded_file = st.file_uploader("Upload a file (Images, PDFs, Text files)", 
                               type=['png', 'jpg', 'jpeg', 'pdf', 'txt'])

# Chat input
with st.form(key="chat_form"):
    user_input = st.text_area("Type your message:", key="user_input")
    col1, col2 = st.columns([1, 5])
    
    with col1:
        submit = st.form_submit_button("Send")
    
    if submit and user_input:
        file_content = None
        if uploaded_file:
            file_content = process_file(uploaded_file)
        
        with st.chat_message("user"):
            st.markdown(user_input)
        
        with st.chat_message("assistant"):
            generate_response(user_input, file_content)

# Clear chat button
if st.button("Clear Chat"):
    st.session_state.chats[st.session_state.current_chat] = []
    st.experimental_rerun()