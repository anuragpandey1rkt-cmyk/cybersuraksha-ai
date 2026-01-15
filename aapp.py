import streamlit as st
from supabase import create_client
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
# STYLES
# =============================
st.markdown("""
<style>
.stButton > button {
    background-color: #4B4BFF;
    color: white;
    border-radius: 8px;
    font-weight: bold;
}
</style>
""", unsafe_allow_html=True)

# =============================
# SECRETS
# =============================
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_ANON_KEY"]
GROQ_API_KEY = st.secrets["GROQ_API_KEY"]

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
groq_client = Groq(api_key=GROQ_API_KEY)

# =============================
# AUTH
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
# AI FUNCTIONS
# =============================
def analyze_text(content):
    prompt = f"""
Analyze the following content for scam risk.
Classify as Low / Medium / High risk.
Explain the reasoning and give safety advice.

Content:
{content}
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
    return analyze_text(f"URL: {url}")

def extract_risk_level(text):
    text = text.lower()
    if "high" in text:
        return "HIGH"
    elif "medium" in text:
        return "MEDIUM"
    return "LOW"

def show_risk_badge(level):
    if level == "HIGH":
        st.error("🔴 HIGH RISK — Avoid interacting with this content.")
    elif level == "MEDIUM":
        st.warning("🟠 MEDIUM RISK — Proceed with caution.")
    else:
        st.success("🟢 LOW RISK — No major threats detected.")

# =============================
# UI
# =============================
st.title("🛡️ CyberSuraksha AI")
st.caption("Defending Digital Citizens from Online Scams")

if "user" not in st.session_state:
    login_tab, signup_tab = st.tabs(["Login", "Sign Up"])

    # ---------- LOGIN ----------
    with login_tab:
        email = st.text_input("Email", key="login_email")
        password = st.text_input("Password", type="password", key="login_password")

        if st.button("Login", key="login_btn"):
            try:
                user = login(email, password)
                st.session_state.user = user
                st.success("Logged in successfully")
                st.rerun()
                st.stop()
            except:
                st.error("Invalid credentials")

    # ---------- SIGN UP ----------
    with signup_tab:
        new_email = st.text_input("New Email", key="signup_email")
        new_password = st.text_input("New Password", type="password", key="signup_password")

        if st.button("Create Account", key="signup_btn"):
            try:
                signup(new_email, new_password)
                st.success("Account created. Please login.")
            except:
                st.error("Signup failed. Use a stronger password.")

else:
    st.subheader("🔍 Cyber Threat Analyzer")

    msg_tab, url_tab = st.tabs(["📩 Message Scanner", "🌐 URL Checker"])

    # ---------- MESSAGE SCANNER ----------
    with msg_tab:
        message = st.text_area("Paste suspicious message", height=160)
        if st.button("Analyze Message", key="analyze_msg"):
            if message.strip() == "":
                st.warning("Please enter a message.")
            else:
                result = analyze_text(message)
                show_risk_badge(extract_risk_level(result))
                st.write(result)

    # ---------- URL SCANNER ----------
    with url_tab:
        url = st.text_input("Enter suspicious URL", key="url_input")
        if st.button("Check URL", key="check_url"):
            if url.strip() == "":
                st.warning("Please enter a URL.")
            else:
                result = analyze_url(url)
                show_risk_badge(extract_risk_level(result))
                st.write(result)

    st.divider()

    if st.button("Logout", key="logout"):
        st.session_state.clear()
        st.rerun()

