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

# --- AGGRESSIVE CSS STYLING ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&family=JetBrains+Mono:wght@300;400;500&display=swap');
    
    :root {
        --bg-primary: #0c0c0c;
        --bg-secondary: #141414;
        --bg-tertiary: #1a1a1a;
        --border-primary: rgba(255, 255, 255, 0.08);
        --border-active: rgba(255, 255, 255, 0.15);
        --text-primary: #ffffff;
        --text-secondary: #8a8a8a;
        --text-dim: #4a4a4a;
        --accent: #e11d48;
        --accent-glow: rgba(225, 29, 72, 0.4);
        --accent-subtle: rgba(225, 29, 72, 0.1);
        --success: #22c55e;
        --warning: #f59e0b;
    }
    
    #MainMenu {visibility: hidden !important;}
    footer {visibility: hidden !important;}
    header {visibility: hidden !important;}
    
    .stApp {
        background: var(--bg-primary) !important;
        font-family: 'JetBrains Mono', monospace !important;
    }
    
    .stApp::before {
        content: '';
        position: fixed;
        top: -50%; left: -50%; right: -50%; bottom: -50%;
        width: 200%; height: 200%;
        background: 
            radial-gradient(circle at 20% 20%, rgba(225, 29, 72, 0.03) 0%, transparent 50%),
            radial-gradient(circle at 80% 80%, rgba(225, 29, 72, 0.02) 0%, transparent 50%);
        pointer-events: none;
        z-index: -2;
    }
    
    .stApp::after {
        content: '';
        position: fixed;
        top: 0; left: 0; right: 0; bottom: 0;
        background-image: 
            linear-gradient(rgba(255,255,255,0.015) 1px, transparent 1px),
            linear-gradient(90deg, rgba(255,255,255,0.015) 1px, transparent 1px);
        background-size: 40px 40px;
        pointer-events: none;
        z-index: -1;
    }
    
    [data-testid="stHeader"] {display: none !important;}
    [data-testid="stToolbar"] {display: none !important;}
    
    ::-webkit-scrollbar {width: 6px; height: 6px;}
    ::-webkit-scrollbar-track {background: var(--bg-primary);}
    ::-webkit-scrollbar-thumb {background: var(--border-active); border-radius: 3px;}
    ::-webkit-scrollbar-thumb:hover {background: var(--text-dim);}
    
    .hero-section {
        text-align: center;
        padding: 60px 20px 40px;
        position: relative;
    }
    
    .hero-title {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 3.5rem;
        font-weight: 700;
        color: var(--text-primary);
        letter-spacing: -0.04em;
        line-height: 1.1;
        margin-bottom: 16px;
    }
    
    .hero-title span {
        color: var(--accent);
    }
    
    .hero-subtitle {
        font-size: 0.75rem;
        color: var(--text-dim);
        letter-spacing: 0.3em;
        text-transform: uppercase;
    }
    
    .hero-line {
        width: 60px;
        height: 1px;
        background: var(--accent);
        margin: 24px auto 0;
    }
    
    .input-section {
        max-width: 500px;
        margin: 0 auto 50px;
        padding: 0 20px;
    }
    
    .ticker-input {
        background: var(--bg-secondary) !important;
        border: 1px solid var(--border-primary) !important;
        border-radius: 0 !important;
        color: var(--text-primary) !important;
        font-family: 'Space Grotesk', sans-serif !important;
        font-size: 1.2rem !important;
        padding: 20px 24px !important;
        letter-spacing: 0.1em;
        transition: all 0.3s ease !important;
    }
    
    .ticker-input:focus {
        border-color: var(--accent) !important;
        box-shadow: 0 0 30px var(--accent-subtle) !important;
        outline: none !important;
    }
    
    .ticker-input::placeholder {
        color: var(--text-dim) !important;
        letter-spacing: 0.15em;
    }
    
    .submit-btn {
        background: var(--accent) !important;
        color: white !important;
        border: none !important;
        border-radius: 0 !important;
        font-family: 'Space Grotesk', sans-serif !important;
        font-weight: 600 !important;
        font-size: 0.85rem !important;
        letter-spacing: 0.2em !important;
        padding: 20px 40px !important;
        margin-top: 16px;
        transition: all 0.3s ease !important;
        text-transform: uppercase;
    }
    
    .submit-btn:hover {
        background: #be123c !important;
        box-shadow: 0 0 40px var(--accent-glow) !important;
        transform: translateY(-2px);
    }
    
    .agents-container {
        padding: 0 40px;
        margin-bottom: 60px;
    }
    
    .agent-card {
        background: var(--bg-secondary);
        border: 1px solid var(--border-primary);
        border-radius: 0;
        padding: 32px;
        position: relative;
        overflow: hidden;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    .agent-card::before {
        content: '';
        position: absolute;
        top: 0; left: 0; width: 3px; height: 100%;
        background: var(--border-primary);
        transition: all 0.3s ease;
    }
    
    .agent-card:hover {
        background: var(--bg-tertiary);
        border-color: var(--border-active);
    }
    
    .agent-card:hover::before {
        background: var(--accent);
    }
    
    .agent-card.status-waiting {opacity: 0.3;}
    .agent-card.status-running {border-color: var(--accent);}
    .agent-card.status-running::before {background: var(--accent); width: 3px;}
    .agent-card.status-complete {border-color: rgba(34, 197, 94, 0.3);}
    .agent-card.status-complete::before {background: var(--success); width: 3px;}
    .agent-card.status-error {border-color: rgba(239, 68, 68, 0.3);}
    .agent-card.status-error::before {background: #ef4444; width: 3px;}
    
    .agent-number {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 0.7rem;
        color: var(--text-dim);
        letter-spacing: 0.2em;
        margin-bottom: 12px;
    }
    
    .agent-name {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 1.4rem;
        font-weight: 600;
        color: var(--text-primary);
        margin-bottom: 8px;
        letter-spacing: -0.02em;
    }
    
    .agent-role {
        font-size: 0.65rem;
        color: var(--text-secondary);
        letter-spacing: 0.15em;
        text-transform: uppercase;
        margin-bottom: 20px;
    }
    
    .agent-status {
        font-size: 0.75rem;
        color: var(--text-secondary);
        display: flex;
        align-items: center;
        gap: 10px;
    }
    
    .status-dot {
        width: 6px;
        height: 6px;
        border-radius: 50%;
        background: var(--text-dim);
    }
    
    .status-running .status-dot {
        background: var(--accent);
        box-shadow: 0 0 10px var(--accent);
        animation: pulse 1.5s infinite;
    }
    
    .status-complete .status-dot {background: var(--success);}
    .status-error .status-dot {background: #ef4444;}
    
    @keyframes pulse {
        0%, 100% {opacity: 1; transform: scale(1);}
        50% {opacity: 0.5; transform: scale(1.2);}
    }
    
    .agent-progress {
        height: 1px;
        background: var(--border-primary);
        margin-top: 20px;
        overflow: hidden;
    }
    
    .agent-progress-bar {
        height: 100%;
        background: var(--accent);
        animation: progress 2s infinite ease-in-out;
    }
    
    @keyframes progress {
        0% {width: 0%; margin-left: 0;}
        50% {width: 50%; margin-left: 25%;}
        100% {width: 0%; margin-left: 100%;}
    }
    
    .results-section {
        padding: 40px;
        background: var(--bg-secondary);
        border-top: 1px solid var(--border-primary);
    }
    
    .results-header {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 1.8rem;
        font-weight: 600;
        color: var(--text-primary);
        margin-bottom: 32px;
        letter-spacing: -0.02em;
    }
    
    .results-header span {
        color: var(--accent);
    }
    
    .metrics-grid {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 1px;
        background: var(--border-primary);
        margin-bottom: 40px;
    }
    
    .metric-cell {
        background: var(--bg-secondary);
        padding: 24px;
        text-align: center;
    }
    
    .metric-label {
        font-size: 0.6rem;
        color: var(--text-dim);
        letter-spacing: 0.2em;
        text-transform: uppercase;
        margin-bottom: 8px;
    }
    
    .metric-value {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 1.4rem;
        font-weight: 600;
        color: var(--text-primary);
    }
    
    .metric-delta {
        font-size: 0.7rem;
        color: var(--success);
        margin-top: 4px;
    }
    
    .report-section {
        background: var(--bg-tertiary);
        border: 1px solid var(--border-primary);
        padding: 32px;
        margin-bottom: 32px;
    }
    
    .report-title {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 1rem;
        font-weight: 600;
        color: var(--text-secondary);
        letter-spacing: 0.1em;
        text-transform: uppercase;
        margin-bottom: 20px;
        padding-bottom: 12px;
        border-bottom: 1px solid var(--border-primary);
    }
    
    .report-content {
        font-size: 0.85rem;
        color: var(--text-secondary);
        line-height: 1.8;
    }
    
    .chart-container {
        background: var(--bg-tertiary);
        border: 1px solid var(--border-primary);
        padding: 24px;
        margin-bottom: 24px;
    }
    
    .chart-title {
        font-size: 0.6rem;
        color: var(--text-dim);
        letter-spacing: 0.15em;
        text-transform: uppercase;
        margin-bottom: 16px;
    }
    
    .action-btn {
        background: transparent !important;
        border: 1px solid var(--border-primary) !important;
        border-radius: 0 !important;
        color: var(--text-secondary) !important;
        font-family: 'Space Grotesk', sans-serif !important;
        font-weight: 500 !important;
        font-size: 0.7rem !important;
        letter-spacing: 0.15em !important;
        padding: 16px 24px !important;
        text-transform: uppercase;
        transition: all 0.3s ease !important;
    }
    
    .action-btn:hover {
        border-color: var(--accent) !important;
        color: var(--text-primary) !important;
    }
    
    .error-msg {
        background: rgba(239, 68, 68, 0.1);
        border: 1px solid rgba(239, 68, 68, 0.3);
        color: #ef4444;
        padding: 16px 24px;
        font-size: 0.8rem;
        margin: 20px 40px;
        text-align: center;
    }
    
    [data-testid="stForm"] {background: transparent !important;}
    [data-testid="stFormSubmitButton"] > button {width: 100%;}
    
    @media (max-width: 768px) {
        .hero-title {font-size: 2rem !important;}
        .metrics-grid {grid-template-columns: repeat(2, 1fr) !important;}
        .agents-container {padding: 0 20px !important;}
    }
</style>
""", unsafe_allow_html=True)


# --- CUSTOM HEADER ---
st.markdown("""
<div class="hero-section">
    <div class="hero-subtitle">Autonomous Equity Research</div>
    <h1 class="hero-title">AI Investment<br><span>Committee</span></h1>
    <div class="hero-line"></div>
</div>
""", unsafe_allow_html=True)


# --- HELPER FUNCTIONS ---
def render_agent_card(placeholder, number, role, name, status="waiting", log="Waiting..."):
    status_text = {
        "waiting": "Waiting...",
        "running": log,
        "complete": "Complete",
        "error": "Error"
    }
    
    progress_html = """
    <div class="agent-progress">
        <div class="agent-progress-bar"></div>
    </div>
    """ if status == "running" else ""
    
    html = f"""
    <div class="agent-card status-{status}">
        <div class="agent-number">{number}</div>
        <div class="agent-name">{name}</div>
        <div class="agent-role">{role}</div>
        <div class="agent-status">
            <div class="status-dot"></div>
            {status_text.get(status, log)}
        </div>
        {progress_html}
    </div>
    """
    placeholder.markdown(html, unsafe_allow_html=True)


def validate_ticker(ticker):
    try:
        info = yf.Ticker(ticker).history(period="1d")
        return not info.empty
    except:
        return False


# --- SESSION STATE ---
if "report_data" not in st.session_state:
    st.session_state.report_data = None


# --- INPUT SECTION ---
with st.container():
    col1, col2, col3 = st.columns([1, 3, 1])
    with col2:
        with st.form("analysis_form", clear_on_submit=True):
            ticker = st.text_input(
                "",
                placeholder="ENTER TICKER SYMBOL (e.g. AAPL)",
                label_visibility="collapsed",
                key="ticker_input"
            )
            submitted = st.form_submit_button("Generate Report", type="primary")


# --- AGENT PIPELINE ---
st.markdown('<div class="agents-container">', unsafe_allow_html=True)
c1, c2, c3 = st.columns(3)
with c1:
    p1 = st.empty()
with c2:
    p2 = st.empty()
with c3:
    p3 = st.empty()

render_agent_card(p1, "01", "Data Acquisition", "The Researcher", "waiting")
render_agent_card(p2, "02", "Quantitative Analysis", "The Analyst", "waiting")
render_agent_card(p3, "03", "Final Synthesis", "The Writer", "waiting")
st.markdown('</div>', unsafe_allow_html=True)


# --- WORKFLOW ---
if submitted and ticker:
    clean_ticker = ticker.upper().strip()
    
    if not validate_ticker(clean_ticker):
        render_agent_card(p1, "01", "Data Acquisition", "The Researcher", "error", f"Invalid ticker: {clean_ticker}")
        st.markdown(f'<div class="error-msg">Ticker "{clean_ticker}" not found. Please verify the symbol.</div>', unsafe_allow_html=True)
        st.stop()
    
    render_agent_card(p1, "01", "Data Acquisition", "The Researcher", "running", "Scanning markets...")
    state = {"ticker": clean_ticker, "messages": []}
    
    final_report = ""
    chart_path = ""
    metrics = {}
    
    try:
        for chunk in app.stream(state, stream_mode="updates"):
            for node, output in chunk.items():
                if node == "researcher":
                    render_agent_card(p1, "01", "Data Acquisition", "The Researcher", "complete")
                    render_agent_card(p2, "02", "Quantitative Analysis", "The Analyst", "running", "Analyzing data...")
                elif node == "analyst":
                    chart_path = output.get("chart_path")
                    metrics = output.get("metrics")
                    render_agent_card(p2, "02", "Quantitative Analysis", "The Analyst", "complete")
                    render_agent_card(p3, "03", "Final Synthesis", "The Writer", "running", "Writing report...")
                elif node == "writer":
                    final_report = output.get("final_report")
                    render_agent_card(p3, "03", "Final Synthesis", "The Writer", "complete", "Report ready")
        
        st.session_state.report_data = {
            "ticker": clean_ticker,
            "report": final_report,
            "chart": chart_path,
            "metrics": metrics
        }
    
    except Exception as e:
        error_msg = str(e).lower()
        if "rate limit" in error_msg:
            render_agent_card(p3, "03", "Final Synthesis", "The Writer", "error", "Rate limited")
            st.markdown('<div class="error-msg">Rate limit reached. Please wait 30 seconds and try again.</div>', unsafe_allow_html=True)
        else:
            render_agent_card(p3, "03", "Final Synthesis", "The Writer", "error", "Error occurred")
            st.markdown(f'<div class="error-msg">Error: {str(e)}</div>', unsafe_allow_html=True)
        st.stop()


# --- RESULTS ---
if st.session_state.report_data:
    data = st.session_state.report_data
    
    render_agent_card(p1, "01", "Data Acquisition", "The Researcher", "complete")
    render_agent_card(p2, "02", "Quantitative Analysis", "The Analyst", "complete")
    render_agent_card(p3, "03", "Final Synthesis", "The Writer", "complete")
    
    st.markdown(f"""
    <div class="results-section">
        <h2 class="results-header">{data['ticker']} <span>Analysis Report</span></h2>
    """, unsafe_allow_html=True)
    
    # Metrics
    if data["metrics"]:
        m = data["metrics"]
        st.markdown(f"""
        <div class="metrics-grid">
            <div class="metric-cell">
                <div class="metric-label">Current Price</div>
                <div class="metric-value">{m.get('current_price', 'N/A')}</div>
                <div class="metric-delta">{m.get('change', '')}</div>
            </div>
            <div class="metric-cell">
                <div class="metric-label">Daily Change</div>
                <div class="metric-value">{m.get('pct_change', 'N/A')}</div>
            </div>
            <div class="metric-cell">
                <div class="metric-label">Volume</div>
                <div class="metric-value">{m.get('volume', 'N/A')}</div>
            </div>
            <div class="metric-cell">
                <div class="metric-label">AI Signal</div>
                <div class="metric-value">{m.get('signal', 'NEUTRAL')}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Report & Chart
    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown(f"""
        <div class="report-section">
            <div class="report-title">Investment Thesis</div>
            <div class="report-content">{data['report']}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        if data["chart"] and os.path.exists(data["chart"]):
            st.markdown('<div class="chart-container"><div class="chart-title">Technical Analysis</div>', unsafe_allow_html=True)
            st.image(data["chart"], use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        # PDF Download
        pdf_name = f"{data['ticker']}_Report.pdf"
        create_pdf(data['ticker'], data['report'], pdf_name, data['chart'])
        
        with open(pdf_name, "rb") as f:
            st.download_button(
                label="Download PDF",
                data=f,
                file_name=pdf_name,
                mime="application/pdf",
                type="primary",
                use_container_width=True
            )
        
        if st.button("New Analysis", type="secondary", use_container_width=True):
            st.session_state.report_data = None
            st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)
