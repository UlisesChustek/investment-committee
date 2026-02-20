# src/tools/financial_tools.py
import yfinance as yf

def get_stock_prices(ticker: str):
    """
    Retrieves historical stock prices for the last month for a given ticker (e.g., AAPL, MELI).
    Returns a summary string of closing prices.
    """
    try:
        stock = yf.Ticker(ticker)
        # Fetch 1 month of history
        hist = stock.history(period="1mo")
        
        if hist.empty:
            return f"Error: No data found for ticker {ticker}."
        
        # Return formatted string (LLMs read text better than raw dataframe objects)
        return hist['Close'].to_string()
    except Exception as e:
        return f"Error fetching data: {str(e)}"

def get_company_info(ticker: str):
    """
    Retrieves the company profile, sector, and business summary.
    """
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        
        # We extract only the relevant parts to save tokens
        return (
            f"Company: {info.get('longName', 'N/A')}\n"
            f"Sector: {info.get('sector', 'N/A')}\n"
            f"Summary: {info.get('longBusinessSummary', 'N/A')}"
        )
    except Exception as e:
        return f"Error fetching info: {str(e)}"