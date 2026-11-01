
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
    font-size: 12px;
    font-weight: 800;
    letter-spacing: 2px;
}

.subject-title {
    color: #f5f7ff;
    font-size: 22px;
    font-weight: 800;
    margin: 12px 0;
}

.muted {
    color: #94a5bd;
    font-size: 12px;
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

.stButton > button:hover,
.stFormSubmitButton > button:hover {
    border: 1px solid #35e0d0;
    color: #08111d;
    filter: brightness(1.1);
}

div[data-testid="stRadio"] label {
    color: #f5f7ff !important;
}

div[data-testid="stRadio"] {
    background: #17243a;
    border: 1px solid #25344c;
    border-radius: 12px;
    padding: 12px;
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

st.markdown("""
<div class="hero">
    <div class="eyebrow">DIGITAL JANMAT NETWORK</div>
    <div class="hero-title">
        PULSE <span style="color:#35e0d0">2047</span>
    </div>
    <div class="hero-title">
        जनमत <span style="color:#35e0d0">LIVE</span>
    </div>
    <div class="hero-subtitle">
        तुमचा विचार · तुमचा आवाज · विकसित भारत २०४७
    </div>
</div>
""", unsafe_allow_html=True)


# --------------------------------------------------
# DATABASE CONNECTION
# --------------------------------------------------

def safe_error_message(error):
    """Hide credentials if an exception contains them."""
    message = str(error)

    try:
        secret = st.secrets.get("SUPABASE_SERVICE_KEY", "")
        url = st.secrets.get("SUPABASE_URL", "")

        if secret:
            message = message.replace(secret, "[SECRET HIDDEN]")

        if url:
            message = message.replace(url, "[PROJECT URL HIDDEN]")

    except Exception:
        pass

    return html.escape(message[:1200])


try:
    supabase_url = st.secrets["SUPABASE_URL"]
    supabase_key = st.secrets["SUPABASE_SERVICE_KEY"]

    if not supabase_url.startswith("https://"):
        raise ValueError("SUPABASE_URL must start with https://")

    supabase = create_client(
        supabase_url,
        supabase_key
    )

except Exception as error:
    st.error("Database connection could not be configured.")

    st.markdown(
        f'<div class="panel">Error details:<br>'
        f'<code>{safe_error_message(error)}</code></div>',
        unsafe_allow_html=True
    )

    st.info(
        "Please check the SUPABASE_URL and "
        "SUPABASE_SERVICE_KEY in Streamlit Secrets."
    )
    st.stop()


# --------------------------------------------------
# PARTICIPANT IDENTIFICATION
# --------------------------------------------------

# A browser receives its own participant ID.
# This is a convenience identifier, not identity verification.

try:
    participant_id = st.query_params.get("pid")

    if not participant_id:
        participant_id = str(uuid.uuid4())
        st.query_params["pid"] = participant_id

except Exception as error:
    st.error("Could not create participant ID.")
    st.code(safe_error_message(error))
    st.stop()


# --------------------------------------------------
# LOAD EXISTING RESPONSE
# --------------------------------------------------

try:
    existing_result = (
        supabase.table("votes")
        .select("participant_id,s1,s2")
        .eq("participant_id", participant_id)
        .limit(1)
        .execute()
    )

    old_vote = (
        existing_result.data[0]
        if existing_result.data
        else {}
    )

except Exception as error:
    st.error("Could not load your voting response.")

    st.markdown(
        f'<div class="panel"><b>Database error:</b><br>'
        f'<code>{safe_error_message(error)}</code></div>',
        unsafe_allow_html=True
    )

    st.info(
        "Check your Supabase URL, secret key, "
        "table name and database connection."
    )
    st.stop()


# --------------------------------------------------
# AUTO REFRESH
# --------------------------------------------------

st_autorefresh(
    interval=5000,
    key="pulse_live_refresh"
)


# --------------------------------------------------
# LOAD LIVE VOTING RESULTS
# --------------------------------------------------

try:
    result = (
        supabase.table("votes")
        .select("participant_id,s1,s2")
        .execute()
    )

    all_votes = result.data or []

except Exception as error:
    st.error("Could not load live voting results.")

    st.markdown(
        f'<div class="panel"><b>Database error:</b><br>'
        f'<code>{safe_error_message(error)}</code></div>',
        unsafe_allow_html=True
    )
    st.stop()


# --------------------------------------------------
# CALCULATE RESULTS
# --------------------------------------------------

total_people = len(all_votes)

s1_yes = sum(
    vote.get("s1") == "समर्थन"
    for vote in all_votes
)

s1_no = sum(
    vote.get("s1") == "विरोध"
    for vote in all_votes
)

s2_yes = sum(
    vote.get("s2") == "समर्थन"
    for vote in all_votes
)

s2_no = sum(
    vote.get("s2") == "विरोध"
    for vote in all_votes
)


def percentage(value, total):
    if total == 0:
        return 0
    return round(value * 100 / total)


# --------------------------------------------------
# LIVE DASHBOARD
# --------------------------------------------------

st.markdown("## 🔴 LIVE VOTING DASHBOARD")

c1, c2, c3 = st.columns(3)

with c1:
    st.markdown(
        '<div class="panel">'
        '<div class="metric-label">TOTAL PARTICIPANTS</div>'
        f'<div class="metric-value">{total_people}</div>'
        '<div class="muted">एकूण सहभागी</div>'
        '</div>',
        unsafe_allow_html=True
    )

with c2:
    st.markdown(
        '<div class="panel">'
        '<div class="metric-label">SUBJECT 01</div>'
        f'<div class="metric-value">{s1_yes + s1_no}</div>'
        '<div class="muted">विषय ०१ प्रतिसाद</div>'
        '</div>',
        unsafe_allow_html=True
    )

with c3:
    st.markdown(
        '<div class="panel">'
        '<div class="metric-label">SUBJECT 02</div>'
        f'<div class="metric-value">{s2_yes + s2_no}</div>'
        '<div class="muted">विषय ०२ प्रतिसाद</div>'
        '</div>',
        unsafe_allow_html=True
    )


# --------------------------------------------------
# RESULT DISPLAY
# --------------------------------------------------

def show_results(title, yes, no):
    total = yes + no

    yes_percent = percentage(yes, total)
    no_percent = percentage(no, total)

    st.markdown(
        f'<div class="panel">'
        f'<div class="subject-tag">LIVE RESULTS</div>'
        f'<div class="subject-title">{title}</div>'
        f'</div>',
        unsafe_allow_html=True
    )

    st.write(f"👍 समर्थन — **{yes} ({yes_percent}%)**")
    st.progress(yes_percent / 100)

    st.write(f"👎 विरोध — **{no} ({no_percent}%)**")
    st.progress(no_percent / 100)


st.markdown("---")

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


# --------------------------------------------------
# VOTING FORM
# --------------------------------------------------

st.markdown("---")
st.markdown("## 🗳️ CAST YOUR VOTE")

st.caption(
    "दोन्ही विषयांसाठी आपला पर्याय निवडा "
    "आणि एकदाच सबमिट करा."
)

with st.form("pulse_voting_form"):

    st.markdown(
        '<div class="subject-tag">SUBJECT 01 / विषय ०१</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="subject-title">'
        'विकसित भारत २०४७ साठीचे माझे योगदान'
        '</div>',
        unsafe_allow_html=True
    )

    old_s1 = old_vote.get("s1")

    s1_index = (
        ["समर्थन", "विरोध"].index(old_s1)
        if old_s1 in ["समर्थन", "विरोध"]
        else None
    )

    s1 = st.radio(
        "विषय १ साठी आपले मत निवडा:",
        ["समर्थन", "विरोध"],
        index=s1_index,
        horizontal=True,
        key="pulse_s1"
    )

    st.markdown("---")

    st.markdown(
        '<div class="subject-tag">SUBJECT 02 / विषय ०२</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="subject-title">'
        'युवाशक्ती राष्ट्रशक्ती'
        '</div>',
        unsafe_allow_html=True
    )

    old_s2 = old_vote.get("s2")

    s2_index = (
        ["समर्थन", "विरोध"].index(old_s2)
        if old_s2 in ["समर्थन", "विरोध"]
        else None
    )

    s2 = st.radio(
        "विषय २ साठी आपले मत निवडा:",
        ["समर्थन", "विरोध"],
        index=s2_index,
        horizontal=True,
        key="pulse_s2"
    )

    submitted = st.form_submit_button(
        "SUBMIT / UPDATE MY RESPONSE →"
    )


# --------------------------------------------------
# SAVE OR UPDATE VOTE
# --------------------------------------------------

if submitted:

    if not s1 or not s2:

        st.warning(
            "कृपया दोन्ही विषयांसाठी पर्याय निवडा."
        )

    else:

        try:
            save_result = (
                supabase.table("votes")
                .upsert(
                    {
                        "participant_id": participant_id,
                        "s1": s1,
                        "s2": s2
                    },
                    on_conflict="participant_id"
                )
                .execute()
            )

            st.success(
                "तुमचा प्रतिसाद यशस्वीरित्या "
                "नोंदवला / अपडेट केला!"
            )

            st.rerun()

        except Exception as error:

            st.error("आपला प्रतिसाद सेव्ह करता आला नाही.")

            st.markdown(
                f'<div class="panel"><b>Database error:</b><br>'
                f'<code>{safe_error_message(error)}</code></div>',
                unsafe_allow_html=True
            )


# --------------------------------------------------
# FOOTER
# --------------------------------------------------

st.markdown("---")

st.markdown(
    """
    <div style="text-align:center; padding:20px;">
        <div style="color:#35e0d0; font-weight:900;">
            PULSE 2047
        </div>
        <div style="color:#94a5bd; font-size:12px;">
            DIGITAL JANMAT NETWORK
        </div>
        <div style="color:#94a5bd; font-size:11px; margin-top:8px;">
            LIVE RESULTS REFRESH EVERY 5 SECONDS
        </div>
    </div>
    """,
    unsafe_allow_html=True
)
