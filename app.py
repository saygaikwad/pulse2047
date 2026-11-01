
import streamlit as st
import streamlit.components.v1 as components
from supabase import create_client
from streamlit_autorefresh import st_autorefresh
import uuid

st.set_page_config(
    page_title="PULSE 2047 | जनमत LIVE",
    page_icon="🗳️",
    layout="centered"
)

st.markdown("""
<style>
.stApp {
    background: radial-gradient(ellipse at 50% -20%, #233a5e 0%, #080d19 65%);
    color: #f5f7ff;
}
.block-container {max-width: 1050px; padding-top: 2rem;}
h1, h2, h3, p, label {color: #f5f7ff;}
.hero {text-align:center; padding:20px 0 28px;}
.eyebrow {color:#35e0d0; letter-spacing:3px; font-size:12px;}
.hero-title {font-size:48px; font-weight:900; margin:8px 0;}
.panel {
    background:#111b2d; border:1px solid #25344c;
    border-radius:17px; padding:20px; margin:12px 0;
}
.metric {color:#35e0d0; font-size:34px; font-weight:800;}
.muted {color:#94a5bd; font-size:13px;}
.stButton>button, .stFormSubmitButton>button {
    width:100%; border-radius:12px; min-height:48px;
    background:linear-gradient(100deg,#35e0d0,#9c82ff);
    color:#08111d; font-weight:900; border:0;
}
div[data-testid="stRadio"] label {color:#f5f7ff;}
hr {border-color:#25344c;}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="hero">
 <div class="eyebrow">DIGITAL JANMAT NETWORK</div>
 <div class="hero-title">PULSE <span style="color:#35e0d0">2047</span></div>
 <div class="hero-title">जनमत <span style="color:#35e0d0">LIVE</span></div>
 <p style="color:#94a5bd">तुमचा विचार · तुमचा आवाज · विकसित भारत २०४७</p>
</div>
""", unsafe_allow_html=True)

# Give each browser a participant ID that remains in its URL.
if "pid" not in st.query_params:
    st.query_params["pid"] = str(uuid.uuid4())

participant_id = st.query_params["pid"]

# Connect to the shared database.
try:
    supabase = create_client(
        st.secrets["SUPABASE_URL"],
        st.secrets["SUPABASE_SERVICE_KEY"]
    )
    connected = True
except Exception:
    connected = False

if not connected:
    st.error("Database connection is not configured yet. Please complete the setup steps.")
    st.stop()

# Load this participant's existing response.
try:
    existing = (
        supabase.table("votes")
        .select("*")
        .eq("participant_id", participant_id)
        .execute()
    )
    old_vote = existing.data[0] if existing.data else {}
except Exception:
    st.error("Could not load votes. Please check the database setup.")
    st.stop()

# Automatically refresh the public results every 5 seconds.
st_autorefresh(interval=5000, key="results_refresh")

# Read all submitted votes for aggregate results.
try:
    all_votes = supabase.table("votes").select("s1,s2").execute().data or []
except Exception:
    st.error("Unable to load live results.")
    st.stop()

total_people = len(all_votes)
s1_yes = sum(v["s1"] == "समर्थन" for v in all_votes)
s1_no = sum(v["s1"] == "विरोध" for v in all_votes)
s2_yes = sum(v["s2"] == "समर्थन" for v in all_votes)
s2_no = sum(v["s2"] == "विरोध" for v in all_votes)

def percentage(value, total):
    return round(value * 100 / total) if total else 0

def show_results(title, yes, no):
    total = yes + no
    yp = percentage(yes, total)
    np = percentage(no, total)
    st.markdown(f'<div class="panel"><h3>{title}</h3>', unsafe_allow_html=True)
    st.write(f"👍 समर्थन — **{yes} ({yp}%)**")
    st.progress(yp / 100)
    st.write(f"👎 विरोध — **{no} ({np}%)**")
    st.progress(np / 100)
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("### LIVE DASHBOARD")
c1, c2, c3 = st.columns(3)
c1.metric("TOTAL PARTICIPANTS", total_people)
c2.metric("SUBJECT 01", len([v for v in all_votes if v.get("s1")]))
c3.metric("SUBJECT 02", len([v for v in all_votes if v.get("s2")]))

st.markdown("---")
st.markdown("### 🗳️ CAST YOUR VOTE")
st.caption("दोन्ही विषयांसाठी आपला पर्याय निवडा आणि एकदाच सबमिट करा.")

with st.form("voting_form"):
    st.markdown("#### विषय ०१")
    st.markdown("### विकसित भारत २०४७ साठीचे माझे योगदान")
    s1 = st.radio(
        "विषय १ साठी आपले मत:",
        ["समर्थन", "विरोध"],
        index=["समर्थन", "विरोध"].index(old_vote["s1"])
        if old_vote.get("s1") in ["समर्थन", "विरोध"] else None,
        horizontal=True,
        key="vote_s1"
    )

    st.markdown("---")
    st.markdown("#### विषय ०२")
    st.markdown("### युवाशक्ती राष्ट्रशक्ती")
    s2 = st.radio(
        "विषय २ साठी आपले मत:",
        ["समर्थन", "विरोध"],
        index=["समर्थन", "विरोध"].index(old_vote["s2"])
        if old_vote.get("s2") in ["समर्थन", "विरोध"] else None,
        horizontal=True,
        key="vote_s2"
    )

    submitted = st.form_submit_button("SUBMIT / UPDATE MY RESPONSE →")

if submitted:
    if not s1 or not s2:
        st.warning("कृपया दोन्ही विषयांसाठी पर्याय निवडा.")
    else:
        try:
            supabase.table("votes").upsert({
                "participant_id": participant_id,
                "s1": s1,
                "s2": s2
            }, on_conflict="participant_id").execute()

            st.success("तुमचा प्रतिसाद यशस्वीरित्या नोंदवला / अपडेट केला!")
            st.rerun()
        except Exception:
            st.error("मत नोंदवता आले नाही. कृपया पुन्हा प्रयत्न करा.")

st.markdown("---")
st.markdown("### 📊 LIVE VOTING RESULTS")
show_results("विषय ०१ · विकसित भारत २०४७", s1_yes, s1_no)
show_results("विषय ०२ · युवाशक्ती राष्ट्रशक्ती", s2_yes, s2_no)

st.caption("Results refresh automatically every 5 seconds.")
st.caption("PULSE 2047 · DIGITAL JANMAT NETWORK")
