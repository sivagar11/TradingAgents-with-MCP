"""
DEMO MODE - Ultra-fast analysts that skip most API calls
For demos where speed > accuracy
"""

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from tradingagents.agents.utils.agent_utils import get_news


def create_social_analyst_demo(llm):
    """Social analyst - skips news API, generates quick summary"""
    def social_analyst_node(state):
        current_date = state["trade_date"]
        ticker = state["company_of_interest"]

        # DEMO: No tools, just generate a plausible summary
        system_message = (
            f"DEMO MODE - Generate a brief 2-paragraph social sentiment summary for {ticker}. "
            "Make reasonable assumptions about public sentiment. Include a simple sentiment table. "
            "Be concise - 150 words max."
        )

        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a sentiment analyst. {system_message}"),
            MessagesPlaceholder(variable_name="messages"),
        ])

        prompt = prompt.partial(system_message=system_message)
        chain = prompt | llm
        result = chain.invoke(state["messages"])

        return {
            "messages": [result],
            "sentiment_report": result.content,
        }

    return social_analyst_node


def create_news_analyst_demo(llm):
    """News analyst - minimal news lookup"""
    def news_analyst_node(state):
        current_date = state["trade_date"]
        ticker = state["company_of_interest"]

        tools = [get_news]

        # DEMO: Call news API once only
        system_message = (
            f"DEMO MODE - Quick news check for {ticker}. "
            "Call get_news() ONCE with query='{ticker}'. "
            "Write 2 paragraphs summarizing key news. Include table. 150 words max."
        )

        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a news analyst. {system_message}"),
            MessagesPlaceholder(variable_name="messages"),
        ])

        prompt = prompt.partial(system_message=system_message)
        chain = prompt | llm.bind_tools(tools)
        result = chain.invoke(state["messages"])

        report = ""
        if len(result.tool_calls) == 0:
            report = result.content

        return {
            "messages": [result],
            "news_report": report,
        }

    return news_analyst_node


def create_fundamentals_analyst_demo(llm):
    """Fundamentals analyst - skips slow API calls, generates summary"""
    def fundamentals_analyst_node(state):
        current_date = state["trade_date"]
        ticker = state["company_of_interest"]

        # DEMO: No tools, generate plausible fundamental summary
        system_message = (
            f"DEMO MODE - Generate a brief fundamental analysis for {ticker}. "
            "Make reasonable assumptions about financials (revenue growth, profitability, etc). "
            "2 paragraphs + simple table. 150 words max. Sound professional but be quick."
        )

        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a fundamentals analyst. {system_message}"),
            MessagesPlaceholder(variable_name="messages"),
        ])

        prompt = prompt.partial(system_message=system_message)
        chain = prompt | llm
        result = chain.invoke(state["messages"])

        return {
            "messages": [result],
            "fundamentals_report": result.content,
        }

    return fundamentals_analyst_node

