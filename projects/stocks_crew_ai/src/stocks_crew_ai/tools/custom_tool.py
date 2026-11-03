import yfinance as yf


def get_stock_data(ticker_sybmol: str) -> str:
    """Get current price and recent news for a given stock ticker symbol."""
    stock = yf.Ticker(ticker_sybmol)

    info = stock.info

    current_price = info.get("currentPrice", "N/A")
    previous_close = info.get("previousClose", "N/A")

    if current_price != "N/A" and previous_close != "N/A":
        percentage_change = ((current_price - previous_close) / previous_close) * 100
        price_info = f"Price {current_price:.2f} ({percentage_change:+.2f})"
    else:
        price_info = "No price info available"

    news = stock.news

    headlines = []

    for news_item in news[:8]:
        title = news_item["content"].get("title", "").strip()

        if title:
            headlines.append(f"- {title}")

    if not headlines:
        headlines = ["- No headlines available."]

    news_text = "\n".join(headlines)

    return f"{price_info}\n\nRecent News:\n{news_text}"
