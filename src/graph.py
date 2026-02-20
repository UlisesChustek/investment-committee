# src/graph.py
import os
import mplfinance as mpf
import matplotlib
matplotlib.use('Agg') 
import matplotlib.pyplot as plt
import yfinance as yf
from duckduckgo_search import DDGS

from src.llm import generate_report
from src.tools.financial_tools import get_stock_prices, get_company_info

def researcher_node(ticker: str) -> str:
    """
    Searches for latest news and market sentiment for the given ticker.
    Returns a summary of search results.
    """
    print(f"[RESEARCHER] Searching news for {ticker}...")
    search_query = f"{ticker} stock latest news financial analysis"
    
    try:
        # Use DuckDuckGo search directly
        with DDGS() as ddgs:
            results = list(ddgs.text(search_query, max_results=5))
            news_summary = "\n".join([f"- {r['title']}: {r['body']}" for r in results])
        return news_summary
    except Exception as e:
        print(f"[WARNING] Search error: {e}")
        return f"Unable to fetch news for {ticker}"

def analyst_node(ticker: str) -> dict:
    """
    Generates technical analysis chart and calculates key metrics.
    Returns dict with chart_path, metrics, and financial_data.
    """
    print(f"[ANALYST] Generating Technical Candlestick Chart for {ticker}...")
    
    prices_text = get_stock_prices(ticker)
    info = get_company_info(ticker)
    
    chart_filename = f"{ticker}_chart.png"
    metrics = {}
    
    try:
        data = yf.Ticker(ticker).history(period="1mo")
        if not data.empty:
            # --- 1. CALCULATE METRICS FOR UI ---
            current_price = data['Close'].iloc[-1]
            prev_price = data['Close'].iloc[-2]
            change = current_price - prev_price
            pct_change = (change / prev_price) * 100
            volume = data['Volume'].iloc[-1]
            
            # Simple Technical Signal (Price vs 20-SMA)
            sma_20 = data['Close'].rolling(window=20).mean().iloc[-1]
            signal = "BULLISH" if current_price > sma_20 else "BEARISH"
            
            metrics = {
                "current_price": f"${current_price:.2f}",
                "change": f"{change:.2f}",
                "pct_change": f"{pct_change:.2f}%",
                "volume": f"{volume:,}",
                "signal": signal
            }
            
            # --- 2. GENERATE CHART ---
            # Clean index for mplfinance
            data.index = data.index.tz_localize(None)
            data = data[['Open', 'High', 'Low', 'Close', 'Volume']]
            
            mpf.plot(
                data, 
                type='candle', 
                style='charles',
                title=f"\n{ticker} - Technical Analysis",
                volume=True,
                mav=(20), 
                savefig=chart_filename,
                figsize=(12, 8)
            )
            print(f"[SUCCESS] Technical Chart generated: {chart_filename}")
        else:
            chart_filename = ""
    except Exception as e:
        print(f"[WARNING] Chart Error: {e}")
        chart_filename = ""

    return {
        "financial_data": f"--- INFO ---\n{info}\n\n--- PRICES ---\n{prices_text}",
        "chart_path": chart_filename,
        "metrics": metrics
    }

def writer_node(ticker: str, news: str, data: str) -> str:
    """
    Compiles the final investment report using the LLM.
    Returns the report text.
    """
    print(f"[WRITER] Compiling final report for {ticker}...")
    
    report = generate_report(ticker, data, news)
    return report

def run_analysis(ticker: str) -> dict:
    """
    Main orchestration function that runs the complete analysis pipeline.
    
    Args:
        ticker: Stock ticker symbol (e.g., 'AAPL', 'NVDA')
    
    Returns:
        dict with keys: ticker, final_report, chart_path, metrics
    """
    # Step 1: Research
    news_summary = researcher_node(ticker)
    
    # Step 2: Analysis
    analyst_result = analyst_node(ticker)
    
    # Step 3: Writing
    final_report = writer_node(
        ticker, 
        news_summary, 
        analyst_result["financial_data"]
    )
    
    return {
        "ticker": ticker,
        "final_report": final_report,
        "chart_path": analyst_result["chart_path"],
        "metrics": analyst_result["metrics"]
    }

# Legacy compatibility: create an 'app' object that mimics the old LangGraph interface
class LegacyAppAdapter:
    """Adapter to maintain compatibility with existing code that uses app.stream() or app.invoke()"""
    
    def invoke(self, state: dict) -> dict:
        """Mimics LangGraph's invoke method"""
        ticker = state.get("ticker")
        result = run_analysis(ticker)
        return result
    
    def stream(self, state: dict, stream_mode: str = "updates"):
        """Mimics LangGraph's stream method by yielding node updates"""
        ticker = state.get("ticker")
        
        # Yield researcher update
        news_summary = researcher_node(ticker)
        yield {"researcher": {"news_summary": news_summary}}
        
        # Yield analyst update
        analyst_result = analyst_node(ticker)
        yield {"analyst": analyst_result}
        
        # Yield writer update
        final_report = writer_node(ticker, news_summary, analyst_result["financial_data"])
        yield {"writer": {"final_report": final_report}}

app = LegacyAppAdapter()