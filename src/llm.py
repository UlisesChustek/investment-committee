# src/llm.py
import os
from dotenv import load_dotenv
from groq import Groq
from groq import RateLimitError

# 1. Load environment variables (Local development only)
load_dotenv()

def get_llm_client():
    """
    Initializes and returns the Groq API client.
    """
    api_key = os.getenv("GROQ_API_KEY")
    
    if not api_key:
        raise ValueError("❌ Error: GROQ_API_KEY not found. Please configure your .env file or system secrets.")

    return Groq(api_key=api_key)

def generate_report(ticker: str, data: str, news: str) -> str:
    """
    Generates an investment report using Groq's Llama 3.3 70B model.
    Includes graceful error handling for rate limits and other API errors.
    """
    client = get_llm_client()
    
    prompt = f"""You are a Senior Investment Banker. 
Write a professional equity research report for: {ticker}.

DATA: {data}
NEWS: {news}

Structure using EXACTLY these Markdown headers:
### Executive Summary
### Company Profile
### Market Analysis
### Quantitative Data
### Risk Factors
### Legal Notice"""

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0  # We want precise data, not creativity
        )
        return response.choices[0].message.content
    
    except RateLimitError:
        # Graceful handling for rate limit errors
        error_msg = "⚠️ Alta demanda de tráfico. El sistema ha alcanzado su límite de velocidad (Rate Limit). Por favor espera 30 segundos y vuelve a intentar."
        raise RateLimitError(error_msg)
    
    except Exception as e:
        # Catch any other unexpected errors
        error_msg = f"❌ Error inesperado al generar el reporte: {str(e)}"
        raise Exception(error_msg)