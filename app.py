import streamlit as st

# Page config (optional but clean)
st.set_page_config(
    page_title="Checkin App Suspended",
    layout="centered"
)

# White background (forces clean look on mobile too)
st.markdown("""
    <style>
    body, .stApp {
        background-color: white;
    }
    </style>
""", unsafe_allow_html=True)

# Centered message
st.markdown("""
    <div style="display: flex; height: 80vh; justify-content: center; align-items: center; text-align: center;">
        <div>
            <h2>The Checkin App has been suspended until our meeting on Monday.</h2>
            <p style="font-size:18px;">Get a paper inspection form from dispatch.</p>
        </div>
    </div>
""", unsafe_allow_html=True)