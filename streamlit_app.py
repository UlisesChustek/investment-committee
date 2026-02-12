# streamlit_app.py
import streamlit as st
import os
import yfinance as yf
from src.graph import app
from src.pdf_generator import create_pdf

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="AI Investment Committee",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- CSS STYLING (Kept exactly as you liked it) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
    .stApp {
        background-color: #050505;
        background-image: radial-gradient(circle at 50% 0%, #1a1a1a 0%, #050505 70%);
        font-family: 'Inter', sans-serif;
    }
    .main-header { text-align: center; margin-bottom: 40px; }
    .main-title {
        font-size: 3rem; font-weight: 800;
        background: -webkit-linear-gradient(0deg, #fff, #888);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .subtitle { color: #666; font-size: 1.1rem; margin-top: -10px; }
    .agent-card {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
        border-radius: 12px;
        padding: 24px;
        width: 100%;
        transition: all 0.4s ease;
        position: relative; overflow: hidden;
    }
    .status-waiting { opacity: 0.5; border-color: #333; }
    .status-running { 
        border-color: #3B82F6; background: rgba(59, 130, 246, 0.05);
        box-shadow: 0 0 30px rgba(59, 130, 246, 0.15);
    }
    .status-complete { border-color: #10B981; background: rgba(16, 185, 129, 0.05); }
    .status-error { border-color: #EF4444; background: rgba(239, 68, 68, 0.05); }
    .agent-name { font-size: 1.25rem; font-weight: 700; color: #fff; margin-bottom: 12px; }
    .agent-role { font-size: 0.75rem; text-transform: uppercase; font-weight: 600; display: block; }
    .agent-status-text { font-size: 0.85rem; display: flex; align-items: center; gap: 8px; }
    .progress-line { height: 2px; width: 100%; background: #222; margin-top: 15px; position: relative; overflow: hidden; }
    .progress-bar { height: 100%; background: #3B82F6; position: absolute; animation: progress 2s infinite ease-in-out; }
    @keyframes progress { 0% { left: -100%; width: 50%; } 100% { left: 100%; width: 50%; } }
    .clear-button {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.15);
        backdrop-filter: blur(10px);
        border-radius: 8px;
        padding: 12px 24px;
        color: #fff;
        font-weight: 600;
        transition: all 0.3s ease;
        cursor: pointer;
    }
    .clear-button:hover {
        background: rgba(255, 255, 255, 0.1);
        border-color: rgba(255, 255, 255, 0.3);
        box-shadow: 0 0 20px rgba(255, 255, 255, 0.1);
        transform: translateY(-2px);
    }
    #MainMenu {visibility: hidden;} footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# --- HELPER FUNCTIONS ---
def render_header():
    st.markdown("""
        <div class="main-header">
            <div class="main-title">AI Investment Committee</div>
            <div class="subtitle">Autonomous Multi-Agent Equity Research System</div>
        </div>
    """, unsafe_allow_html=True)

def render_agent_card(placeholder, role, name, status="waiting", log="System Standby"):
    color_map = {"waiting": "#666", "running": "#3B82F6", "complete": "#10B981", "error": "#EF4444"}
    icon_map = {"waiting": "⚪", "running": "🔵", "complete": "🟢", "error": "🔴"}
    color = color_map.get(status, "#666")
    icon = icon_map.get(status, "⚪")
    progress_html = f"""<div class="progress-line"><div class="progress-bar"></div></div>""" if status == "running" else ""
    
    html = f"""
    <div class="agent-card status-{status}">
        <span class="agent-role" style="color: {color};">{role}</span>
        <div class="agent-name">{name}</div>
        <div class="agent-status-text" style="color: {color};">{icon} {log}</div>
        {progress_html}
    </div>
    """
    placeholder.markdown(html, unsafe_allow_html=True)

def validate_ticker(ticker):
    try:
        info = yf.Ticker(ticker).history(period="1d")
        return not info.empty
    except: return False

# --- MAIN EXECUTION ---
render_header()

# 1. INITIALIZE SESSION STATE (Persistence Layer)
if "report_data" not in st.session_state:
    st.session_state.report_data = None

# 2. INPUT SECTION
with st.container():
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        with st.form("analysis_form"):
            ticker = st.text_input("", placeholder="ENTER TICKER (e.g. NVDA)", label_visibility="collapsed")
            submitted = st.form_submit_button("INITIATE ANALYSIS", type="primary", use_container_width=True)

# 3. AGENT PIPELINE UI
st.markdown("<br>", unsafe_allow_html=True)
col1, col2, col3 = st.columns(3)
with col1: p1 = st.empty()
with col2: p2 = st.empty()
with col3: p3 = st.empty()

# Default State
render_agent_card(p1, "DATA ACQUISITION", "The Researcher", "waiting")
render_agent_card(p2, "QUANTITATIVE ANALYSIS", "The Analyst", "waiting")
render_agent_card(p3, "FINAL SYNTHESIS", "The Writer", "waiting")

# 4. WORKFLOW LOGIC
if submitted and ticker:
    clean_ticker = ticker.upper().replace(" INC", "").strip()
    
    # Validation
    if not validate_ticker(clean_ticker):
        render_agent_card(p1, "DATA ACQUISITION", "The Researcher", "error", f"Asset '{clean_ticker}' Not Found")
        st.error(f"❌ Critical Error: Ticker '{clean_ticker}' does not exist.")
        st.stop()
            
    # Run Agents
    render_agent_card(p1, "DATA ACQUISITION", "The Researcher", "running", f"Scanning web for {clean_ticker}...")
    state = {"ticker": clean_ticker, "messages": []}
    
    # Variables to hold data
    final_report = ""
    chart_path = ""
    metrics = {}

    for chunk in app.stream(state, stream_mode="updates"):
        for node, output in chunk.items():
            if node == "researcher":
                render_agent_card(p1, "DATA ACQUISITION", "The Researcher", "complete", "Market Sentiment Acquired")
                render_agent_card(p2, "QUANTITATIVE ANALYSIS", "The Analyst", "running", "Fetching OHLCV Data...")
            elif node == "analyst":
                chart_path = output.get("chart_path")
                metrics = output.get("metrics")
                render_agent_card(p2, "QUANTITATIVE ANALYSIS", "The Analyst", "complete", "Technical Chart Generated")
                render_agent_card(p3, "FINAL SYNTHESIS", "The Writer", "running", "Compiling Investment Thesis...")
            elif node == "writer":
                final_report = output.get("final_report")
                render_agent_card(p3, "FINAL SYNTHESIS", "The Writer", "complete", "Report Ready for Review")

    # SAVE TO SESSION STATE
    st.session_state.report_data = {
        "ticker": clean_ticker,
        "report": final_report,
        "chart": chart_path,
        "metrics": metrics
    }

# 5. RENDER RESULTS (FROM SESSION STATE)
if st.session_state.report_data:
    data = st.session_state.report_data
    
    # If the user just ran the analysis, keep the cards green. 
    # If they are just viewing a previous result, we might want to show them as static or keep them green.
    # For simplicity, we redraw the green cards if data exists.
    render_agent_card(p1, "DATA ACQUISITION", "The Researcher", "complete", "Market Sentiment Acquired")
    render_agent_card(p2, "QUANTITATIVE ANALYSIS", "The Analyst", "complete", "Technical Chart Generated")
    render_agent_card(p3, "FINAL SYNTHESIS", "The Writer", "complete", "Report Ready for Review")

    st.markdown("---")
    
    # A. Metrics
    if data["metrics"]:
        st.markdown(f"### 📊 {data['ticker']} Market Pulse")
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Current Price", data["metrics"].get("current_price"), data["metrics"].get("change"))
        m2.metric("Daily Change", data["metrics"].get("pct_change"))
        m3.metric("Volume", data["metrics"].get("volume"))
        
        # Dynamic Signal Logic
        signal = data["metrics"].get("signal", "NEUTRAL")
        signal_color = "normal"
        if signal == "BULLISH": signal_color = "off" # Streamlit doesn't support green text easily in metric delta, but we can pass it as value
        m4.metric("AI Signal", signal, "20-Day SMA X-Over")

    st.markdown("---")

    # B. Report Body
    r1, r2 = st.columns([1.6, 1])
    with r1:
        st.markdown(f"### 📑 Investment Thesis")
        st.markdown(data["report"])
    
    with r2:
        st.markdown("### 📈 Technical Indicators")
        if data["chart"] and os.path.exists(data["chart"]):
            st.image(data["chart"], use_container_width=True)
        else:
            st.warning("Chart data unavailable.")
        
        # C. PDF Download (Safe to click now!)
        st.markdown("<br>", unsafe_allow_html=True)
        pdf_name = f"{data['ticker']}_Report.pdf"
        create_pdf(data['ticker'], data['report'], pdf_name, data['chart'])
        
        with open(pdf_name, "rb") as f:
            st.download_button(
                label="📥 DOWNLOAD PDF DOSSIER",
                data=f,
                file_name=pdf_name,
                mime="application/pdf",
                type="primary",
                use_container_width=True
            )
        
        # D. Clear Button
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🔄 CLEAR & START NEW ANALYSIS", type="secondary", use_container_width=True):
            st.session_state.report_data = None
            st.rerun()