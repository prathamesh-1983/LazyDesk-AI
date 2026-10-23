from pathlib import Path
import streamlit as st

from lazydesk.config import APP_NAME, DEFAULT_MODEL, DEFAULT_OLLAMA_URL
from lazydesk.llm import OllamaClient, OllamaError
from lazydesk.organizer import scan_directory, build_plan, apply_plan, category_folders
from lazydesk.text_tools import summarize_text, extract_tasks, suggest_filename
from lazydesk.utils import readable_size

st.set_page_config(page_title=APP_NAME, page_icon="🦥", layout="wide")

st.markdown("""
<style>
  .main .block-container {max-width: 1180px; padding-top: 1.8rem;}
  .hero {padding: 1.35rem 1.5rem; border: 1px solid rgba(128,128,128,.25);
         border-radius: 18px; margin-bottom: 1rem;
         background: linear-gradient(120deg, rgba(99,102,241,.13), rgba(20,184,166,.08));}
  .hero h1 {margin: 0 0 .35rem 0;}
  .muted {opacity: .75;}
  div[data-testid="stMetric"] {border: 1px solid rgba(128,128,128,.22); padding: .7rem; border-radius: 12px;}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="hero">
  <h1>🦥 LazyDesk AI</h1>
  <div class="muted">A local-first productivity agent for the tasks you keep putting off.</div>
</div>
""", unsafe_allow_html=True)

with st.sidebar:
    st.header("⚙️ Local AI settings")
    ollama_url = st.text_input("Ollama URL", value=DEFAULT_OLLAMA_URL, help="Usually http://localhost:11434")
    model = st.text_input("Model name", value=DEFAULT_MODEL, help="Must already be downloaded in Ollama.")
    st.caption("Your prompts are sent to the Ollama server you configure. With local Ollama, they stay on your machine.")
    if st.button("Check connection", use_container_width=True):
        try:
            client = OllamaClient(ollama_url, model)
            models = client.list_models()
            st.session_state["ollama_models"] = models
            if any(m == model or m.split(":")[0] == model.split(":")[0] for m in models):
                st.success(f"Connected. Model {model} is available.")
            else:
                st.warning("Ollama is responding, but this model was not found. Pull it with `ollama pull " + model + "`.")
            if models:
                st.caption("Available: " + ", ".join(models[:12]))
        except OllamaError as e:
            st.error(str(e))
    st.divider()
    st.markdown("**Privacy & safety**")
    st.caption("LazyDesk previews file changes first. It does not delete files. Review generated output before using it.")

client = OllamaClient(ollama_url, model)

tab1, tab2, tab3, tab4 = st.tabs([
    "✨ Text assistant", "✅ Task extractor", "🗂️ File organizer", "📋 Activity & help"
])

with tab1:
    st.subheader("Turn long notes into useful summaries")
    st.write("Paste meeting notes, research, a draft, or any text you want to simplify.")
    text = st.text_area("Your text", height=230, placeholder="Paste notes here…")
    c1, c2 = st.columns([1, 1])
    with c1:
        summary_style = st.selectbox("Summary style", ["Concise bullets", "Executive summary", "Key points and decisions"])
    with c2:
        max_words = st.slider("Approximate length (words)", 50, 300, 120, 25)
    if st.button("Summarize locally", type="primary", key="summarize"):
        if not text.strip():
            st.warning("Enter some text first.")
        else:
            with st.spinner("Asking your local model…"):
                try:
                    result = summarize_text(client, text, summary_style, max_words)
                    st.session_state["last_summary"] = result
                except OllamaError as e:
                    st.error(str(e))
    if st.session_state.get("last_summary"):
        st.markdown("#### Summary")
        st.text_area("Generated summary", value=st.session_state["last_summary"], height=220, key="summary_output")
        st.download_button("Download summary", st.session_state["last_summary"], file_name="lazydesk-summary.txt", mime="text/plain")

with tab2:
    st.subheader("Convert brain-dump notes into actionable tasks")
    notes = st.text_area("Notes or brain dump", height=220, placeholder="Example: Email Priya the report by Friday. Check Q3 numbers. Schedule a 20-minute review…", key="task_notes")
    if st.button("Extract tasks", type="primary"):
        if not notes.strip():
            st.warning("Add some notes first.")
        else:
            with st.spinner("Extracting tasks…"):
                try:
                    result = extract_tasks(client, notes)
                    st.session_state["last_tasks"] = result
                except OllamaError as e:
                    st.error(str(e))
    if st.session_state.get("last_tasks"):
        st.markdown("#### Suggested task list")
        st.text_area("Review and edit the tasks", value=st.session_state["last_tasks"], height=240, key="task_output")
        st.download_button("Download task list", st.session_state["last_tasks"], file_name="lazydesk-tasks.md", mime="text/markdown")

