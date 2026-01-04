# --- [PASTE THIS AT THE VERY END OF YOUR APP.PY FILE] ---

# --- CUSTOM FOOTER INJECTION ---
footer_html = """
<style>
    /* 1. Make space at bottom of app so footer doesn't cover content */
    .block-container {
        padding-bottom: 70px !important;
    }

    /* 2. Style the Custom Footer */
    .custom-footer {
        position: fixed;
        left: 0;
        bottom: 0;
        width: 100%;
        background-color: #0E1117; /* Match Main Background Color */
        color: #D4AF37; /* Gold Text */
        text-align: center;
        padding: 15px 0;
        font-size: 14px;
        border-top: 1px solid #333; /* Subtle top border line */
        z-index: 9999; /* Ensure it sits on top of everything */
    }
    
    /* Optional: Make the text slightly lighter if Gold is too intense */
    .custom-footer p {
        margin: 0;
        color: #B0B0B0; /* Light Grey text */
    }
    .custom-footer span {
        color: #D4AF37; /* Highlight 'Aeolianlux' in Gold */
        font-weight: bold;
    }
</style>

<div class="custom-footer">
    <p>© 2024 <span>Aeolianlux</span> | The Definition of Dubai Luxury. All rights reserved.</p>
</div>
"""
# Inject the HTML/CSS
st.markdown(footer_html, unsafe_allow_html=True)
