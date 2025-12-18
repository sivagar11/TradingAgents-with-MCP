"""
DEMO MODE Market Analyst - Optimized for speed
Makes only 1-2 tool calls, generates quick summary
"""

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from tradingagents.agents.utils.agent_utils import get_stock_data, get_indicators


def create_market_analyst_demo(llm):
    def market_analyst_node(state):
        current_date = state["trade_date"]
        ticker = state["company_of_interest"]

        tools = [get_stock_data, get_indicators]

        # DEMO MODE: Ultra-concise prompt, specific indicators only
        system_message = (
            """DEMO MODE - Quick market analysis. 
            
Steps:
1. Call get_stock_data(ticker, start_date, end_date)
2. Call get_indicators ONCE with: ["rsi", "macd", "close_50_sma"] (3 indicators only)

Write a 2-paragraph summary:
- Paragraph 1: Trend (bullish/bearish/neutral) based on 50 SMA
- Paragraph 2: Momentum (RSI) and MACD signal

End with a simple table:
| Indicator | Value | Signal |
|-----------|-------|--------|
| RSI | XX | Overbought/Normal/Oversold |
| MACD | XX | Bullish/Bearish |
| 50 SMA | XX | Above/Below price |

Keep it brief - this is a demo."""
        )

        prompt = ChatPromptTemplate.from_messages([
            (
                "system",
                "You are a market analyst. Use tools efficiently. {system_message}\n"
                "Current date: {current_date}, Ticker: {ticker}",
            ),
            MessagesPlaceholder(variable_name="messages"),
        ])

        prompt = prompt.partial(system_message=system_message)
        prompt = prompt.partial(current_date=current_date)
        prompt = prompt.partial(ticker=ticker)

        chain = prompt | llm.bind_tools(tools)
        result = chain.invoke(state["messages"])

        report = ""
        if len(result.tool_calls) == 0:
            report = result.content
       
        return {
            "messages": [result],
            "market_report": report,
        }

    return market_analyst_node

