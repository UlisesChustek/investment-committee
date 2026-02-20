# AI Investment Committee

Autonomous multi-agent equity research system that generates professional investment reports with technical analysis and market sentiment evaluation.

## System Architecture

The system implements a sequential pipeline architecture with three specialized agents:

```
Input (Ticker) → Researcher → Analyst → Writer → Output (PDF Report)
```

### Core Components

- **Researcher Agent**: Web scraping via DuckDuckGo for real-time market sentiment and news aggregation
- **Analyst Agent**: Quantitative analysis using `yfinance` for OHLC data extraction and technical indicator calculation (20-day SMA, volume analysis)
- **Writer Agent**: LLM-powered report synthesis using Groq's Llama 3.3 70B model
- **PDF Generator**: Automated document compilation with embedded candlestick charts using FPDF2

### Technology Stack

| Layer | Technology |
|-------|-----------|
| LLM | Groq Cloud (Llama 3.3 70B) |
| Data Sources | yfinance, DuckDuckGo Search |
| Visualization | Matplotlib, mplfinance |
| Document Generation | FPDF2 |
| Web Interface | Streamlit |

## Installation

### Prerequisites

- Python 3.9+
- Groq API Key ([Get one here](https://console.groq.com))

### Setup

1. **Clone repository**
   ```bash
   git clone https://github.com/yourusername/investment-committee.git
   cd investment-committee
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment**
   
   Create `.env` file:
   ```bash
   GROQ_API_KEY=your_api_key_here
   ```

## Usage

### Web Interface (Recommended)

```bash
streamlit run streamlit_app.py
```

Access at `http://localhost:8501`

**Features:**
- Real-time agent status visualization
- Interactive metric dashboard
- Embedded technical charts
- One-click PDF export

### CLI Interface

```bash
python app.py
```

**Workflow:**
1. Enter stock ticker (e.g., `AAPL`, `NVDA`, `TSLA`)
2. System executes analysis pipeline
3. Select save location via file dialog
4. PDF report auto-opens on completion

## Project Structure

```
investment-committee/
├── src/
│   ├── graph.py              # Agent orchestration pipeline
│   ├── llm.py                # Groq API client
│   ├── pdf_generator.py      # Report rendering engine
│   └── tools/
│       └── financial_tools.py # Data extraction utilities
├── app.py                    # CLI entry point
├── streamlit_app.py          # Web UI
├── requirements.txt          # Python dependencies
└── .env                      # API credentials (not tracked)
```

## Dependencies

Core libraries and their purpose:

- `groq` - LLM inference via Groq Cloud API
- `yfinance` - Historical stock data retrieval
- `duckduckgo-search` - Web search for market news
- `mplfinance` - Financial candlestick chart generation
- `fpdf2` - PDF document creation
- `streamlit` - Web application framework
- `python-dotenv` - Environment variable management

## Output Format

Generated reports include:

1. **Executive Summary** - Investment thesis overview
2. **Company Profile** - Sector and business description
3. **Market Analysis** - Sentiment from recent news
4. **Quantitative Data** - Price metrics and technical indicators
5. **Technical Chart** - 30-day candlestick with volume and 20-SMA
6. **Risk Factors** - Identified market risks
7. **Legal Disclaimer** - AI-generated content notice

## API Rate Limits

- **Groq**: 30 requests/minute (free tier)
- **yfinance**: No official limit, respect fair use
- **DuckDuckGo**: Rate-limited by IP, built-in retry logic

## Deployment

### Streamlit Community Cloud

1. Push to GitHub
2. Connect repository at [share.streamlit.io](https://share.streamlit.io)
3. Add `GROQ_API_KEY` to app secrets
4. Deploy

### Docker (Optional)

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["streamlit", "run", "streamlit_app.py"]
```

## License

MIT

## Disclaimer

This tool generates AI-powered research reports for educational purposes only. It does not constitute financial advice. Consult a licensed financial advisor before making investment decisions.
