
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
            तुमचा विचार · तुमचा आवाज
        </div>
    </div>
