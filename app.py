import streamlit as st
import datetime
import os

# --- 1. CONFIGURATION ---
st.set_page_config(
    page_title="Aeolianlux | Dubai Luxury",
    page_icon="⚜️",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# --- 2. STYLE (Dark Mode & Hidden Footer) ---
st.markdown("""
<style>
    .stApp { background-color: #0E1117; color: #FAFAFA; }
    
    /* Hide Streamlit Elements */
    header {visibility: hidden !important;}
    footer {visibility: hidden !important;}
    .stDeployButton {display:none !important;}
    
    /* Input Fields */
    .stTextInput input {
        color: #000000 !important; 
        background-color: #FFFFFF !important; 
        border: 1px solid #D4AF37 !important; 
    }
    .stTextInput label { color: #D4AF37 !important; }
    
    /* Gold Buttons */
    [data-testid="stFormSubmitButton"] > button {
        background-color: #D4AF37 !important;
        border: none !important;
    }
    [data-testid="stFormSubmitButton"] > button p {
        color: #000000 !important; 
        font-weight: 900 !important;
    }
</style>
""", unsafe_allow_html=True)

# --- 3. LOGIC & CONNECTIONS ---
try:
    from openai import OpenAI
    from pinecone import Pinecone
    if "OPENAI_API_KEY" in st.secrets:
        client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
    else:
        client = None
    
    if "PINECONE_API_KEY" in st.secrets:
        pc = Pinecone(api_key=st.secrets["PINECONE_API_KEY"])
        index = pc.Index("aeolianlux-index")
    else:
        index = None
except Exception:
    client = None
    index = None

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "user_info" not in st.session_state:
    st.session_state.user_info = None

# --- 4. APP INTERFACE ---
# Lead Capture Form
if st.session_state.user_info is None:
    st.markdown("<h1 style='text-align: center; color: #D4AF37;'>⚜️ Aeolianlux</h1>", unsafe_allow_html=True)
    st.write("May we request the pleasure of your introduction to serve you better?")
    
    with st.form("lead_capture_form"):
        name = st.text_input("Full Name")
        col1, col2 = st.columns([1, 3])
        with col1:
            country_code = st.text_input("Code", value="+971")
        with col2:
            mobile_number = st.text_input("Mobile Number")
            
        if st.form_submit_button("ENTER CONCIERGE"):
            if name and mobile_number:
                st.session_state.user_info = {"name": name, "phone": f"{country_code} {mobile_number}"}
                st.rerun()
    st.stop()

# Chat Interface
st.markdown(f"<h3 style='color: #D4AF37;'>⚜️ Welcome, {st.session_state.user_info['name']}</h3>", unsafe_allow_html=True)

for message in st.session_state.chat_history:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Ask me about Dubai Luxury..."):
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.chat_history.append({"role": "user", "content": prompt})

    # AI Response Logic
    if client:
        # (Simple response logic for now to prevent errors)
        response = "Thank you for your inquiry. I am checking our luxury database..." 
        with st.chat_message("assistant"):
            st.markdown(response)
        st.session_state.chat_history.append({"role": "assistant", "content": response})
    else:
        st.error("AI Brain is offline (Check API Keys).")
