import streamlit as st
from google import genai
from google.genai import types
import os
from dotenv import load_dotenv
import base64
import time

# --- 1. CONFIGURATION ---
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    st.error("❌ Missing Google API Key. Please create a .env file.")
    st.stop()

client = genai.Client(api_key=api_key)

# HACKATHON SETTING: Use 2.0 Flash for the best speed/intelligence balance in demos
MODEL_ID = "gemini-2.5-flash" 

st.set_page_config(layout="wide", page_title="Peerspective: Agentic Reviewer", page_icon="logo.png")

# --- CUSTOM CSS (Workstation Layout) ---
st.markdown("""
    <style>
        /* PDF Container - Fixed height for workstation feel */
        .pdf-container { 
            height: 85vh; 
            width: 100%; 
            overflow: hidden; 
            border: 1px solid #ddd; 
            border-radius: 8px; 
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        iframe { width: 100%; height: 100%; border: none; }
        
        /* Agent Status Bar - Professional styling */
        .stStatus { border-left: 4px solid #4285F4 !important; background-color: #f8f9fa; }
        
        /* Tabs - Clean look */
        .stTabs [data-baseweb="tab-list"] { gap: 24px; }
        .stTabs [data-baseweb="tab"] { height: 50px; white-space: pre-wrap; background-color: #fff; border-radius: 4px; gap: 1px; padding-top: 10px; padding-bottom: 10px; }
    </style>
""", unsafe_allow_html=True)

# --- JOURNAL TEMPLATES (The "Smart" Feature) ---
JOURNAL_TEMPLATES = {
    "Standard (General)": """
        1. **Executive Summary**: Brief overview.
        2. **Major Comments**: Significant flaws in methodology or logic.
        3. **Minor Comments**: Typos, labeling issues.
    """,
    "Nature / Science (Impact-Focused)": """
        1. **Impact Statement**: Does this paper fundamentally advance the field? (News & Views style).
        2. **Novelty Check**: Is the finding truly new or just incremental?
        3. **Technical Rigor**: Are the statistics robust enough for a general audience?
        *Tone: Critical, High-Level, Demanding.*
    """,
    "IEEE / Technical (Method-Focused)": """
        1. **Technical Merit**: Is the algorithm/math sound?
        2. **Replicability**: Are the experiments described in enough detail?
        3. **Equation Validation**: Check specific formulas (Eq 1, Eq 2...).
        *Tone: Precise, Mathematical, Dry.*
    """
}

# --- HELPER: PDF DISPLAY ---
def display_pdf(file_bytes):
    base64_pdf = base64.b64encode(file_bytes).decode('utf-8')
    # '#view=FitH' ensures it fits the width nicely
    st.markdown(f'<div class="pdf-container"><iframe src="data:application/pdf;base64,{base64_pdf}#view=FitH"></iframe></div>', unsafe_allow_html=True)

# --- 2. SIDEBAR ---
with st.sidebar:
    st.image("logo.png", width=70)
    st.title("Peerspective")
    st.caption(f"Engine: {MODEL_ID}")
    
    st.subheader("1. Submission")
    uploaded_file = st.file_uploader("Upload Manuscript", type=['pdf'])
    
    st.divider()
    
    st.subheader("2. Agent Configuration")
    reviewer_name = st.text_input("Reviewer Name (for COI)", "Dr. Peer Reviewer")
    
    # NEW: Journal Style Selector
    selected_journal = st.selectbox(
        "Target Journal Template", 
        list(JOURNAL_TEMPLATES.keys())
    )

# --- 3. MAIN WORKSTATION ---
if not uploaded_file:
    # Welcome / Empty State
    st.info("👈 Upload a PDF to launch the Agentic Workstation.")
    st.stop()

# Layout: Agent (Left) | PDF (Right)
col_agent, col_pdf = st.columns([1, 1.1])

