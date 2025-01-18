import streamlit as st
from langchain_core.prompts import (
    ChatPromptTemplate,
    MessagesPlaceholder,
    HumanMessagePromptTemplate,
)
from langchain_core.messages import SystemMessage
from langchain.memory import ConversationBufferWindowMemory
from langchain_groq import ChatGroq
import json
from dotenv import load_dotenv
import os

def load_personas(file_path):
    """Load persona data from a text file"""
    with open(file_path, 'r', encoding='utf-8') as file:
        return json.load(file)

def load_global_persona_notes(file_path):
    """Load global persona notes from a text file"""
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read().strip()

def main():

    """
    Main entry point of the Streamlit chat application with persona card selection.
    """
    # Load environment variables
    load_dotenv()

    # Retrieve API Key from .env file
    # groq_api_key = os.getenv('GROQ_API_KEY')
    groq_api_key = st.secrets["GROQ_API_KEY"]
    if not groq_api_key:
        st.error("API key not found. Please check your .env file.")

    model = 'llama3-8b-8192'  # Hardcoded model
    memory_length = 5  # Hardcoded conversational memory length

    # Centered Main Title
    st.markdown("<h1 style='text-align: center;'>Personas</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; margin-top:-20px;opacity:50%'>Therapy personas to simulate real client interactions and responses.</p>", unsafe_allow_html=True)

    # Load personas and global persona notes from files
    personas = load_personas("personas.txt")
    global_persona_notes = load_global_persona_notes("globalPersonaNote.txt")

    # Card Selection
    st.sidebar.header("Select a Persona")
    selected_category = st.sidebar.selectbox("Choose Category:", list(personas.keys()))
    selected_persona = st.sidebar.radio("Choose Persona:", [p["name"] for p in personas[selected_category]])

    # Fetch the corresponding prompt
    selected_prompt = next(p["prompt"] for p in personas[selected_category] if p["name"] == selected_persona)

    # Append global persona notes
    full_prompt = f"{selected_prompt}\n\n{global_persona_notes}"

    # Clear chat and memory if persona changes
    if 'current_persona' not in st.session_state or st.session_state.current_persona != selected_persona:
        st.session_state.chat_history = []
        st.session_state.current_persona = selected_persona

    # Subheading with centered and italic styling
    st.markdown(f"<h3 style='text-align: center; font-style: italic; opacity:1'>{selected_persona}</h3>", unsafe_allow_html=True)

    # Initialize chat history
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []

    # Groq Chat model setup
    groq_chat = ChatGroq(groq_api_key=groq_api_key, model_name=model)
    memory = ConversationBufferWindowMemory(k=memory_length, return_messages=True)

    # Chat Input UI
    user_input = st.chat_input("Say something...")

    # Process user input
    if user_input:
        prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content=full_prompt),
            MessagesPlaceholder(variable_name="chat_history"),
            HumanMessagePromptTemplate.from_template("{human_input}")
        ])

        conversation = prompt | groq_chat
        response = conversation.invoke({"chat_history": st.session_state.chat_history, "human_input": user_input})
        response_content = response if isinstance(response, str) else response.content

        st.session_state.chat_history.append({"role": "user", "content": user_input})
        st.session_state.chat_history.append({"role": "assistant", "content": response_content})

    # Display chat history
    for message in st.session_state.chat_history:
        if message["role"] == "user":
            with st.chat_message("user"):
                st.markdown(message["content"])
        elif message["role"] == "assistant":
            with st.chat_message("assistant"):
                st.markdown(message["content"])

if __name__ == "__main__":
    main()
