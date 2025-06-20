import streamlit as st
import requests
import json
from dotenv import load_dotenv
import os
from langchain_core.prompts import (
    ChatPromptTemplate,
    MessagesPlaceholder,
    HumanMessagePromptTemplate,
)
from langchain_core.messages import SystemMessage
from langchain.memory import ConversationBufferWindowMemory
from langchain_groq import ChatGroq

# 🔒 Backend endpoint to verify Firebase ID token
BACKEND_VERIFY_URL = "https://personaus-auth-backend-production.up.railway.app/verify-token"

def load_personas(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return json.load(file)

def load_global_persona_notes(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read().strip()

def verify_token(id_token):
    try:
        res = requests.post(BACKEND_VERIFY_URL, json={"idToken": id_token})
        if res.status_code == 200:
            return res.json().get("email")
        return None
    except Exception as e:
        print("Token verification failed:", e)
        return None

def main():
    load_dotenv()


    # ✅ ORIGINAL FUNCTIONALITY BELOW
    groq_api_key = st.secrets["GROQ_API_KEY"]
    if not groq_api_key:
        st.error("API key not found. Please check your .env file.")

    model = 'llama3-8b-8192'
    memory_length = 5

    st.markdown("<h1 style='text-align: center;'>Personaus</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; margin-top:-20px;opacity:50%'>Therapy personas to simulate real client interactions and responses.</p>", unsafe_allow_html=True)

    personas = load_personas("personas.txt")
    global_persona_notes = load_global_persona_notes("globalPersonaNote.txt")

    st.sidebar.header("Select a Persona")
    selected_category = st.sidebar.selectbox("Choose Category:", list(personas.keys()))
    selected_persona = st.sidebar.radio("Choose Persona:", [p["name"] for p in personas[selected_category]])

    selected_prompt = next(p["prompt"] for p in personas[selected_category] if p["name"] == selected_persona)
    full_prompt = f"{selected_prompt}\n\n{global_persona_notes}"

    if 'current_persona' not in st.session_state or st.session_state.current_persona != selected_persona:
        st.session_state.chat_history = []
        st.session_state.current_persona = selected_persona

    st.markdown(f"<h3 style='text-align: center; font-style: italic; opacity:1'>{selected_persona}</h3>", unsafe_allow_html=True)

    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []

    groq_chat = ChatGroq(groq_api_key=groq_api_key, model_name=model)
    memory = ConversationBufferWindowMemory(k=memory_length, return_messages=True)

    user_input = st.chat_input("Say something...")

    if user_input:
        prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content=full_prompt),
            MessagesPlaceholder(variable_name="chat_history"),
            HumanMessagePromptTemplate.from_template("{human_input}")
        ])

        conversation = prompt | groq_chat
        response = conversation.invoke({
            "chat_history": st.session_state.chat_history,
            "human_input": user_input
        })
        response_content = response if isinstance(response, str) else response.content

        st.session_state.chat_history.append({"role": "user", "content": user_input})
        st.session_state.chat_history.append({"role": "assistant", "content": response_content})

    for message in st.session_state.chat_history:
        if message["role"] == "user":
            with st.chat_message("user"):
                st.markdown(message["content"])
        elif message["role"] == "assistant":
            with st.chat_message("assistant"):
                st.markdown(message["content"])

if __name__ == "__main__":
    main()
