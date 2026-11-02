"""
FileVerse 3D - Streamlit UI for file & folder CRUD (Create, Read, Update, Delete)

Run:
    pip install -r requirements.txt
    streamlit run app.py

All operations happen inside a sandbox folder called "workspace" next to this
script, so nothing outside it can be read, renamed or deleted.
"""

import shutil
from datetime import datetime
from pathlib import Path

import streamlit as st

try:
    import plotly.graph_objects as go

    HAS_PLOTLY = True
except ImportError:  # the 3D explorer tab will show an install hint
    HAS_PLOTLY = False

# --------------------------------------------------------------------------
# Page config
# --------------------------------------------------------------------------
st.set_page_config(
    page_title="FileVerse 3D",
    page_icon="🧊",
    layout="wide",
    initial_sidebar_state="expanded",
)

ROOT = Path("workspace").resolve()
ROOT.mkdir(exist_ok=True)

ROOT_LABEL = "📦 workspace (root)"

# --------------------------------------------------------------------------
# Styling: light pastel palette + 3D effects (perspective, depth, tilt)
# --------------------------------------------------------------------------
CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700;800&display=swap');

:root {
    --indigo: #6366f1;
    --violet: #8b5cf6;
    --pink: #f472b6;
    --sky: #38bdf8;
    --mint: #34d399;
    --amber: #fbbf24;
    --rose: #fb7185;
    --ink: #1e293b;
    --muted: #64748b;
}

html, body, [class*="css"], .stApp {
    font-family: 'Poppins', sans-serif;
    color: var(--ink);
}

/* Soft light gradient background */
.stApp {
    background: linear-gradient(135deg, #eef2ff 0%, #fdf4ff 45%, #ecfeff 100%);
    background-attachment: fixed;
}

header[data-testid="stHeader"] { background: transparent; }
.block-container { padding-top: 2rem; max-width: 1250px; }

h1, h2, h3, h4, label, p, span, div { color: var(--ink); }

/* ---------- Sidebar ---------- */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #ffffff 0%, #f5f3ff 100%);
    border-right: 1px solid #e0e7ff;
    box-shadow: 6px 0 30px rgba(99, 102, 241, 0.10);
}

