import streamlit as st
import time
import re

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Kapture Prism",
    page_icon="🔴",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# --- 2. ULTRA-PREMIUM CSS ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');

    .stApp {
        background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
        font-family: 'Inter', sans-serif;
    }
    
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    @keyframes slideUpFade {
        0% { opacity: 0; transform: translateY(30px) scale(0.98); }
        100% { opacity: 1; transform: translateY(0) scale(1); }
    }

    /* --- HEADER STYLING --- */
    .header-container {
        text-align: center;
        padding-top: 40px;
        padding-bottom: 20px;
        animation: slideUpFade 0.8s ease-out;
    }
    .header-title {
        font-size: 3.5rem;
        font-weight: 800;
        color: #d32f2f;
        letter-spacing: -2px;
        line-height: 1.1;
    }
    .header-prism { color: #263238; }
    .header-subtitle {
        font-size: 1.1rem;
        color: #90a4ae;
        font-weight: 500;
        margin-top: 10px;
        letter-spacing: 0.5px;
        text-transform: uppercase;
    }

    /* --- PROBLEM STATEMENT BOX --- */
    .business-case-box {
        background-color: #fff3e0; /* Soft Orange/Gold tint */
        border-left: 5px solid #ff9800;
        padding: 20px;
        border-radius: 8px;
        margin-bottom: 30px;
        font-size: 0.95rem;
        color: #455a64;
        line-height: 1.5;
        animation: slideUpFade 1s ease-out;
    }
    .case-title {
        font-weight: 700;
        color: #e65100;
        margin-bottom: 8px;
        text-transform: uppercase;
        font-size: 0.85rem;
    }

    /* --- INPUT BAR --- */
    .stTextInput > div > div > input {
        border-radius: 50px;
        border: 2px solid transparent;
        background-color: #ffffff;
        padding: 22px 30px;
        font-size: 1.2rem;
        color: #37474f;
        box-shadow: 0 10px 30px -5px rgba(0, 0, 0, 0.08);
        transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
    }
    .stTextInput > div > div > input:focus {
        border-color: #d32f2f;
        background-color: #fff;
        outline: none;
        box-shadow: 0 4px 25px rgba(211, 47, 47, 0.15);
    }

    /* --- ANSWER CARD --- */
    .answer-card {
        background: #ffffff;
        border-radius: 24px;
        padding: 40px;
        margin-top: 40px;
        box-shadow: 0 20px 40px -10px rgba(0,0,0,0.1); 
        border: 1px solid #f1f3f4;
        position: relative;
        overflow: hidden;
        animation: slideUpFade 0.6s cubic-bezier(0.2, 0.8, 0.2, 1) forwards;
    }
    .answer-card::before {
        content: "";
        position: absolute;
        left: 0;
        top: 0;
        bottom: 0;
        width: 8px;
        background: linear-gradient(180deg, #d32f2f 0%, #ff5252 100%);
    }
    .card-label {
        font-size: 0.85rem;
        font-weight: 700;
        letter-spacing: 1.5px;
        text-transform: uppercase;
        color: #d32f2f;
        margin-bottom: 15px;
        display: block;
        opacity: 0.8;
    }
    .card-body {
        font-size: 1.35rem;
        line-height: 1.6;
        color: #1c262b;
        font-weight: 500;
    }

    /* --- FOOTER --- */
    .custom-footer {
        text-align: center;
        margin-top: 100px;
        padding-bottom: 30px;
        font-size: 1.8rem;
        font-weight: 900; 
        color: #fbc02d;
        text-shadow: 2px 2px 0px rgba(0,0,0,0.05);
        letter-spacing: -0.5px;
        animation: slideUpFade 1.2s ease-out;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. LOGIC (BRAIN) ---
STOP_WORDS = {
    "how", "do", "we", "you", "ensure", "what", "is", "are", "can", "the", "a", "an", 
    "of", "in", "to", "for", "on", "does", "doesn't", "it", "be", "us", "our", "my"
}

def clean_and_tokenize(text):
    words = re.findall(r'\w+', text.lower())
    return {w for w in words if w not in STOP_WORDS}

def load_and_parse_brain():
    qa_database = []
    current_category = "General"
    try:
        with open("kapture_brain.txt", "r", errors="ignore") as f:
            lines = f.readlines()
        current_q = None
        current_a = None
        for line in lines:
            line = line.strip()
            if not line: continue
            if line.startswith("[CATEGORY:"):
                current_category = line.split(":")[1].strip(" ]")
            elif line.startswith("Q:"):
                current_q = line[2:].strip()
            elif line.startswith("A:"):
                current_a = line[2:].strip()
                if current_q and current_a:
                    qa_database.append({
                        "category": current_category,
                        "question": current_q,
                        "answer": current_a,
                        "tokens": clean_and_tokenize(current_q)
                    })
                    current_q = None 
        return qa_database
    except FileNotFoundError:
        return []

brain = load_and_parse_brain()

def find_best_match(user_query):
    if not brain: return "System Error", "Knowledge Base file is missing."
    user_tokens = clean_and_tokenize(user_query)
    best_score = 0
    best_match = None
    for item in brain:
        overlap = len(user_tokens.intersection(item['tokens']))
        if overlap > best_score:
            best_score = overlap
            best_match = item
    if best_score == 0:
        return "No Direct Match", "I couldn't find a specific technical answer for that. (Tip: Try using specific keywords like 'latency', 'webhook', or 'storage')."
    return best_match['category'], best_match['answer']

# --- 4. THE UI RENDER ---

# Header
st.markdown("""
    <div class="header-container">
        <div class="header-title">Kapture <span class="header-prism">Prism</span></div>
        <div class="header-subtitle">Sales Engineering Intelligence</div>
    </div>
""", unsafe_allow_html=True)

# THE BUSINESS CASE (New Section)
with st.expander("ℹ️ Why this tool exists (Problem & Solution)"):
    st.markdown("""
    <div class="business-case-box">
        <div class="case-title">THE PROBLEM: The "Technical Feasibility" Bottleneck</div>
        In enterprise sales, deal velocity stalls when commercial teams lack the architectural knowledge to answer specific technical queries (e.g., API limits, SOC2 compliance). This triggers a "Check-and-Return" loop, adding 3-5 days of latency while waiting for Solution Engineers to respond to routine Tier-1 questions.
        <br><br>
        <div class="case-title">THE SOLUTION: Automated Solutioning Intelligence</div>
        <strong>Kapture Prism</strong> is a deterministic retrieval engine that decouples technical verification from engineering availability. By instantly retrieving verified specs from the engineering knowledge base, it empowers Sales Reps to handle technical objections in real-time. This reduces time-to-answer from days to milliseconds and preserves Solution Engineering capacity for high-value custom implementations.
    </div>
    """, unsafe_allow_html=True)

# Input
query = st.text_input("", placeholder="Ask Prism a technical question...")

# Result
if query:
    with st.spinner(""):
        time.sleep(0.4) 
        category, answer = find_best_match(query)
    
    st.markdown(f"""
    <div class="answer-card">
        <span class="card-label">{category}</span>
        <div class="card-body">{answer}</div>
    </div>
    """, unsafe_allow_html=True)

# Footer
st.markdown("""
    <div class="custom-footer">
        ⚡ Powered by Prajwal's Lab
    </div>
""", unsafe_allow_html=True)
