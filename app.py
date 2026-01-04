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
    
    /* 2. HIDE STREAMLIT BRANDING (Footer & Menu) */
    header {visibility: hidden !important;}
    footer {visibility: hidden !important;}
    .stDeployButton {display:none !important;}
    [data-testid="stDecoration"] {display:none !important;}
    [data-testid="stStatusWidget"] {display:none !important;}
    #MainMenu {visibility: hidden !important;}
    
    /* 3. INPUT FIELDS (Visible Text) */
    .stTextInput input {
        color: #000000 !important; /* Force Black Text */
        background-color: #FFFFFF !important; /* White Box */
        border: 1px solid #D4AF37 !important; /* Gold Border */
        border-radius: 5px;
    }
    .stTextInput label {
        color: #D4AF37 !important; /* Gold Label */
    }
    
    /* --- 4. THE BUTTON FIX (THE NUCLEAR OPTION) --- */
    /* Force the button background to Gold */
    div.stButton > button {
        background-color: #D4AF37 !important; 
        border: none !important;
        transition: all 0.3s ease;
    }
    
    /* FORCE ALL TEXT INSIDE THE BUTTON TO BE BLACK */
    div.stButton > button p, 
    div.stButton > button span,
    div.stButton > button div {
        color: #000000 !important; 
        font-weight: 900 !important; /* Extra Bold */
        font-size: 18px !important;
    }
    
    /* HOVER STATE */
    div.stButton > button:hover {
        background-color: #FFFFFF !important; /* White Background */
        border: 1px solid #D4AF37 !important;
    }
    /* FORCE TEXT TO BE GOLD ON HOVER */
    div.stButton > button:hover p,
    div.stButton > button:hover span {
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

# --- 5. LEAD CAPTURE FORM (The Gate) ---
if st.session_state.user_info is None:
    # Centered Logo and Title
    st.markdown("<h1 style='text-align: center; color: #D4AF37;'>⚜️ Aeolianlux</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; font-style: italic; color: #BBBBBB;'>The Definition of Dubai Luxury.</p>", unsafe_allow_html=True)
    st.markdown("---")
    
    st.write("May we request the pleasure of your introduction to serve you better as you navigate the absolute pinnacle of Dubai luxury?")
    
    with st.form("lead_capture_form"):
        name = st.text_input("Full Name")
        
        # Split Phone Number (Country Code + Number)
        col1, col2 = st.columns([1, 3])
        with col1:
            country_code = st.text_input("Code", value="+971")
        with col2:
            mobile_number = st.text_input("Mobile Number")
            
        submitted = st.form_submit_button("ENTER CONCIERGE")
        
        if submitted and name and mobile_number:
            full_phone = f"{country_code} {mobile_number}"
            # Log the lead
            print(f"NEW LEAD: {name} - {full_phone} - {datetime.datetime.now()}")
            
            st.session_state.user_info = {"name": name, "phone": full_phone}
            st.rerun()
            
    st.stop() # Stops the app here if they haven't logged in

# --- 6. MAIN CHAT INTERFACE ---
# Header
st.markdown(f"<h3 style='color: #D4AF37;'>⚜️ Welcome, {st.session_state.user_info['name']}</h3>", unsafe_allow_html=True)

# Display Chat History
for message in st.session_state.chat_history:
    role = message["role"]
    with st.chat_message(role):
        st.markdown(message["content"])

# Chat Input with Premium Greeting
user_input = st.chat_input("I am at your service. What do you wish to discover about Dubai Luxury Living?")

if user_input:
    # 1. Show User Message
    with st.chat_message("user"):
        st.markdown(user_input)
    st.session_state.chat_history.append({"role": "user", "content": user_input})

    # 2. Retrieve Knowledge (Only if connected)
    knowledge = "AI is ready, but Database is not connected yet."
    if client and index:
        try:
            xq = client.embeddings.create(input=user_input, model="text-embedding-3-small").data[0].embedding
            res = index.query(vector=xq, top_k=3, include_metadata=True)
            knowledge = "\n".join([match['metadata']['text'] for match in res['matches']])
        except Exception as e:
            knowledge = f"Database Error: {e}"

    # 3. Generate AI Response
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
        # Fallback if no API key is present
        response_text = "Thank you for your inquiry. Our AI concierge is currently offline for maintenance. Please check back shortly."
        with st.chat_message("assistant"):
            st.markdown(response_text)
        st.session_state.chat_history.append({"role": "assistant", "content": response_text})