/* ---------- Hero with rotating 3D cube ---------- */
.hero {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 2rem;
    padding: 2rem 2.5rem;
    margin-bottom: 1.5rem;
    border-radius: 28px;
    background: linear-gradient(120deg, #c7d2fe 0%, #fbcfe8 55%, #bae6fd 100%);
    box-shadow:
        0 2px 0 rgba(255,255,255,0.8) inset,
        0 25px 50px -12px rgba(99, 102, 241, 0.35),
        0 10px 20px rgba(244, 114, 182, 0.18);
    perspective: 1200px;
    overflow: hidden;
}
.hero h1 {
    font-size: 2.6rem;
    font-weight: 800;
    margin: 0;
    background: linear-gradient(90deg, #4338ca, #be185d);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    text-shadow: 0 6px 18px rgba(99,102,241,0.25);
}
.hero p { margin: .4rem 0 0 0; color: #475569; font-size: 1.02rem; }

.scene { width: 110px; height: 110px; perspective: 600px; flex-shrink: 0; }
.cube {
    width: 100%; height: 100%;
    position: relative;
    transform-style: preserve-3d;
    animation: spin 14s linear infinite;
}
.cube .face {
    position: absolute;
    width: 110px; height: 110px;
    display: flex; align-items: center; justify-content: center;
    font-size: 2.4rem;
    border-radius: 18px;
    border: 2px solid rgba(255,255,255,0.9);
    background: rgba(255,255,255,0.55);
    backdrop-filter: blur(4px);
    box-shadow: 0 0 25px rgba(99,102,241,0.25) inset;
}
.cube .front  { transform: rotateY(  0deg) translateZ(55px); }
.cube .back   { transform: rotateY(180deg) translateZ(55px); }
.cube .right  { transform: rotateY( 90deg) translateZ(55px); }
.cube .left   { transform: rotateY(-90deg) translateZ(55px); }
.cube .top    { transform: rotateX( 90deg) translateZ(55px); }
.cube .bottom { transform: rotateX(-90deg) translateZ(55px); }
@keyframes spin {
    from { transform: rotateX(-20deg) rotateY(0deg); }
    to   { transform: rotateX(-20deg) rotateY(360deg); }
}

/* ---------- 3D tilting metric cards ---------- */
.card-wrap { perspective: 900px; }
.metric-card {
    position: relative;
    padding: 1.4rem 1.4rem 1.2rem 1.4rem;
    border-radius: 22px;
    background: #ffffff;
    border: 1px solid rgba(255,255,255,0.9);
    box-shadow:
        0 1px 0 #fff inset,
        0 18px 30px -12px rgba(99,102,241,0.30),
        0 6px 12px rgba(15,23,42,0.06);
    transform-style: preserve-3d;
    transition: transform .35s cubic-bezier(.2,.8,.2,1), box-shadow .35s ease;
}
.metric-card:hover {
    transform: rotateX(7deg) rotateY(-9deg) translateY(-8px);
    box-shadow:
        0 30px 45px -15px rgba(99,102,241,0.45),
        0 12px 20px rgba(15,23,42,0.08);
}
.metric-card .icon {
    width: 54px; height: 54px; border-radius: 16px;
    display: flex; align-items: center; justify-content: center;
    font-size: 1.7rem;
    transform: translateZ(40px);
    box-shadow: 0 10px 18px -6px rgba(0,0,0,0.20);
}
.metric-card .value {
    font-size: 2rem; font-weight: 700; margin-top: .7rem;
    transform: translateZ(25px);
}
.metric-card .label {
    font-size: .85rem; color: var(--muted); font-weight: 500;
    letter-spacing: .04em; text-transform: uppercase;
}

/* ---------- Section panels ---------- */
.panel {
    background: rgba(255,255,255,0.80);
    backdrop-filter: blur(8px);
    border: 1px solid #ffffff;
    border-radius: 22px;
    padding: 1.4rem 1.6rem;
    box-shadow: 0 20px 40px -18px rgba(99,102,241,0.28), 0 4px 10px rgba(15,23,42,0.04);
    margin-bottom: 1rem;
}
.panel h3 { margin-top: 0; }

/* ---------- 3D buttons ---------- */
.stButton > button, .stDownloadButton > button {
    font-family: 'Poppins', sans-serif;
    font-weight: 600;
    color: #ffffff !important;
    border: none;
    border-radius: 14px;
    padding: .65rem 1.4rem;
    background: linear-gradient(180deg, #818cf8 0%, #6366f1 100%);
    box-shadow:
        0 6px 0 #4f46e5,
        0 14px 22px rgba(99,102,241,0.35);
    transform: translateY(0);
    transition: transform .12s ease, box-shadow .12s ease, filter .2s ease;
}
.stButton > button:hover, .stDownloadButton > button:hover {
    filter: brightness(1.06);
    transform: translateY(-2px);
    box-shadow:
        0 8px 0 #4f46e5,
        0 18px 28px rgba(99,102,241,0.40);
    color: #ffffff !important;
}
.stButton > button:active, .stDownloadButton > button:active {
    transform: translateY(6px);
    box-shadow: 0 0 0 #4f46e5, 0 4px 8px rgba(99,102,241,0.30);
}
.stButton > button p, .stDownloadButton > button p { color: #ffffff !important; }

/* danger buttons: wrap in a container with key starting "danger" */
div[class*="st-key-danger"] .stButton > button {
    background: linear-gradient(180deg, #fda4af 0%, #fb7185 100%);
    box-shadow: 0 6px 0 #e11d48, 0 14px 22px rgba(251,113,133,0.40);
}
div[class*="st-key-danger"] .stButton > button:hover {
    box-shadow: 0 8px 0 #e11d48, 0 18px 28px rgba(251,113,133,0.45);
}
div[class*="st-key-danger"] .stButton > button:active {
    box-shadow: 0 0 0 #e11d48, 0 4px 8px rgba(251,113,133,0.35);
}

/* ---------- Inputs ---------- */
.stTextInput input, .stTextArea textarea,
div[data-baseweb="select"] > div {
    background: #ffffff !important;
    color: var(--ink) !important;
    border-radius: 14px !important;
    border: 1.5px solid #e0e7ff !important;
    box-shadow: inset 0 2px 5px rgba(99,102,241,0.08);
}
.stTextInput input:focus, .stTextArea textarea:focus {
    border-color: var(--indigo) !important;
    box-shadow: 0 0 0 4px rgba(99,102,241,0.15) !important;
}

/* ---------- Tabs ---------- */
.stTabs [data-baseweb="tab-list"] {
    gap: .6rem;
    background: rgba(255,255,255,0.7);
    padding: .5rem;
    border-radius: 18px;
    box-shadow: 0 10px 25px -10px rgba(99,102,241,0.30);
}
.stTabs [data-baseweb="tab"] {
    border-radius: 12px;
    padding: .55rem 1.2rem;
    font-weight: 600;
    color: var(--muted);
    transition: transform .2s ease, background .2s ease;
}
.stTabs [data-baseweb="tab"]:hover { transform: translateY(-2px); background: #eef2ff; }
.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, #c7d2fe, #fbcfe8) !important;
    color: #3730a3 !important;
    box-shadow: 0 6px 14px rgba(99,102,241,0.25);
}
.stTabs [data-baseweb="tab-highlight"], .stTabs [data-baseweb="tab-border"] { display: none; }

/* ---------- Misc ---------- */
div[data-testid="stAlert"] { border-radius: 16px; }
div[data-testid="stFileUploader"] section {
    border-radius: 16px; background: #ffffff; border: 2px dashed #c7d2fe;
}
.stCodeBlock, pre { border-radius: 16px !important; }
.chip {
    display: inline-block; padding: .2rem .7rem; margin: .15rem;
    border-radius: 999px; font-size: .8rem; font-weight: 600;
    background: #eef2ff; color: #4338ca; border: 1px solid #c7d2fe;
}
.chip.folder { background: #f3e8ff; color: #7e22ce; border-color: #e9d5ff; }
.chip.file   { background: #e0f2fe; color: #0369a1; border-color: #bae6fd; }
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)


# --------------------------------------------------------------------------
# Helpers
# --------------------------------------------------------------------------
def rel(p: Path) -> str:
    return p.relative_to(ROOT).as_posix()


def safe_path(relative: str) -> Path:
    """Resolve a path and make sure it stays inside the workspace sandbox."""
    p = (ROOT / relative).resolve()
    if p != ROOT and not p.is_relative_to(ROOT):
        raise ValueError("Path is outside the workspace.")
    return p


def valid_name(name: str) -> bool:
    name = name.strip()
    return bool(name) and "/" not in name and "\\" not in name and name not in {".", ".."}


def human_size(num: float) -> str:
    for unit in ("B", "KB", "MB", "GB"):
        if num < 1024:
            return f"{num:.0f} {unit}" if unit == "B" else f"{num:.1f} {unit}"
        num /= 1024
    return f"{num:.1f} TB"


def get_folders():
    return sorted((p for p in ROOT.rglob("*") if p.is_dir()), key=lambda x: rel(x).lower())


def get_files():
    return sorted((p for p in ROOT.rglob("*") if p.is_file()), key=lambda x: rel(x).lower())


def folder_total_size(folder: Path) -> int:
    return sum(f.stat().st_size for f in folder.rglob("*") if f.is_file())


def parent_options():
    return [ROOT_LABEL] + [rel(f) for f in get_folders()]


def parent_path(choice: str) -> Path:
    return ROOT if choice == ROOT_LABEL else safe_path(choice)


def flash(message: str, icon: str = "✅"):
    st.session_state["flash"] = (message, icon)
    st.rerun()


def metric_card(icon: str, label: str, value: str, gradient: str) -> str:
    return f"""
    <div class="card-wrap">
      <div class="metric-card">
        <div class="icon" style="background:{gradient};">{icon}</div>
        <div class="value">{value}</div>
        <div class="label">{label}</div>
      </div>
    </div>
    """


# Show a pending message after a rerun
if "flash" in st.session_state:
    msg, icon = st.session_state.pop("flash")
    st.toast(msg, icon=icon)

# --------------------------------------------------------------------------
# Sidebar
# --------------------------------------------------------------------------
with st.sidebar:
    st.markdown("## 🧊 FileVerse 3D")
    st.caption("Manage folders and files with a clean 3D interface.")
    st.markdown("---")
    st.markdown("**📍 Workspace**")
    st.code(str(ROOT), language=None)
    if st.button("🔄 Refresh", use_container_width=True):
        st.rerun()
    st.markdown("---")
    st.markdown(
        """
        **Quick guide**
        - 📁 *Folders*: create, rename, delete
        - 📄 *Files*: create, read, update, delete
        - 🧊 *3D Explorer*: see your tree in 3D
        """
    )
    st.info("Everything is sandboxed to the workspace folder for safety.", icon="🛡️")

# --------------------------------------------------------------------------
# Hero
# --------------------------------------------------------------------------
st.markdown(
    """
    <div class="hero">
      <div>
        <h1>FileVerse 3D</h1>
        <p>Create, read, update and delete files and folders, all in one beautiful space.</p>
      </div>
      <div class="scene">
        <div class="cube">
          <div class="face front">📁</div>
          <div class="face back">📄</div>
          <div class="face right">✏️</div>
          <div class="face left">🗑️</div>
          <div class="face top">🔍</div>
          <div class="face bottom">🧊</div>
        </div>
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)

tab_dash, tab_folders, tab_files, tab_3d = st.tabs(
    ["🏠 Dashboard", "📁 Folders", "📄 Files", "🧊 3D Explorer"]
)

# --------------------------------------------------------------------------
# Dashboard
# --------------------------------------------------------------------------
with tab_dash:
    folders = get_folders()
    files = get_files()
    total = sum(f.stat().st_size for f in files)

    c1, c2, c3, c4 = st.columns(4)
    c1.markdown(
        metric_card("📁", "Folders", str(len(folders)), "linear-gradient(135deg,#ddd6fe,#c4b5fd)"),
        unsafe_allow_html=True,
    )
    c2.markdown(
        metric_card("📄", "Files", str(len(files)), "linear-gradient(135deg,#bae6fd,#7dd3fc)"),
        unsafe_allow_html=True,
    )
    c3.markdown(
        metric_card("💾", "Total size", human_size(total), "linear-gradient(135deg,#a7f3d0,#6ee7b7)"),
        unsafe_allow_html=True,
    )
    latest = max(files, key=lambda f: f.stat().st_mtime) if files else None
    c4.markdown(
        metric_card(
            "⏱️",
            "Last change",
            datetime.fromtimestamp(latest.stat().st_mtime).strftime("%d %b, %H:%M") if latest else "-",
            "linear-gradient(135deg,#fde68a,#fcd34d)",
        ),
        unsafe_allow_html=True,
    )

    st.markdown("<br>", unsafe_allow_html=True)
    left, right = st.columns([3, 2])

    with left:
        st.markdown('<div class="panel"><h3>🗂️ Workspace contents</h3>', unsafe_allow_html=True)
        if not folders and not files:
            st.info("The workspace is empty. Create your first folder or file from the tabs above.")
        else:
            rows = []
            for f in folders:
                rows.append(
                    {"Type": "📁 Folder", "Path": rel(f), "Size": human_size(folder_total_size(f)),
                     "Modified": datetime.fromtimestamp(f.stat().st_mtime).strftime("%Y-%m-%d %H:%M")}
                )
            for f in files:
                rows.append(
                    {"Type": "📄 File", "Path": rel(f), "Size": human_size(f.stat().st_size),
                     "Modified": datetime.fromtimestamp(f.stat().st_mtime).strftime("%Y-%m-%d %H:%M")}
                )
            st.dataframe(rows, use_container_width=True, hide_index=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with right:
        st.markdown('<div class="panel"><h3>🕒 Recent files</h3>', unsafe_allow_html=True)
        recent = sorted(files, key=lambda f: f.stat().st_mtime, reverse=True)[:6]
        if recent:
            for f in recent:
                st.markdown(
                    f'<span class="chip file">📄 {rel(f)}</span> '
                    f'<span style="color:#64748b;font-size:.8rem;">{human_size(f.stat().st_size)}</span>',
                    unsafe_allow_html=True,
                )
        else:
            st.caption("No files yet.")
        st.markdown("</div>", unsafe_allow_html=True)

# --------------------------------------------------------------------------
# Folders: Create / Rename / Delete
# --------------------------------------------------------------------------
with tab_folders:
    col_a, col_b = st.columns(2)

    with col_a:
        st.markdown('<div class="panel"><h3>➕ Create folder</h3>', unsafe_allow_html=True)
        parent_choice = st.selectbox("Create inside", parent_options(), key="new_folder_parent")
        new_folder = st.text_input("Folder name", placeholder="e.g. projects", key="new_folder_name")
        if st.button("Create folder", key="btn_create_folder"):
            if not valid_name(new_folder):
                st.error("Please enter a valid folder name (no slashes).")
            else:
                target = parent_path(parent_choice) / new_folder.strip()
                if target.exists():
                    st.error("This folder name already exists. Try another.")
                else:
                    target.mkdir()
                    flash(f"Folder '{new_folder.strip()}' created successfully", "📁")
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown('<div class="panel"><h3>✏️ Rename folder</h3>', unsafe_allow_html=True)
        folder_list = [rel(f) for f in get_folders()]
        if folder_list:
            old_choice = st.selectbox("Choose folder", folder_list, key="rename_folder_pick")
            new_name = st.text_input("New name", key="rename_folder_new")
            if st.button("Rename folder", key="btn_rename_folder"):
                if not valid_name(new_name):
                    st.error("Please enter a valid new name.")
                else:
                    old_p = safe_path(old_choice)
                    new_p = old_p.parent / new_name.strip()
                    if new_p.exists():
                        st.error("A folder or file with that name already exists.")
                    else:
                        old_p.rename(new_p)
                        flash("Folder renamed successfully", "✏️")
        else:
            st.caption("No folders to rename yet.")
        st.markdown("</div>", unsafe_allow_html=True)

    with col_b:
        st.markdown('<div class="panel"><h3>🗑️ Delete folder (with all files)</h3>', unsafe_allow_html=True)
        folder_list = [rel(f) for f in get_folders()]
        if folder_list:
            del_choice = st.selectbox("Choose folder to delete", folder_list, key="delete_folder_pick")
            del_p = safe_path(del_choice)
            n_files = sum(1 for x in del_p.rglob("*") if x.is_file())
            n_dirs = sum(1 for x in del_p.rglob("*") if x.is_dir())

            if n_files or n_dirs:
                st.warning(
                    f"This folder contains **{n_files} file(s)** and **{n_dirs} subfolder(s)** "
                    f"({human_size(folder_total_size(del_p))}). Everything inside will be deleted permanently.",
                    icon="⚠️",
                )
                confirmed = st.checkbox("Yes, delete the folder and everything inside it", key="confirm_delete_folder")
            else:
                st.caption("This folder is empty.")
                confirmed = True

            with st.container(key="danger_delete_folder"):
                if st.button("Delete folder", key="btn_delete_folder"):
                    if not confirmed:
                        st.error("Please tick the confirmation box first.")
                    else:
                        shutil.rmtree(del_p)  # removes the folder + all files and subfolders
                        flash(f"Folder '{del_choice}' and all its contents deleted", "🗑️")
        else:
            st.caption("No folders available.")
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown('<div class="panel"><h3>📂 Folders</h3>', unsafe_allow_html=True)
        flist = get_folders()
        if flist:
            st.markdown(
                " ".join(f'<span class="chip folder">📁 {rel(f)}</span>' for f in flist),
                unsafe_allow_html=True,
            )
        else:
            st.caption("No folders yet.")
        st.markdown("</div>", unsafe_allow_html=True)

# --------------------------------------------------------------------------
# Files: Create / Read / Update / Delete
# --------------------------------------------------------------------------
with tab_files:
    sub_create, sub_read, sub_update, sub_delete = st.tabs(
        ["➕ Create", "👁️ Read", "✏️ Update", "🗑️ Delete"]
    )

    # ---- Create ----
    with sub_create:
        st.markdown('<div class="panel"><h3>Create a new file</h3>', unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            file_parent = st.selectbox("Create inside", parent_options(), key="new_file_parent")
        with c2:
            file_name = st.text_input("File name with extension", placeholder="notes.txt", key="new_file_name")
        content = st.text_area("File content", height=180, key="new_file_content")
        if st.button("Create file", key="btn_create_file"):
            if not valid_name(file_name):
                st.error("Please enter a valid file name (no slashes).")
            else:
                target = parent_path(file_parent) / file_name.strip()
                if target.exists():
                    st.error("File name already exists. Try another name.")
                else:
                    target.write_text(content, encoding="utf-8")
                    flash(f"File '{file_name.strip()}' created successfully", "📄")
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown('<div class="panel"><h3>⬆️ Or upload files</h3>', unsafe_allow_html=True)
        up_parent = st.selectbox("Upload into", parent_options(), key="upload_parent")
        uploads = st.file_uploader("Drop files here", accept_multiple_files=True, key="uploader")
        if uploads and st.button("Save uploaded files", key="btn_upload"):
            saved = 0
            for up in uploads:
                name = Path(up.name).name
                if valid_name(name):
                    (parent_path(up_parent) / name).write_bytes(up.getbuffer())
                    saved += 1
            flash(f"{saved} file(s) uploaded", "⬆️")
        st.markdown("</div>", unsafe_allow_html=True)

    # ---- Read ----
    with sub_read:
        st.markdown('<div class="panel"><h3>Read a file</h3>', unsafe_allow_html=True)
        files_now = [rel(f) for f in get_files()]
        if files_now:
            pick = st.selectbox("Which file do you want to read?", files_now, key="read_pick")
            p = safe_path(pick)
            st.caption(
                f"Size: {human_size(p.stat().st_size)}  |  Modified: "
                f"{datetime.fromtimestamp(p.stat().st_mtime).strftime('%Y-%m-%d %H:%M:%S')}"
            )
            raw = p.read_bytes()
            try:
                text = raw.decode("utf-8")
                lang = p.suffix.lstrip(".") or None
                st.code(text if text else "(empty file)", language=lang, line_numbers=True)
            except UnicodeDecodeError:
                st.info("This looks like a binary file, so it can't be shown as text.")
            st.download_button("Download file", data=raw, file_name=p.name, key="dl_file")
        else:
            st.info("No files to read yet.")
        st.markdown("</div>", unsafe_allow_html=True)

    # ---- Update ----
    with sub_update:
        st.markdown('<div class="panel"><h3>Update a file</h3>', unsafe_allow_html=True)
        files_now = [rel(f) for f in get_files()]
        if files_now:
            pick = st.selectbox("File to update", files_now, key="update_pick")
            p = safe_path(pick)
            mode = st.radio(
                "What do you want to do?",
                ["Change the name", "Overwrite the content", "Append new content"],
                horizontal=True,
                key="update_mode",
            )
            if mode == "Change the name":
                new_name = st.text_input("New name with extension", key="update_new_name")
                if st.button("Rename file", key="btn_rename_file"):
                    if not valid_name(new_name):
                        st.error("Please enter a valid file name.")
                    else:
                        new_p = p.parent / new_name.strip()
                        if new_p.exists():
                            st.error("A file with that name already exists.")
                        else:
                            p.rename(new_p)
                            flash("File name changed successfully", "✏️")
            elif mode == "Overwrite the content":
                try:
                    current = p.read_text(encoding="utf-8")
                except UnicodeDecodeError:
                    current = ""
                    st.info("Binary file: current content can't be shown.")
                data = st.text_area("New content (replaces everything)", value=current, height=200,
                                    key=f"overwrite_{pick}")
                if st.button("Overwrite file", key="btn_overwrite"):
                    p.write_text(data, encoding="utf-8")
                    flash("File overwritten successfully", "📝")
            else:
                data = st.text_area("Text to append", height=160, key="append_text")
                if st.button("Append to file", key="btn_append"):
                    with open(p, "a", encoding="utf-8") as fs:
                        fs.write(data)
                    flash("Content appended successfully", "➕")
        else:
            st.info("No files to update yet.")
        st.markdown("</div>", unsafe_allow_html=True)

    # ---- Delete ----
    with sub_delete:
        st.markdown('<div class="panel"><h3>Delete a file</h3>', unsafe_allow_html=True)
        files_now = [rel(f) for f in get_files()]
        if files_now:
            pick = st.selectbox("File to delete", files_now, key="delete_pick")
            with st.container(key="danger_delete_file"):
                if st.button("Delete file", key="btn_delete_file"):
                    safe_path(pick).unlink()
                    flash(f"File '{pick}' deleted successfully", "🗑️")
        else:
            st.info("No files to delete.")
        st.markdown("</div>", unsafe_allow_html=True)

# --------------------------------------------------------------------------
# 3D Explorer: the workspace tree as an interactive 3D graph
# --------------------------------------------------------------------------
with tab_3d:
    st.markdown('<div class="panel"><h3>🧊 Workspace in 3D</h3>', unsafe_allow_html=True)
    st.caption(
        "X = folder depth, Y = position in the tree, Z = size. "
        "Drag to rotate, scroll to zoom, hover for details."
    )

    if not HAS_PLOTLY:
        st.warning("Install Plotly to see the 3D view:  `pip install plotly`")
    else:
        folders = get_folders()
        files = get_files()

        if not folders and not files:
            st.info("Add some folders and files to see them appear in 3D.")
        else:
            items = [(f, True) for f in folders] + [(f, False) for f in files]
            items.sort(key=lambda t: rel(t[0]).lower())

            pos = {".": (0, 0, 0)}
            names, xs, ys, zs, colors, symbols, sizes, hovers = (
                ["workspace"], [0], [0], [0], ["#6366f1"], ["diamond"], [14], ["workspace (root)"]
            )
            for idx, (p, is_dir) in enumerate(items, start=1):
                depth = len(p.relative_to(ROOT).parts)
                size_b = folder_total_size(p) if is_dir else p.stat().st_size
                z = size_b / 1024  # KB
                pos[rel(p)] = (depth, idx, z)
                names.append(p.name)
                xs.append(depth)
                ys.append(idx)
                zs.append(z)
                colors.append("#a78bfa" if is_dir else "#38bdf8")
                symbols.append("diamond" if is_dir else "circle")
                sizes.append(11 if is_dir else 8)
                hovers.append(
                    f"{'📁' if is_dir else '📄'} {rel(p)}<br>Size: {human_size(size_b)}"
                )

            # lines from parent to child
            lx, ly, lz = [], [], []
            for p, _ in items:
                parent_key = "." if p.parent == ROOT else rel(p.parent)
                a = pos.get(parent_key, (0, 0, 0))
                b = pos[rel(p)]
                lx += [a[0], b[0], None]
                ly += [a[1], b[1], None]
                lz += [a[2], b[2], None]

            fig = go.Figure()
            fig.add_trace(
                go.Scatter3d(
                    x=lx, y=ly, z=lz, mode="lines",
                    line=dict(color="#c7d2fe", width=5),
                    hoverinfo="skip", showlegend=False,
                )
            )
            fig.add_trace(
                go.Scatter3d(
                    x=xs, y=ys, z=zs, mode="markers+text",
                    text=names, textposition="top center",
                    textfont=dict(color="#334155", size=11),
                    marker=dict(size=sizes, color=colors, symbol=symbols,
                                line=dict(color="#ffffff", width=2), opacity=0.95),
                    hovertext=hovers, hoverinfo="text", showlegend=False,
                )
            )
            axis = dict(
                backgroundcolor="rgba(238,242,255,0.7)",
                gridcolor="#e0e7ff", zerolinecolor="#c7d2fe",
                showspikes=False, color="#475569",
            )
            fig.update_layout(
                height=620,
                margin=dict(l=0, r=0, t=10, b=0),
                paper_bgcolor="rgba(0,0,0,0)",
                scene=dict(
                    xaxis=dict(title="Depth", **axis),
                    yaxis=dict(title="Tree position", **axis),
                    zaxis=dict(title="Size (KB)", **axis),
                    camera=dict(eye=dict(x=1.6, y=1.6, z=0.9)),
                ),
            )
            st.plotly_chart(fig, use_container_width=True)

            st.markdown(
                '<span class="chip folder">◆ Folder</span> '
                '<span class="chip file">● File</span> '
                '<span class="chip">◆ Root</span>',
                unsafe_allow_html=True,
            )
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown(
    "<p style='text-align:center;color:#94a3b8;margin-top:2rem;'>FileVerse 3D · built with Streamlit</p>",
    unsafe_allow_html=True,
)