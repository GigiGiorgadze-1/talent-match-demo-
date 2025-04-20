# app.py
import streamlit as st, openai, json, os

openai.api_key = os.getenv("OPENAI_API_KEY")
ASSISTANT_ID   = "asst_..."

st.title("Consultant‑Match Demo")

project = st.text_area("Paste project brief")
cv_files = st.file_uploader("Upload consultant CVs (.txt)", type="txt", accept_multiple_files=True)

if st.button("Generate team options") and project and cv_files:
    cvs = [f.read().decode("utf‑8") for f in cv_files]

    msg = {
        "project_description": project,
        "cvs": cvs
    }

    with st.spinner("Talking to TalentMatch‑GPT…"):
        run = openai.beta.assistants.create_thread_and_run(
            assistant_id=ASSISTANT_ID,
            thread={"messages":[{"role":"user","content":json.dumps(msg)}]}
        )

        # simple polling; production → use webhooks
        while run.status not in ("completed","failed"):
            run = openai.beta.assistants.runs.retrieve(run.thread_id, run.id)

    if run.status=="completed":
        answer = openai.beta.assistants.threads.messages.list(run.thread_id).data[0].content[0].text.value
        st.markdown(answer, unsafe_allow_html=True)
    else:
        st.error("Assistant failed: "+run.last_error.message)