# === LEFT COLUMN: AGENT ===
with col_agent:
    st.subheader("🤖 Review Console")
    
    # 1. Background Ingestion
    with open("temp_paper.pdf", "wb") as f:
        f.write(uploaded_file.getvalue())

    # Only upload to Gemini once per file
    if "gemini_file" not in st.session_state:
        with st.spinner("🧠 Ingesting Visuals & Text..."):
            file_ref = client.files.upload(file="temp_paper.pdf")
            st.session_state["gemini_file"] = file_ref
            st.toast("Manuscript Indexed", icon="✅")

    # 2. The "Agentic" Action Button
    if st.button("🚀 Run Full Review Cycle", type="primary", use_container_width=True):
        
        # Use st.status to show the "Thinking" process (Crucial for Demos)
        with st.status("Agent is working...", expanded=True) as status:
            
            # --- PHASE 1: THE AUDIT (Speed Optimized) ---
            # Combines COI + Novelty Search in one call
            status.write("🕵️‍♂️ Phase 1: Auditing Ethics (COI) & Novelty...")
            
            audit_prompt = f"""
            Act as a Screening Agent. Perform two checks:
            
            1. **Conflict of Interest (COI)**: Check the author list. Is '{reviewer_name}' an author or close affiliate? Output 'COI: CLEAN' or 'COI: WARNING'.
            2. **Novelty Verification**: Extract the core claim. Use Google Search to find if it contradicts papers from past 5 years as of today.
            
            Output a structured summary.
            """
            
            # Enable Google Search Tool
            search_tool = types.Tool(google_search=types.GoogleSearch())
            
            audit_response = client.models.generate_content(
                model=MODEL_ID,
                contents=[st.session_state["gemini_file"], audit_prompt],
                config=types.GenerateContentConfig(tools=[search_tool])
            )
            
            st.session_state["audit_data"] = audit_response.text
            status.write("✅ Pre-flight Checks Complete.")

            # --- PHASE 2: THE DRAFT (Journal Specific) ---
            status.write(f"✍️ Phase 2: Synthesizing Review ({selected_journal})...")
            
            final_prompt = f"""
            You are an Expert Reviewer.
            
            CONTEXT:
            - Journal Style: {selected_journal}
            - Audit Data: {audit_response.text}
            
            TASK:
            1. Check Figures vs Text consistency (Visual Audit).
            2. Write a review following the **Style Guide** below:
            {JOURNAL_TEMPLATES[selected_journal]}
            
            CRITICAL OUTPUT FORMAT:
            You MUST separate the review into two parts using "===SPLIT===".
            
            Part 1: Comments to Authors (Constructive).
            ===SPLIT===
            Part 2: Confidential Comments to Editor (Brutal honesty, Accept/Reject).
            """
            
            review_response = client.models.generate_content(
                model=MODEL_ID,
                contents=[st.session_state["gemini_file"], final_prompt]
            )
            
            st.session_state["full_review"] = review_response.text
            status.update(label="✅ Review Cycle Complete!", state="complete", expanded=False)

    # 3. Results Display
    if "full_review" in st.session_state:
        
        # Display Audit Warnings if any
        if "audit_data" in st.session_state:
            with st.expander("🔍 View Pre-Flight Audit Log (COI & Search)", expanded=False):
                st.markdown(st.session_state["audit_data"])

        # Parse the Split Review
        try:
            parts = st.session_state["full_review"].split("===SPLIT===")
            public_review, private_review = parts[0], parts[1]
        except:
            public_review, private_review = st.session_state["full_review"], "Parsing Error: Could not separate sections."

        # Tabs for Output
        tab_authors, tab_editor = st.tabs(["📧 To Authors", "🔒 To Editor"])
        
        with tab_authors:
            st.markdown(public_review)
            st.download_button("Download Report (Authors)", public_review, "review_authors.md")
        
        with tab_editor:
            st.error("CONFIDENTIAL: Editor Eyes Only")
            st.markdown(private_review)
            st.download_button("Download Report (Editor)", private_review, "review_editor.md")

    # 4. Socratic Chat (Always Visible)
    st.divider()
    st.subheader("💬 Socratic Chat")
    st.caption("Ask questions about specific Figures or Equations.")

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if user_input := st.chat_input("Ex: 'Check the math in Eq 2'"):
        st.chat_message("user").markdown(user_input)
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        
        with st.chat_message("assistant"):
            with st.spinner("Checking manuscript..."):
                # Chat also uses Search Tool for consistency
                search_tool = types.Tool(google_search=types.GoogleSearch())
                
                response = client.models.generate_content(
                    model=MODEL_ID,
                    contents=[st.session_state["gemini_file"], user_input],
                    config=types.GenerateContentConfig(tools=[search_tool])
                )
                
                st.markdown(response.text)
                
                # Show Grounding Sources
                if response.candidates[0].grounding_metadata.search_entry_point:
                     st.markdown(response.candidates[0].grounding_metadata.search_entry_point.rendered_content, unsafe_allow_html=True)

                st.session_state.chat_history.append({"role": "assistant", "content": response.text})

# === RIGHT COLUMN: PDF ===
with col_pdf:
    display_pdf(uploaded_file.getvalue())

# --- Attribution ---
st.markdown("---")
st.markdown('<a href="https://www.flaticon.com/free-icons/scanner" title="scanner icons">Scanner icons created by manshagraphics - Flaticon</a>', unsafe_allow_html=True)