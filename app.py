# app.py  – Streamlit + OpenAI Assistants demo
import streamlit as st
import openai, json, time, os
from pathlib import Path

# 1️⃣  ───────────────────────────────────────────────────────────────
# Secure key handling
openai.api_key = st.secrets["OPENAI_API_KEY"]      # store in .streamlit/secrets.toml
ASSISTANT_ID   = st.secrets["ASSISTANT_ID"]        # created once; keep the id

st.set_page_config(page_title="TalentMatch Demo", page_icon="🧩")
st.title("🔎 TalentMatch – Team‑builder demo")

# 2️⃣  ───────────────────────────────────────────────────────────────
# UI: project brief + batch CV upload
project_brief = st.text_area("Paste the project brief", height=200)
cv_files      = st.file_uploader(
    "Upload consultant CVs (.txt)", type="txt", accept_multiple_files=True
)

if st.button("Generate team options", disabled=not(project_brief and cv_files)):
    # 3️⃣  ───────────────────────────────────────────────────────────
    # Read file contents
    cvs = [f.read().decode("utf‑8", errors="ignore") for f in cv_files]

    user_payload = json.dumps({
        "project_description": project_brief,
        "cvs": cvs
    })

    # 4️⃣  ───────────────────────────────────────────────────────────
    # Create a new thread with the user message
    try:
        thread = openai.beta.threads.create(
            messages=[{"role": "user", "content": user_payload}]
        )
    except Exception as e:
        st.error(f"Thread creation failed: {e}")
        st.stop()

    # 5️⃣  ───────────────────────────────────────────────────────────
    # Start the run (stream=True for token streaming)
    with st.spinner("Talking to TalentMatch‑GPT…"):
        try:
            stream = openai.beta.threads.runs.create(
                thread_id=thread.id,
                assistant_id=ASSISTANT_ID,
                stream=True            # 🔥 real‑time tokens
            )
        except Exception as e:
            st.error(f"Run failed: {e}")
            st.stop()

        # 6️⃣  ───────────────────────────────────────────────────────
        # Consume the stream chunk‑by‑chunk
        response_md = st.empty()        # placeholder container
        collected   = ""                # incremental buffer

        for chunk in stream:
            if "content" in chunk.delta:
                token = chunk.delta.content
                collected += token
                response_md.markdown(collected, unsafe_allow_html=True)

        # 7️⃣  ───────────────────────────────────────────────────────
        st.success("Finished ✔")

        # Optional: show the raw JSON if you want to debug
        with st.expander("Raw response JSON"):
            st.json(stream.done())
