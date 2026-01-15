import streamlit as st
from supabase import create_client, Client
from groq import Groq
import re


# =============================
# CONFIG
# =============================
st.set_page_config(
    page_title="CyberSuraksha AI",
    page_icon="🛡️",
    layout="centered"
)

# =============================
# LOAD SECRETS
# =============================
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_ANON_KEY"]
GROQ_API_KEY = st.secrets["GROQ_API_KEY"]

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
groq_client = Groq(api_key=GROQ_API_KEY)

# =============================
# AUTH FUNCTIONS
# =============================
def login(email, password):
    return supabase.auth.sign_in_with_password(
        {"email": email, "password": password}
    )

def signup(email, password):
    return supabase.auth.sign_up(
        {"email": email, "password": password}
    )

# =============================
# AI ANALYSIS
# =============================
def analyze_text(text):
    prompt = f"""
You are a cybersecurity assistant.
Analyze the following message and classify scam risk as:
Low / Medium / High.

Also explain WHY it may be risky and give safety advice.

Message:
{text}
"""

    response = groq_client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": "You are a cyber safety expert."},
            {"role": "user", "content": prompt}
        ]
    )

    return response.choices[0].message.content
def analyze_url(url):
    prompt = f"""
You are a cybersecurity expert.
Analyze the following URL and assess scam risk as:
Low / Medium / High.

Explain WHY the URL may be risky and give safety advice.

URL:
{url}
"""
    response = groq_client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": "You are a cyber safety expert."},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content


def extract_risk_level(text):
    text = text.lower()
    if "high risk" in text or "high" in text:
        return "HIGH"
    elif "medium risk" in text or "medium" in text:
        return "MEDIUM"
    else:
        return "LOW"


def show_risk_badge(level):
    if level == "HIGH":
        st.markdown("### 🔴 **HIGH RISK**")
        st.error("This content appears dangerous. Avoid interacting.")
    elif level == "MEDIUM":
        st.markdown("### 🟠 **MEDIUM RISK**")
        st.warning("Proceed with caution. Verify before action.")
    else:
        st.markdown("### 🟢 **LOW RISK**")
        st.success("No major threats detected, but stay alert.")

# =============================
# UI
# =============================
st.title("🛡️ CyberSuraksha AI")
st.caption("Defending Digital Citizens from Online Scams")

if "user" not in st.session_state:
    tab1, tab2 = st.tabs(["Login", "Sign Up"])

    with tab1:
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        if st.button("Login"):
            try:
                user = login(email, password)
                st.session_state.user = user
                st.success("Logged in successfully")
                st.rerun()
            except:
                st.error("Invalid credentials")

    with tab2:
        email = st.text_input("New Email")
        password = st.text_input("New Password", type="password")
        if st.button("Create Account"):
            try:
                signup(email, password)
                st.success("Account created successfully. Please login.")
            except Exception as e:
                if "weak password" in str(e).lower():
                    st.error("Password too weak. Use at least 6 characters with numbers & symbols.")
                 else:
                    st.error("Signup failed. Try a stronger password or different email.")

else:
    st.subheader("🔍 Cyber Threat Analyzer")

    tab1, tab2 = st.tabs(["📩 Message Scanner", "🌐 URL Checker"])

    # =============================
    # MESSAGE SCANNER
    # =============================
    with tab1:
        st.markdown("#### Paste suspicious message / email / SMS")
        text = st.text_area("", height=180)

        if st.button("Analyze Message"):
            if text.strip() == "":
                st.warning("Please enter some text.")
            else:
                with st.spinner("Analyzing message..."):
                    result = analyze_text(text)
                    risk = extract_risk_level(result)
                    show_risk_badge(risk)
                    st.markdown("### 📄 Explanation")
                    st.write(result)

    # =============================
    # URL SCANNER
    # =============================
    with tab2:
        st.markdown("#### Enter suspicious website URL")
        url = st.text_input("")

        if st.button("Check URL Safety"):
            if url.strip() == "":
                st.warning("Please enter a URL.")
            else:
                with st.spinner("Analyzing URL..."):
                    result = analyze_url(url)
                    risk = extract_risk_level(result)
                    show_risk_badge(risk)
                    st.markdown("### 📄 Explanation")
                    st.write(result)

    st.divider()

    if st.button("Logout"):
        st.session_state.clear()
        st.rerun()
