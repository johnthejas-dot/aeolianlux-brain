import streamlit as st
from openai import OpenAI
from pinecone import Pinecone
import datetime

# 1. Page Configuration
st.set_page_config(
    page_title="Aeolianlux Luxury Concierge",
    page_icon="⚜️",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# 2. ULTRA-LUXURY VISUAL STYLE (NUCLEAR EDITION)
st.markdown("""
<style>
    /* 1. Main Background */
    .stApp {
        background-color: #0E1117;
        color: #FAFAFA;
    }
    
    /* 2. NUCLEAR FOOTER REMOVAL */
    header {visibility: hidden;}
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {display:none;}
    
    /* This targets the specific "Built with Streamlit" balloon */
    .viewerBadge_container__1QSob {display: none !important;}
    [data-testid="stDecoration"] {display:none;}
    [data-testid="stFooter"] {display: none !important;}
    
    /* 3. Style the Input Fields */
    .stTextInput input, .stSelectbox div[data-testid="stMarkdownContainer"] {
        color: #FFFFFF !important;
    }
    .stTextInput input {
        background-color: #262730 !important;
        border: 1px solid #555 !important;
    }
    /* Style the Dropdown box */
    div[data-baseweb="select"] > div {
        background-color: #262730 !important;
        color: #FFFFFF !important;
        border: 1px solid #555 !important;
    }
    .stTextInput label, .stSelectbox label {
        color: #D4AF37 !important;
    }

    /* 4. FORCE GOLD BUTTON (The Nuclear Option) */
    /* Target EVERY possible button state */
    button, 
    div.stButton > button, 
    button[data-testid="baseButton-secondary"],
    button[kind="secondary"] {
        background-color: #D4AF37 !important;
        color: #000000 !important;
        border: none !important;
        font-weight: bold !important;
        font-size: 16px !important;
        padding: 0.5rem 1rem !important;
        width: 100% !important;
        opacity: 1 !important;
    }
    
    /* Hover State */
    button:hover, 
    div.stButton > button:hover,
    button[data-testid="baseButton-secondary"]:hover {
        background-color: #F8F8FF !important; /* White */
        color: #D4AF37 !important; /* Gold Text */
        box-shadow: 0 4px 12px rgba(212, 175, 55, 0.5) !important;
    }
    
    /* Remove outline on focus */
    button:focus {
        outline: none !important;
        box-shadow: none !important;
    }

    /* 5. Chat Message Styling */
    .stChatMessage[data-testid="stChatMessage"]:nth-child(odd) {
        background-color: #1E1E1E;
        border: 1px solid #333;
    }
    .stChatMessage[data-testid="stChatMessage"]:nth-child(even) {
        background-color: #161920;
        border: 1px solid #D4AF37;
    }
</style>
""", unsafe_allow_html=True)

# 3. Initialize Connections
try:
    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
    pc = Pinecone(api_key=st.secrets["PINECONE_API_KEY"])
    index = pc.Index("aeolianlux-index")
except Exception as e:
    st.error(f"Connection Error: {e}")
    st.stop()

# 4. Session State
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "user_info" not in st.session_state:
    st.session_state.user_info = None

# --- LEAD CAPTURE FORM ---
if st.session_state.user_info is None:
    st.markdown("<h1 style='text-align: center; color: #D4AF37;'>⚜️ Aeolianlux</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; font-style: italic; color: #BBBBBB;'>The Definition of Dubai Luxury.</p>", unsafe_allow_html=True)
    st.markdown("---")
    
    st.write("May we request the pleasure of your introduction to serve you better as you navigate the absolute pinnacle of Dubai luxury?")
    
    with st.form("lead_capture_form"):
        name = st.text_input("Full Name")
        
        country_codes = [
            "+971 (UAE)", "+1 (USA/CAN)", "+44 (UK)", "+91 (IND)", 
            "+966 (KSA)", "+965 (KWT)", "+974 (QAT)", "+973 (BHR)", "+968 (OMN)",
            "+7 (RUS)", "+86 (CHN)", "+33 (FRA)", "+49 (GER)", "+39 (ITA)", 
            "+41 (CHE)", "+61 (AUS)", "+65 (SGP)"
        ]
        
        col1, col2 = st.columns([1.5, 3])
        with col1:
            country_code = st.selectbox("Code", options=country_codes, index=0)
        with col2:
            mobile_number = st.text_input("Mobile Number")
            
        submitted = st.form_submit_button("ENTER CONCIERGE")
        
        if submitted and name and mobile_number:
            clean_code = country_code.split(" ")[0] 
            full_phone = f"{clean_code} {mobile_number}"
            
            print(f"NEW LEAD: {name} - {full_phone} - {datetime.datetime.now()}")
            st.session_state.user_info = {"name": name, "phone": full_phone}
            st.rerun()
            
    st.stop()

# --- CHAT INTERFACE ---
st.markdown(f"<h3 style='color: #D4AF37;'>⚜️ Welcome, {st.session_state.user_info['name']}</h3>", unsafe_allow_html=True)

# Display Chat History
for message in st.session_state.chat_history:
    role = message["role"]
    with st.chat_message(role):
        st.markdown(message["content"])

# Chat Input
user_input = st.chat_input("I am at your service. What do you wish to discover about Dubai Luxury Living?")

if user_input:
    with st.chat_message("user"):
        st.markdown(user_input)
    st.session_state.chat_history.append({"role": "user", "content": user_input})

    # Retrieve Knowledge
    try:
        xq = client.embeddings.create(input=user_input, model="text-embedding-3-small").data[0].embedding
        res = index.query(vector=xq, top_k=3, include_metadata=True)
        knowledge = "\n".join([match['metadata']['text'] for match in res['matches']])
    except:
        knowledge = "No specific database info found."

    # Generate AI Response
    system_prompt = f"""
    You are Aeolianlux, Dubai's most elite digital concierge.
    User Name: {st.session_state.user_info['name']}
    
    Context from database:
    {knowledge}
    
    Tone Guidelines:
    - Elegant, sophisticated, and warm. Use words like "Exquisite," "Bespoke," "Curated."
    - Be helpful but concise.
    - Always answer the user's question directly using the database info.
    """

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
