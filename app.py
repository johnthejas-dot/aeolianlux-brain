import streamlit as st
from openai import OpenAI
from pinecone import Pinecone
import datetime

# 1. Page Configuration (Mobile Optimized)
st.set_page_config(
    page_title="Aeolianlux Luxury Concierge",
    page_icon="⚜️",
    layout="centered",
    initial_sidebar_state="collapsed"  # Hides sidebar on mobile by default
)

# 2. Custom CSS for Luxury Look & Mobile Hide
st.markdown("""
<style>
    /* Elegant Dark Theme Background */
    .stApp {
        background-color: #0E1117;
        color: #FAFAFA;
    }
    
    /* Hide the top Streamlit bar/menu for cleaner look */
    header {visibility: hidden;}
    #MainMenu {visibility: hidden;}
    
    /* Chat Message Styling */
    .stChatMessage {
        background-color: #1E1E1E;
        border: 1px solid #333;
        border-radius: 10px;
    }

    /* Input Box Styling */
    .stTextInput input {
        color: #FAFAFA !important;
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

# 4. Session State for Lead Capture & Chat History
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "user_info" not in st.session_state:
    st.session_state.user_info = None

# --- LEAD CAPTURE FORM ---
if st.session_state.user_info is None:
    st.markdown("## ⚜️ Welcome to Aeolianlux")
    st.markdown("To provide you with the best personalized luxury experience, please introduce yourself.")
    
    with st.form("lead_capture_form"):
        name = st.text_input("Name")
        phone = st.text_input("WhatsApp / Mobile Number")
        submitted = st.form_submit_button("Start Concierge")
        
        if submitted and name and phone:
            # SAVE LEAD (Simple Log to Console/Streamlit Logs)
            print(f"NEW LEAD: {name} - {phone} - {datetime.datetime.now()}")
            st.session_state.user_info = {"name": name, "phone": phone}
            st.rerun()  # Refresh to show chat
            
    st.stop() # Stop here until form is filled

# --- CHAT INTERFACE ---
st.title("⚜️ Aeolianlux Concierge")
st.caption(f"Welcome, {st.session_state.user_info['name']}. Ask me about Dubai luxury, visas, or history.")

# Display Chat History
for message in st.session_state.chat_history:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat Input
user_input = st.chat_input("How can I assist you today?")

if user_input:
    # 1. Show User Message
    with st.chat_message("user"):
        st.markdown(user_input)
    st.session_state.chat_history.append({"role": "user", "content": user_input})

    # 2. Retrieve Knowledge from Pinecone
    try:
        xq = client.embeddings.create(input=user_input, model="text-embedding-3-small").data[0].embedding
        res = index.query(vector=xq, top_k=3, include_metadata=True)
        knowledge = "\n".join([match['metadata']['text'] for match in res['matches']])
    except:
        knowledge = "No specific database info found."

    # 3. Generate AI Response
    system_prompt = f"""
    You are Aeolianlux, an elite luxury concierge for Dubai.
    User Name: {st.session_state.user_info['name']}
    
    Use this knowledge base to answer:
    {knowledge}
    
    Guidelines:
    - Be polite, sophisticated, and helpful.
    - If you recommend a place, mention why it is luxurious.
    - If the user asks for a Visa or Emergency number, provide the exact details from the knowledge base.
    - Keep answers concise (under 4 sentences) unless asked for a list.
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
