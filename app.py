
import streamlit as st
from supabase import create_client
from streamlit_autorefresh import st_autorefresh
import uuid
import html

# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="PULSE 2047 | जनमत LIVE",
    page_icon="🗳️",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# --------------------------------------------------
# DESIGN
# --------------------------------------------------

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+Devanagari:wght@400;500;600;700;800;900&display=swap');

* {
    font-family: 'Noto Sans Devanagari', sans-serif;
}

.stApp {
    background: radial-gradient(
        ellipse at 50% -20%,
        #233a5e 0%,
        #080d19 65%
    );
    color: #f5f7ff;
}

.block-container {
    max-width: 1050px;
    padding-top: 25px;
    padding-bottom: 40px;
}

header[data-testid="stHeader"] {
    background: transparent;
}

.hero {
    text-align: center;
    padding: 25px 0 30px;
}

.eyebrow {
    color: #35e0d0;
    letter-spacing: 3px;
    font-size: 12px;
    font-weight: 800;
}

.hero-title {
    font-size: clamp(34px, 6vw, 52px);
    font-weight: 900;
    margin: 8px 0;
    color: #f5f7ff;
}

.hero-subtitle {
    color: #94a5bd;
    font-size: 15px;
}

.panel {
    background: #111b2d;
    border: 1px solid #25344c;
    border-radius: 17px;
    padding: 20px;
    margin: 14px 0;
}

.metric-label {
    color: #94a5bd;
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 1px;
}

.metric-value {
    color: #35e0d0;
    font-size: 32px;
    font-weight: 900;
}

.subject-tag {
    color: #35e0d0;
