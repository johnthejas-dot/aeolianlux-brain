# --- 2. ULTRA-LUXURY VISUAL STYLE (CSS) ---
st.markdown("""
<style>
    /* 1. MAIN BACKGROUND - Deep Luxury Black */
    .stApp {
        background-color: #0E1117;
        color: #FAFAFA;
    }
    
    /* 2. AGGRESSIVE FOOTER REMOVAL */
    /* Hides the hamburger menu, footer, and the 'Built with Streamlit' red balloon */
    header {visibility: hidden !important;}
    footer {visibility: hidden !important;}
    .stDeployButton {display:none !important;}
    [data-testid="stDecoration"] {display:none !important;}
    [data-testid="stStatusWidget"] {display:none !important;} /* Hides the bottom viewer badge */
    
    /* 3. INPUT FIELDS (Visible Text) */
    .stTextInput input {
        color: #000000 !important; /* Force Black Text */
        background-color: #FFFFFF !important; /* White Box */
        border: 1px solid #D4AF37 !important; /* Gold Border */
    }
    .stTextInput label {
        color: #D4AF37 !important; /* Gold Label */
    }
    
    /* 4. THE GOLD BUTTON (Fixing the Invisible Text) */
    /* This targets the button and the text INSIDE the button */
    div.stButton > button {
        background-color: #D4AF37 !important; /* Gold Background */
        border: none !important;
        transition: all 0.3s ease;
    }
    
    /* Force the TEXT inside the button to be BLACK */
    div.stButton > button p {
        color: #000000 !important; 
        font-weight: bold !important;
        font-size: 18px !important;
    }
    
    /* HOVER STATE */
    div.stButton > button:hover {
        background-color: #FFFFFF !important; /* White Background */
        border: 1px solid #D4AF37 !important;
    }
    div.stButton > button:hover p {
        color: #D4AF37 !important; /* Gold Text on Hover */
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