with tab3:
    st.subheader("Organize a folder without risky surprises")
    st.info("This tool scans filenames and file types only. It does not upload or read file contents. It proposes moves into category folders and never deletes files.")
    folder = st.text_input("Folder to scan", placeholder="/Users/you/Downloads or C:\\Users\\you\\Downloads")
    max_files = st.slider("Maximum files to inspect", 10, 1000, 250, 10)
    if st.button("Scan folder", type="primary"):
        if not folder.strip():
            st.warning("Enter a folder path.")
        else:
            try:
                entries = scan_directory(folder.strip(), max_files=max_files)
                st.session_state["scan_entries"] = entries
                st.session_state["scan_folder"] = str(Path(folder.strip()).expanduser().resolve())
                st.session_state.pop("organize_plan", None)
                if not entries:
                    st.info("No files found at this folder's top level.")
            except (OSError, ValueError) as e:
                st.error(f"Could not scan folder: {e}")

    entries = st.session_state.get("scan_entries", [])
    if entries:
        st.metric("Files scanned", len(entries))
        import pandas as pd
        df = pd.DataFrame([{
            "File": e["name"], "Type": e["extension"] or "(no extension)",
            "Size": readable_size(e["size"]), "Suggested category": e["category"],
            "Current location": e["path"]
        } for e in entries])
        st.dataframe(df, use_container_width=True, hide_index=True)
        if st.button("Create organization preview"):
            st.session_state["organize_plan"] = build_plan(entries, st.session_state["scan_folder"])
        plan = st.session_state.get("organize_plan", [])
        if plan:
            st.markdown("#### Proposed changes")
            plan_df = pd.DataFrame([{
                "From": p["source"], "To": p["destination"], "Action": p["status"]
            } for p in plan])
            st.dataframe(plan_df, use_container_width=True, hide_index=True)
            pending = [p for p in plan if p["status"] == "Ready"]
            if not pending:
                st.success("Nothing needs moving.")
            else:
                st.warning(f"{len(pending)} file(s) are ready to move. Existing destinations are skipped.")
                confirm = st.checkbox("I reviewed the preview and approve these file moves.")
                if st.button("Apply approved moves", type="primary", disabled=not confirm):
                    try:
                        outcomes = apply_plan(plan)
                        st.session_state["organize_outcomes"] = outcomes
                        st.success(f"Finished. Moved {sum(o['status'] == 'Moved' for o in outcomes)} file(s); skipped {sum(o['status'] != 'Moved' for o in outcomes)}.")
                        st.session_state.pop("scan_entries", None)
                        st.session_state.pop("organize_plan", None)
                    except OSError as e:
                        st.error(f"File operation stopped: {e}")
            if st.button("Cancel preview"):
                st.session_state.pop("organize_plan", None)
                st.rerun()
    if st.session_state.get("organize_outcomes"):
        with st.expander("Last move results"):
            st.dataframe(st.session_state["organize_outcomes"], use_container_width=True, hide_index=True)

with tab4:
    st.subheader("How LazyDesk works")
    st.markdown("""
**Local AI workflow**
1. Install and start Ollama.
2. Download a compatible open-weight model.
3. Set the model and server URL in the sidebar.
4. Use the text and task tools; inference is sent to your configured Ollama server.

**File organizer safety**
- Scans the selected folder's top-level files only.
- Categorizes using file extensions and filename patterns.
- Shows a preview before any move.
- Does not delete files or overwrite existing destinations.
- Avoid scanning system folders or folders you do not own.

**Troubleshooting**
- If connection fails, start Ollama and verify `http://localhost:11434`.
- Run `ollama pull qwen2.5:3b` (or another model compatible with your hardware).
- Use the exact model name shown by `ollama list`.
- Smaller models run more easily on modest hardware, but output quality varies.
""")
    st.markdown("**Suggested next steps:** add unit tests, record a demo, publish the repository, and write your DEV Community challenge post.")
