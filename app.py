
import streamlit as st
from supabase import create_client
from streamlit_autorefresh import st_autorefresh
import uuid

# --------------------------------------------------
# PAGE CONFIG
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

.stApp {
    background: radial-gradient(ellipse at 50% -20%, #233a5e 0%, #080d19 65%);
    color: #f5f7ff;
    font-family: 'Noto Sans Devanagari', sans-serif;
}

.block-container {
    max-width: 1050px;
    padding-top: 25px;
    padding-bottom: 40px;
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

.stButton > button,
.stFormSubmitButton > button {
    width: 100%;
    min-height: 48px;
    border: 0;
    border-radius: 12px;
    background: linear-gradient(100deg, #35e0d0, #9c82ff);
    color: #08111d;
    font-weight: 900;
}

div[data-testid="stRadio"] {
    background: #17243a;
    border: 1px solid #25344c;
    border-radius: 12px;
    padding: 12px;
}

div[data-testid="stRadio"] label {
    color: #f5f7ff !important;
}

div[data-testid="stMetric"] {
    background: #111b2d;
    border: 1px solid #25344c;
    border-radius: 15px;
    padding: 15px;
}

hr {
    border-color: #25344c;
}

footer {
    visibility: hidden;
}
</style>
""", unsafe_allow_html=True)

# --------------------------------------------------
# HEADER
# --------------------------------------------------

st.markdown(
    '<div class="hero"><div class="eyebrow">'
    'DIGITAL JANMAT NETWORK</div></div>',
    unsafe_allow_html=True
)

st.markdown(
    "<h1 style='text-align:center;'>PULSE <span style='color:#35e0d0'>2047</span></h1>",
    unsafe_allow_html=True
)

st.markdown(
    "<h1 style='text-align:center;'>जनमत <span style='color:#35e0d0'>LIVE</span></h1>",
    unsafe_allow_html=True
)

st.markdown(
    "<p style='text-align:center;color:#94a5bd;'>"
    "तुमचा विचार · तुमचा आवाज · विकसित भारत २०४७"
    "</p>",
    unsafe_allow_html=True
)

# --------------------------------------------------
# DATABASE CONNECTION
# --------------------------------------------------

def show_error(error):
    message = str(error)

    try:
        key = st.secrets.get("SUPABASE_SERVICE_KEY", "")
        url = st.secrets.get("SUPABASE_URL", "")

        if key:
            message = message.replace(key, "[SECRET HIDDEN]")

        if url:
            message = message.replace(url, "[URL HIDDEN]")
    except Exception:
        pass

    st.code(message[:1000])


try:
    supabase_url = st.secrets["SUPABASE_URL"].strip().rstrip("/")
    supabase_key = st.secrets["SUPABASE_SERVICE_KEY"].strip()

    if not supabase_url.startswith("https://"):
        raise ValueError("Invalid Supabase URL")

    if not supabase_url.endswith(".supabase.co"):
        raise ValueError("Use the base Project URL ending in .supabase.co")

    supabase = create_client(supabase_url, supabase_key)

except Exception as error:
    st.error("Database connection failed.")
    show_error(error)
    st.stop()

# --------------------------------------------------
# PAGE TYPE
# --------------------------------------------------

view = st.query_params.get("view", "vote")

# ==================================================
# ADMIN DASHBOARD
# ==================================================

if view == "admin":

    st.markdown("## 🔴 LIVE VOTING DASHBOARD")
    st.caption("ADMIN VIEW · LIVE RESULTS")

    st_autorefresh(
        interval=5000,
        key="admin_refresh"
    )

    try:
        response = (
            supabase.table("votes")
            .select("participant_id,s1,s2")
            .execute()
        )

        votes = response.data or []

    except Exception as error:
        st.error("Could not load voting results.")
        show_error(error)
        st.stop()

    total = len(votes)

    s1_yes = sum(v.get("s1") == "समर्थन" for v in votes)
    s1_no = sum(v.get("s1") == "विरोध" for v in votes)

    s2_yes = sum(v.get("s2") == "समर्थन" for v in votes)
    s2_no = sum(v.get("s2") == "विरोध" for v in votes)

    st.markdown("---")

    c1, c2, c3 = st.columns(3)

    c1.metric("TOTAL PARTICIPANTS", total)
    c2.metric("SUBJECT 01", s1_yes + s1_no)
    c3.metric("SUBJECT 02", s2_yes + s2_no)

    def show_results(title, yes, no):

        total_votes = yes + no

        yes_pct = round(yes * 100 / total_votes) if total_votes else 0
        no_pct = round(no * 100 / total_votes) if total_votes else 0

        st.markdown("---")
        st.subheader(title)

        st.write(f"👍 समर्थन — {yes} ({yes_pct}%)")
        st.progress(yes_pct / 100)

        st.write(f"👎 विरोध — {no} ({no_pct}%)")
        st.progress(no_pct / 100)

    show_results(
        "विषय ०१ · विकसित भारत २०४७ साठीचे माझे योगदान",
        s1_yes,
        s1_no
    )

    show_results(
        "विषय ०२ · युवाशक्ती राष्ट्रशक्ती",
        s2_yes,
        s2_no
    )

    st.markdown("---")
    st.caption("PULSE 2047 · ADMIN DASHBOARD")

    st.stop()

# ==================================================
# PUBLIC VOTING PAGE
# ==================================================

st.markdown("---")
st.markdown("## 🗳️ CAST YOUR VOTE")

st.caption(
    "दोन्ही विषयांसाठी आपला पर्याय निवडा "
    "आणि एकदाच सबमिट करा."
)

# --------------------------------------------------
# PARTICIPANT ID
# --------------------------------------------------

try:
    participant_id = st.query_params.get("pid")

    if not participant_id:
        participant_id = str(uuid.uuid4())
        st.query_params["pid"] = participant_id

except Exception as error:
    st.error("Could not create participant ID.")
    show_error(error)
    st.stop()

# --------------------------------------------------
# LOAD PREVIOUS VOTE
# --------------------------------------------------

try:
    previous = (
        supabase.table("votes")
        .select("participant_id,s1,s2")
        .eq("participant_id", participant_id)
        .limit(1)
        .execute()
    )

    old_vote = previous.data[0] if previous.data else {}

except Exception as error:
    st.error("Could not load your previous response.")
    show_error(error)
    st.stop()

# --------------------------------------------------
# VOTING FORM
# --------------------------------------------------

with st.form("pulse_voting_form"):

    st.markdown("### SUBJECT 01 / विषय ०१")
    st.subheader("विकसित भारत २०४७ साठीचे माझे योगदान")

    options = ["समर्थन", "विरोध"]

    old_s1 = old_vote.get("s1")
    s1_index = options.index(old_s1) if old_s1 in options else None

    s1 = st.radio(
        "विषय १ साठी आपले मत निवडा:",
        options,
        index=s1_index,
        horizontal=True,
        key="pulse_s1"
    )

    st.markdown("---")

    st.markdown("### SUBJECT 02 / विषय ०२")
    st.subheader("युवाशक्ती राष्ट्रशक्ती")

    old_s2 = old_vote.get("s2")
    s2_index = options.index(old_s2) if old_s2 in options else None

    s2 = st.radio(
        "विषय २ साठी आपले मत निवडा:",
        options,
        index=s2_index,
        horizontal=True,
        key="pulse_s2"
    )

    submitted = st.form_submit_button(
        "SUBMIT / UPDATE MY RESPONSE →"
    )

# --------------------------------------------------
# SAVE RESPONSE
# --------------------------------------------------

if submitted:

    try:
        supabase.table("votes").upsert(
            {
                "participant_id": participant_id,
                "s1": s1,
                "s2": s2
            },
            on_conflict="participant_id"
        ).execute()

        st.success(
            "तुमचा प्रतिसाद यशस्वीरित्या नोंदवला / अपडेट केला!"
        )

    except Exception as error:
        st.error("आपला प्रतिसाद सेव्ह करता आला नाही.")
        show_error(error)

# --------------------------------------------------
# FOOTER
# --------------------------------------------------

st.markdown("---")

st.markdown(
    "<p style='text-align:center;color:#35e0d0;font-weight:900;'>PULSE 2047</p>",
    unsafe_allow_html=True
)

st.markdown(
    "<p style='text-align:center;color:#94a5bd;font-size:12px;'>DIGITAL JANMAT NETWORK</p>",
    unsafe_allow_html=True
)
