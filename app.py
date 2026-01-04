import streamlit as st
import datetime
import os

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Aeolianlux | Dubai Luxury",
    page_icon="⚜️",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# --- 2. ULTRA-LUXURY VISUAL STYLE (CSS) ---
st.markdown("""
<style>
    /* 1. Main Background - Deep Dark Navy/Black */
    .stApp {
        background-color: #0E1117;
        color: #FAFAFA;
    }
    
    /* 2. HIDE STREAMLIT BRANDING */
    header {visibility: hidden !important;}
    footer {visibility: hidden !important;}
    .stDeployButton {display:none !important;}
    [data-testid="stDecoration"] {display:none !important;}
    [data-testid="stStatusWidget"] {display:none !important;}
    #MainMenu {visibility: hidden !important;}
    
    /* 3. INPUT FIELDS (Visible Text) */
    .stTextInput input {
        color: #000000 !important; 
        background-color: #FFFFFF !important; 
        border: 1px solid #D4AF37 !important; 
        border-radius: 5px;
    }
    .stTextInput label {
        color: #D4AF37 !important; 
    }
    
    /* --- 4. THE BUTTON FIX (BULLETPROOF) --- */
    
    /* Target specifically the Form Submit Button */
    [data-testid="stFormSubmitButton"] > button {
        background-color: #D4AF37 !important;
        border: none !important;
        transition: all 0.3s ease;
    }

    /* Force ALL text inside the button to be BLACK */
    [data-testid="stFormSubmitButton"] > button p,
    [data-testid="stFormSubmitButton"] > button div,
    [data-testid="stFormSubmitButton"] > button span {
        color: #000000 !important; 
        font-weight: 900 !important;
        font-size: 18px !important;
    }

    /* Hover Effects */
    [data-testid="stFormSubmitButton"] > button:hover {
        background-color: #FFFFFF !important;
        border: 1px solid #D4AF37 !important;
    }
    [data-testid="stFormSubmitButton"] > button:hover p {
        color: #D4AF37 !important;
    }

    /* 5. CHAT MESSAGES */
    .stChatMessage[data-testid="stChatMessage"]:nth-child(odd) {
        background-color: #1E1E1E;
        border: 1px solid #333;
    }
    .stChatMessage[data-testid="stChatMessage"]:nth-child(even) {
        background-color: #161920;
        border: 1px solid #D4AF37;
    }
    .stChatInput textarea {
        color: #000000 !important;
        background-color: #FFFFFF !important;
    }
</style>
""", unsafe_allow_html=True)

# --- 3. INITIALIZE CONNECTIONS ---
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
except Exception as e:
    client = None
    index = None

# --- 4. SESSION STATE ---
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "user_info" not in st.session_state:
    st.session_state.user_info = None

# --- 5. LEAD CAPTURE FORM ---
if st.session_state.user_info is None:
    st.markdown("<h1 style='text-align: center; color: #D4AF37;'>⚜️ Aeolianlux</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; font-style: italic; color: #BBBBBB;'>The Definition of Dubai Luxury.</p>", unsafe_allow_html=True)
    st.markdown("---")
    
    st.write("May we request the pleasure of your introduction to serve you better as you navigate the absolute pinnacle of Dubai luxury?")
    
    with st.form("lead_capture_form"):
        name = st.text_input("Full Name")
        
        col1, col2 = st.columns([1, 3])
        with col1:
            country_code = st.text_input("Code", value="+971")
        with col2:
            mobile_number = st.text_input("Mobile Number")
            
        submitted = st.form_submit_button("ENTER CONCIERGE")
        
        if submitted and name and mobile_number:
            full_phone = f"{country_code} {mobile_number}"
            print(f"NEW LEAD: {name} - {full_phone} - {datetime.datetime.now()}")
            st.session_state.user_info = {"name": name, "phone": full_phone}
            st.rerun()
            
    st.stop()

# --- 6. MAIN CHAT INTERFACE ---
st.markdown(f"<h3 style='color: #D4AF37;'>⚜️ Welcome, {st.session_state.user_info['name']}</h3>", unsafe_allow_html=True)

for message in st.session_state.chat_history:
    role = message["role"]
    with st.chat_message(role):
        st.markdown(message["content"])

user_input = st.chat_input("I am at your service. What do you wish to discover about Dubai Luxury Living?")

if user_input:
    with st.chat_message("user"):
        st.markdown(user_input)
    st.session_state.chat_history.append({"role": "user", "content": user_input})

    knowledge = "AI is ready, but Database is not connected yet."
    if client and index:
        try:
            xq = client.embeddings.create(input=user_input, model="text-embedding-3-small").data[0].embedding
            res = index.query(vector=xq, top_k=3, include_metadata=True)
            knowledge = "\n".join([match['metadata']['text'] for match in res['matches']])
        except Exception as e:
            knowledge = f"Database Error: {e}"

    system_prompt = f"""
    You are Aeolianlux, Dubai's most elite digital concierge.
    User Name: {st.session_state.user_info['name']}
    Context from database: {knowledge}
    Tone Guidelines: Elegant, sophisticated, and warm.
    """

    if client:
        with st.chat_message("assistant"):
            response_stream = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_input}
                ],
                stream=True
            )
            response_text = st.write_stream(response_stream)
        
        st.session_state.chat_history.append({"role": "assistant", "content": response_text})
    else:
        response_text = "Thank you for your inquiry. Our AI concierge is currently offline for maintenance."
        with st.chat_message("assistant"):
            st.markdown(response_text)
        st.session_state.chat_history.append({"role": "assistant", "content": response_text})
