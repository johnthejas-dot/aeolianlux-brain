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
    .stTextInput input, .stSelectbox div[data-baseweb="select"] > div {
        color: #000000 !important; 
        background-color: #FFFFFF !important; 
        border: 1px solid #D4AF37 !important; 
    }
    .stTextInput label, .stSelectbox label { color: #D4AF37 !important; }
    
    /* Gold Buttons */
    [data-testid="stFormSubmitButton"] > button {
        background-color: #D4AF37 !important;
        border: none !important;
    }
    [data-testid="stFormSubmitButton"] > button p {
        color: #000000 !important; 
        font-weight: 900 !important;
    }
    
    /* Chat Messages - Force Text Color */
    .stChatMessage[data-testid="stChatMessage"]:nth-child(odd) {
        background-color: #1E1E1E !important;
    }
    .stChatMessage[data-testid="stChatMessage"]:nth-child(even) {
        background-color: #161920 !important;
        border: 1px solid #D4AF37 !important;
    }
    [data-testid="stChatMessage"] p {
        color: #E0E0E0 !important;
    }
</style>
""", unsafe_allow_html=True)

# --- 3. LOGIC & CONNECTIONS (CACHED TO FIX GLITCHES) ---
# We wrap this in @st.cache_resource so it runs once and stays connected
# This prevents the "Enter" button from resetting the app on click.

@st.cache_resource
def init_connections():
    try:
        from openai import OpenAI
        from pinecone import Pinecone
        
        # Connect to OpenAI
        if "OPENAI_API_KEY" in st.secrets:
            client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
        else:
            client = None
        
        # Connect to Pinecone (Database)
        if "PINECONE_API_KEY" in st.secrets:
            pc = Pinecone(api_key=st.secrets["PINECONE_API_KEY"])
            # Ensure your Index name matches exactly
            index = pc.Index("aeolianlux-index")
        else:
            index = None
            
        return client, index
    except Exception as e:
        return None, None

# Initialize connections
client, index = init_connections()

# Initialize Session State (Memory)
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "user_info" not in st.session_state:
    st.session_state.user_info = None

# --- 4. APP INTERFACE ---

# --- Common Country Codes List ---
country_codes = [
    "+971 (UAE)", "+1 (USA/Canada)", "+44 (UK)", "+91 (India)", 
    "+966 (Saudi Arabia)", "+974 (Qatar)", "+973 (Bahrain)", 
    "+965 (Kuwait)", "+968 (Oman)", "+33 (France)", 
    "+49 (Germany)", "+39 (Italy)", "+86 (China)", 
    "+81 (Japan)", "+7 (Russia)", "+61 (Australia)"
]

# Lead Capture Form
if st.session_state.user_info is None:
    st.markdown("<h1 style='text-align: center; color: #D4AF37;'>⚜️ Aeolian Lux ⚜️</h1>", unsafe_allow_html=True)
    st.write("May we request the pleasure of your introduction to serve you better?")
    
    with st.form("lead_capture_form"):
        name = st.text_input("Full Name")
        
        # Layout with Dropdown
        col1, col2 = st.columns([1.5, 3]) 
        with col1:
            country_code_selection = st.selectbox("Code", options=country_codes, index=0)
        with col2:
            mobile_number = st.text_input("Mobile Number", placeholder="50 123 4567")
            
        if st.form_submit_button("ENTER CONCIERGE"):
            if name and mobile_number:
                # Clean the code to just get "+971" etc.
                clean_code = country_code_selection.split(" ")[0]
                st.session_state.user_info = {"name": name, "phone": f"{clean_code} {mobile_number}"}
                st.rerun()
    st.stop()

# Chat Interface
st.markdown(f"<h3 style='color: #D4AF37;'>⚜️ Welcome, {st.session_state.user_info['name']}</h3>", unsafe_allow_html=True)

for message in st.session_state.chat_history:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Ask me about Dubai Luxury..."):
    # 1. Show User Message
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.chat_history.append({"role": "user", "content": prompt})

    # 2. THE REAL AI LOGIC
    if client:
        # Retrieve Knowledge from Pinecone
        knowledge = ""
        if index:
            try:
                xq = client.embeddings.create(input=prompt, model="text-embedding-3-small").data[0].embedding
                res = index.query(vector=xq, top_k=3, include_metadata=True)
                knowledge = "\n".join([match['metadata']['text'] for match in res['matches']])
            except Exception as e:
                knowledge = "No specific database info found."

        # Generate Answer
        system_prompt = f"""
        You are Aeolianlux, Dubai's most elite digital concierge.
        User Name: {st.session_state.user_info['name']}
        
        Context from database:
        {knowledge}
        
        Tone Guidelines:
        - Elegant, sophisticated, and warm. Use words like "Exquisite," "Bespoke," "Curated."
        - Be helpful but concise.
        """
        
        with st.chat_message("assistant"):
            try:
                response_stream = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": prompt}
                    ],
                    stream=True
                )
                response = st.write_stream(response_stream)
                st.session_state.chat_history.append({"role": "assistant", "content": response})
            except Exception as e:
                st.error("An error occurred generating the response. Please try again.")
    else:
        # Fallback if Keys are missing
        st.error("Concierge is offline. Please check API keys.")
