import streamlit as st
import ollama
import os
import json
import datetime
from security import verify_deployment

verify_deployment()

desiredModel = "deepseek-r1:8b"

# Set page config with menu items for help, bug report, and about
st.set_page_config(
    page_title="Manas-GPT | AI Chat Assistant",
    page_icon=":robot_face:",
    layout="centered",
    menu_items={
        'Get Help': 'https://github.com/mdkulkarni2005/manas-gpt',
        'Report a bug': "https://github.com/mdkulkarni2005/manas-gpt/issues",
        'About': f"Created by Manas D. Kulkarni - {datetime.datetime.now().year}"
    }
)

# Custom CSS for modern UI/UX design
st.markdown("""
    <style>
        body {
            font-family: 'Poppins', sans-serif;
            background-color: #f4f4f4;
        }
        .header {
            background-color: #1a73e8;
            padding: 20px 0;
            border-radius: 8px;
            color: white;
            text-align: center;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
            margin-bottom: 20px;
        }
        .header h2 {
            font-size: 2em;
            margin-bottom: 10px;
        }
        .header p {
            font-size: 1.1em;
            margin-top: 0;
        }
        .header a {
            text-decoration: none;
            color: white;
            padding: 10px;
            margin: 0 15px;
            font-size: 1.2em;
            border-radius: 5px;
            transition: background-color 0.3s, transform 0.3s;
        }
        .header a:hover {
            background-color: #0f59c1;
            transform: translateY(-2px);
        }
        .footer {
            position: fixed;
            bottom: 10px;
            right: 10px;
            background-color: rgba(255, 255, 255, 0.8);
            padding: 10px;
            border-radius: 5px;
            font-size: 12px;
            text-align: center;
        }
        .footer a {
            color: #1a73e8;
            text-decoration: none;
        }
    </style>
""", unsafe_allow_html=True)

# Header with custom design
st.markdown("""
    <div class="header">
        <h2>Manas-GPT | AI Chat Assistant</h2>
        <p>
            <a href="https://github.com/mdkulkarni2005/manas-gpt" target="_blank">
                <img src="https://img.icons8.com/ios/50/ffffff/github.png" alt="GitHub" style="vertical-align: middle; height: 25px;"/>
                GitHub
            </a>
            <a href="https://www.linkedin.com/in/mdkulkarni2005" target="_blank">
                <img src="https://img.icons8.com/ios/50/ffffff/linkedin.png" alt="LinkedIn" style="vertical-align: middle; height: 25px;"/>
                LinkedIn
            </a>
            <a href="https://yourwebsite.com" target="_blank">
                <img src="https://img.icons8.com/ios/50/ffffff/domain.png" alt="Website" style="vertical-align: middle; height: 25px;"/>
                Website
            </a>
        </p>
    </div>
""", unsafe_allow_html=True)

if "chats" not in st.session_state:
    st.session_state.chats = {"Default Chat": []}
if "current_chat" not in st.session_state:
    st.session_state.current_chat = "Default Chat"

# Sidebar section for chat management
st.sidebar.title("Chat Management")
chat_name = st.sidebar.text_input("New Chat Name", "")
if st.sidebar.button("Create Chat") and chat_name:
    st.session_state.chats[chat_name] = []
    st.session_state.current_chat = chat_name

delete_chat = st.sidebar.selectbox("Delete Chat", ["Select"] + list(st.session_state.chats.keys()))
if st.sidebar.button("Delete") and delete_chat != "Select":
    del st.session_state.chats[delete_chat]
    st.session_state.current_chat = "Default Chat"

selected_chat = st.sidebar.radio("Select Chat", list(st.session_state.chats.keys()))
st.session_state.current_chat = selected_chat

def generate_response(questionToAsk):
    """Function to generate streamed response from the LLM."""
    response_container = st.empty()
    full_response = ""
    
    with st.spinner("Generating response..."):
        chat_history = st.session_state.chats.get(st.session_state.current_chat, [])
        response = ollama.chat(
            model=desiredModel,
            messages=chat_history + [{'role': 'user', 'content': questionToAsk}],
            stream=True,
        )
        
        for chunk in response:
            full_response += chunk['message']['content']
            response_container.markdown(f"**{full_response}**")
    
    response_container.markdown(f"**{full_response}**")
    
    st.session_state.chats[st.session_state.current_chat].append({'role': 'user', 'content': questionToAsk})
    st.session_state.chats[st.session_state.current_chat].append({'role': 'assistant', 'content': full_response})

# Form for user input and question submission
with st.form("chat_form"):
    user_input = st.text_area("Ask your question:", "Type here...")
    submitted = st.form_submit_button("Submit")
    if submitted and user_input.strip():
        st.chat_message("user").markdown(user_input)
        st.chat_message("assistant")
        generate_response(user_input)

# Sidebar for additional features
st.sidebar.subheader("Additional Features")
if st.sidebar.button("Clear Chat History"):
    st.session_state.chats[st.session_state.current_chat] = []
    st.experimental_rerun()
if st.sidebar.button("Export Chat History"):
    chat_data = json.dumps(st.session_state.chats, indent=4)
    st.sidebar.download_button("Download Chat History", chat_data, file_name="chat_history.json")

# Footer for copyright and GitHub link
st.markdown("""
    <div class="footer">
        © 2024 Manas D. Kulkarni - All Rights Reserved<br>
        <a href='https://github.com/mdkulkarni2005/manas-gpt'>GitHub Repository</a>
    </div>
""", unsafe_allow_html=True)
