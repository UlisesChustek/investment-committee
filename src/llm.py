# src/llm.py
import os
from dotenv import load_dotenv
from groq import Groq

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

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0  # We want precise data, not creativity
    )
    
    return response.choices[0].message.content