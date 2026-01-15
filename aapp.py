import streamlit as st
from supabase import create_client, Client
from groq import Groq

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
            signup(email, password)
            st.success("Account created. Please login.")

else:
    st.subheader("🔍 Scam & Phishing Analyzer")

    text = st.text_area(
        "Paste suspicious message / email / SMS here",
        height=200
    )

    if st.button("Analyze Risk"):
        if text.strip() == "":
            st.warning("Please enter some text")
        else:
            with st.spinner("Analyzing..."):
                result = analyze_text(text)
                st.success("Analysis Complete")
                st.write(result)

    if st.button("Logout"):
        st.session_state.clear()
        st.rerun()
