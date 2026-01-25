import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
import pandas as pd
from datetime import datetime
import streamlit_oauth as oauth
import os
import json
import base64
import google.generativeai as genai

# --- 1. CONFIGURATION & SETUP ---
st.set_page_config(
    page_title="Aeolian Lux | AI Concierge", 
    page_icon="✨", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# API KEY SETUP
GOOG_API_KEY = "AIzaSyD4-xlOdK1tPRN7JYMii0fzT72idj-R_ZE"
genai.configure(api_key=GOOG_API_KEY)

# Connect to Database (CRM Feature)
if not firebase_admin._apps:
    try:
        cred = credentials.Certificate('firestore_key.json') 
        firebase_admin.initialize_app(cred)
    except Exception as e:
        st.error(f"Failed to connect to Database: {e}")

db = firestore.client()

# --- 2. AUTHENTICATION ---
if 'user_email' not in st.session_state:
    st.session_state.user_email = ''

def login_screen():
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.write("") 
        st.write("") 
        # BRANDING: Matches Aeolianlux.com
        st.markdown("<h1 style='text-align: center; color: #D4AF37;'>Aeolian Lux</h1>", unsafe_allow_html=True)
        st.markdown("<h3 style='text-align: center; color: #FAFAFA;'>AI Concierge</h3>", unsafe_allow_html=True)
        st.write("")
        st.markdown("<p style='text-align: center; color: #E0E0E0;'>Instant answers. Infinite patience. 24/7 Availability.</p>", unsafe_allow_html=True)
        st.write("")
        
        import streamlit_oauth
        from streamlit_oauth import OAuth2Component
        
        try:
            with open('client_secret.json') as f:
                secrets = json.load(f)
                web_config = secrets['web']
                CLIENT_ID = web_config['client_id']
                CLIENT_SECRET = web_config['client_secret']
                AUTHORIZE_URL = web_config['auth_uri']
                TOKEN_URL = web_config['token_uri']
        except Exception as e:
            st.error(f"Config Error: {e}")
            return

        oauth2 = OAuth2Component(CLIENT_ID, CLIENT_SECRET, AUTHORIZE_URL, TOKEN_URL, TOKEN_URL, "")
        result = oauth2.authorize_button("Experience the AI", "http://localhost:8501", "openid email profile")
        
        if result:
            try:
                if 'id_token' in result:
                    id_token = result['id_token']
                elif 'token' in result and 'id_token' in result['token']:
                    id_token = result['token']['id_token']
                else:
                    st.error("Login failed: No token found.")
                    return

                token_parts = id_token.split('.')
                padding = len(token_parts[1]) % 4
                if padding == 1:
                    st.error("Invalid token format")
                else:
                    padding_char = "=" * padding
                    user_data = json.loads(base64.urlsafe_b64decode(token_parts[1] + padding_char))
                    st.session_state.user_email = user_data['email']
                    st.rerun()
            except Exception as e:
                st.error(f"Login error: {e}")

# --- 3. MODULE: CRM / CLIENT VAULT (The "Backend Skill" Showcase) ---
def client_vault():
    st.title("🗄️ Concierge CRM")
    st.markdown("Manage VIP client requests and profiles.")
    
    tab1, tab2 = st.tabs(["📝 New Request", "📊 Client Database"])
    
    with tab1:
        with st.form("lead_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                name = st.text_input("Guest Name")
                company = st.text_input("Affiliation")
                phone = st.text_input("Contact")
            with col2:
                email = st.text_input("Email")
                business_unit = st.selectbox("Request Category", ["Luxury Stay", "Fine Dining", "Yacht Charter", "High-End Shopping"])
                priority = st.select_slider("Status", ["Standard", "VIP", "VVIP"])
            notes = st.text_area("Preferences / Special Requirements")
            
            if st.form_submit_button("💾 Log Request"):
                data = {"name": name, "company": company, "phone": phone, "email": email, 
                        "business_unit": business_unit, "priority": priority, "notes": notes, 
                        "created_at": datetime.now(), "created_by": st.session_state.user_email}
                db.collection('leads').add(data)
                st.toast(f"✅ Request Logged: {name}", icon="💾")

    with tab2:
        if st.button("🔄 Sync Database"):
            docs = db.collection('leads').stream()
            data = [doc.to_dict() for doc in docs]
            if data:
                df = pd.DataFrame(data)
                st.dataframe(df, use_container_width=True)
            else:
                st.info("Database is empty.")

# --- 4. MODULE: AI CONCIERGE (The "Frontend Star") ---
def load_luxury_data():
    """Reads verified luxury data from Excel."""
    combined_data = ""
    # Files representing verified data sources
    files = ["Aeolianlux_Dubai _Jan_2026.xlsx", "Aeolianlux_Dubai _Jan_2026_luxury_services.xlsx"]
    for file in files:
        if os.path.exists(file):
            try:
                df = pd.read_excel(file)
                combined_data += f"\nVERIFIED SOURCE ({file}):\n{df.to_string(index=False)}\n"
            except: pass
    return combined_data

def ai_consultant():
    # LUXURY HEADER
    st.markdown("<h1 style='color: #D4AF37;'>Aeolian Lux AI Concierge</h1>", unsafe_allow_html=True)
    st.markdown("**Your Digital Chief of Staff.** *Specializing in Dubai's finest experiences.*")
    
    # Sidebar
    with st.sidebar:
        st.write("---")
        with st.expander("ℹ️ Intelligence Feed"):
            st.success("Dubai Grid: Live")
            st.success("Verified Listings: Active")
        if st.button("Start New Consultation"):
            st.session_state.messages = []
            st.rerun()

    # Chat UI
    if "messages" not in st.session_state:
        st.session_state.messages = [{
            "role": "assistant", 
            "content": "Welcome. I am the Aeolian Lux AI. I can assist with curating luxury stays, sourcing exclusive products, or planning itineraries in Dubai. How may I serve you today?"
        }]

    for message in st.session_state.messages:
        avatar = "🤵" if message["role"] == "assistant" else "👤"
        with st.chat_message(message["role"], avatar=avatar):
            st.markdown(message["content"])

    # INPUT BOX
    if prompt := st.chat_input("Ask for 5-star hotels, Patek Philippe availability, or fine dining..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user", avatar="👤"):
            st.markdown(prompt)

        with st.chat_message("assistant", avatar="🤵"):
            message_placeholder = st.empty()
            try:
                # Load Verified Data
                luxury_context = load_luxury_data()
                
                # THE "CHIEF OF STAFF" BRAIN
                full_prompt = f"""
                You are the 'Aeolian Lux AI Concierge'.
                
                YOUR MISSION:
                To assist high-net-worth individuals and tourists in Dubai by filtering for ONLY luxury, verified, and high-quality options.
                
                YOUR DATA SOURCE (Use this for specific prices/locations):
                {luxury_context}
                
                USER QUERY: {prompt}
                
                GUIDELINES:
                1. **Tone:** Professional, Concise, Sophisticated. (Think: "Instant answers. Infinite patience.").
                2. **Accuracy:** Prioritize the 'VERIFIED SOURCE' data above. If the user asks for food, stay, cloths, watches, yachts, restaurants, jewellery, luxury living or hotels listed there, quote the specific prices and specs.
                3. **Filtering:** If the user asks for something generic, suggest the specific luxury options from your data (e.g., "For a 5-star stay, I recommend Atlantis The Royal or Burj Al Arab...").
                4. **Role:** You are not just a chatbot; you are a Digital Chief of Staff.
                """
                
                model = genai.GenerativeModel('gemini-2.0-flash')
                response = model.generate_content(full_prompt)
                message_placeholder.markdown(response.text)
                st.session_state.messages.append({"role": "assistant", "content": response.text})
            except Exception as e:
                st.error(f"AI Error: {e}")

# --- 5. MAIN NAVIGATION ---
if not st.session_state.user_email:
    login_screen()
else:
    with st.sidebar:
        st.header("Aeolian Lux")
        st.caption(f"Member: {st.session_state.user_email}")
        st.divider()
        page = st.radio("Select Module", ["AI Concierge 🧠", "CRM Vault 🗄️", "System Status ✅"])
        st.divider()
        if st.button("Log Out"):
            st.session_state.user_email = ''
            st.rerun()
    
    if "AI Concierge" in page:
        ai_consultant()
    elif "CRM Vault" in page:
        client_vault()
    elif "System Status" in page:
        st.title("✅ System Online")
        st.success("Connected to Aeolian Lux Neural Grid.")
