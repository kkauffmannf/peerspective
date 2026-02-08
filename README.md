# Peerspective 🔬
### *The Agentic Workflow for High-Integrity Peer Review*

[![Google AI Studio](https://img.shields.io/badge/Powered%20By-Google%20AI%20Studio-blue)](https://aistudio.google.com/)
[![Hackathon](https://img.shields.io/badge/Hackathon-Gemini%203-orange)](https://gemini3.devpost.com/)

**Peerspective** is an autonomous AI agent designed to solve the "Reviewer Burnout" crisis in STEM. It transforms the tedious, multiple-hours chore of scientific validation into a rigorous, supervised previous audit. By leveraging Gemini’s native multimodality and long-context reasoning, Peerspective detects discrepancies between figures and text, verifies novelty via real-time search, and ensures ethical compliance. 

## ✨ Key Features

*   **🎨 Visual Consistency Audit:** Directly analyzes the pixels of figures and charts to ensure that the visual data mathematically supports the claims made in the results section.
*   **🌎 Global Grounding Agent:** Uses **Google Search Grounding** to cross-reference a paper's claims against the most recent literature (up to 2026), flagging if a "novel" discovery has already been published.
*   **🎭 Journal-Specific Adaptation:** Dynamically adapts its reasoning engine to match specific journal tiers, including **Nature/Science** (impact-focused) and **IEEE** (technical-focused).
*   **⚖️ Automated COI Check:** Automatically scans the author list and metadata to flag potential Conflicts of Interest for the assigned reviewer.

---

## 🛠️ Technology Stack

*   **Core Engine:** `gemini-2.5-flash` (Optimized for speed and high-context reasoning).
*   **UI Framework:** Streamlit (Configured for a split-screen "Workstation" layout).
*   **Intelligence Tools:**
    *   **Google Search Tool:** For real-time academic fact-checking.
    *   **Multimodal File API:** For native processing of high-resolution scientific PDFs.
    *   **Context Caching:** (Simulated) for fast iterative deep-dives.

---

## 🤖 The "Agentic" Workflow
Unlike simple LLM wrappers, Peerspective follows a multi-step autonomous logic:
1.  **Ingestion:** Native indexing of the full manuscript including tables and images.
2.  **Audit Phase:** Runs a parallel check on Ethics (COI) and Novelty (Google Search).
3.  **Analysis Phase:** Reasons through the manuscript, mapping figures to results.
4.  **Synthesis Phase:** Generates a dual-perspective report (Public comments to authors vs. Private recommendations for the editor).

---

## 📥 Installation & Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/your-username/peerspective.git
   cd peerspective