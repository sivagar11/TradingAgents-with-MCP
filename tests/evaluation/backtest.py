#!/usr/bin/env python3
"""
Simple Backtesting Engine for TradingAgents Evaluation

This module simulates trading based on TradingAgents decisions over a time period.
It tracks portfolio value, trades, and generates performance logs.

Purpose: Prove the system works end-to-end as a trading system.
"""

import sys
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Any
import csv

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


class Portfolio:
    """Manages portfolio state during backtesting."""
    
    def __init__(self, initial_capital: float = 10000.0):
        self.initial_capital = initial_capital
        self.cash = initial_capital
        self.shares = 0
        self.history = []  # List of portfolio states
        
    def get_value(self, current_price: float) -> float:
        """Calculate total portfolio value."""
        return self.cash + (self.shares * current_price)
    
    def can_buy(self, price: float, shares: int = 1) -> bool:
        """Check if we have enough cash to buy."""
        return self.cash >= (price * shares)
    
    def can_sell(self) -> bool:
        """Check if we have shares to sell."""
        return self.shares > 0
    
    def buy(self, price: float, shares: int, date: str, reason: str = ""):
        """Execute a buy order."""
        cost = price * shares
        if not self.can_buy(price, shares):
            return False
        
        self.cash -= cost
        self.shares += shares
        
        trade = {
            "date": date,
            "action": "BUY",
            "price": price,
            "shares": shares,
            "cost": cost,
            "cash_after": self.cash,
            "shares_after": self.shares,
            "portfolio_value": self.get_value(price),
            "reason": reason
        }
        self.history.append(trade)
        return True
    
    def sell(self, price: float, shares: int, date: str, reason: str = ""):
        """Execute a sell order."""
        if not self.can_sell():
            return False
        
        # Sell all shares we have
        shares_to_sell = min(shares, self.shares)
        revenue = price * shares_to_sell
        
        self.cash += revenue
        self.shares -= shares_to_sell
        
        trade = {
            "date": date,
            "action": "SELL",
            "price": price,
            "shares": shares_to_sell,
            "revenue": revenue,
            "cash_after": self.cash,
            "shares_after": self.shares,
            "portfolio_value": self.get_value(price),
            "reason": reason
        }
        self.history.append(trade)
        return True
    
    def hold(self, price: float, date: str, reason: str = ""):
        """Record a hold decision."""
        trade = {
            "date": date,
            "action": "HOLD",
            "price": price,
            "shares": 0,
            "cash_after": self.cash,
            "shares_after": self.shares,
            "portfolio_value": self.get_value(price),
            "reason": reason
        }
        self.history.append(trade)
        return True
    
    def get_summary(self) -> Dict[str, Any]:
        """Get portfolio summary statistics."""
        if not self.history:
            return {}
        
        final_value = self.history[-1]["portfolio_value"]
        total_return = ((final_value - self.initial_capital) / self.initial_capital) * 100
        
        trades = [h for h in self.history if h["action"] in ["BUY", "SELL"]]
        
        return {
            "initial_capital": self.initial_capital,
            "final_cash": self.cash,
            "final_shares": self.shares,
            "final_value": final_value,
            "total_return_pct": total_return,
            "total_trades": len(trades),
            "buy_trades": len([t for t in trades if t["action"] == "BUY"]),
            "sell_trades": len([t for t in trades if t["action"] == "SELL"]),
            "hold_decisions": len([h for h in self.history if h["action"] == "HOLD"]),
        }


class Backtester:
    """Simple backtesting engine for TradingAgents."""
    
    def __init__(self, trading_graph, symbol: str, initial_capital: float = 10000.0):
        """
        Initialize backtester.
        
        Args:
            trading_graph: TradingAgentsGraph instance (async)
            symbol: Stock symbol to trade
            initial_capital: Starting capital
        """
        self.graph = trading_graph
        self.symbol = symbol
        self.portfolio = Portfolio(initial_capital)
        self.daily_log = []
    
    async def run_single_day(self, date: str, verbose: bool = True) -> Dict[str, Any]:
        """
        Run trading analysis for a single day.
        
        Args:
            date: Date string in YYYY-MM-DD format
            verbose: Whether to print progress
            
        Returns:
            Dictionary with decision and execution details
        """
        if verbose:
            print(f"\n📅 Running analysis for {self.symbol} on {date}...")
        
        try:
            # Run the trading graph
            trace, decision = await self.graph.propagate(self.symbol, date)
            
            # Extract decision from the decision object
            action = "HOLD"  # Default
            reason = "Analysis completed"
            
            if decision and hasattr(decision, 'final_decision'):
                action = decision.final_decision.upper()
                reason = getattr(decision, 'reasoning', 'Decision made')
            elif decision and hasattr(decision, 'action'):
                action = decision.action.upper()
                reason = getattr(decision, 'reason', 'Decision made')
            elif isinstance(decision, dict):
                action = decision.get('action', 'HOLD').upper()
                reason = decision.get('reason', 'Decision made')
            
            if verbose:
                print(f"   Decision: {action}")
                print(f"   Reason: {reason[:100]}...")
            
            return {
                "date": date,
                "action": action,
                "reason": reason,
                "trace": trace,
                "decision": decision
            }
            
        except Exception as e:
            print(f"   ❌ Error during analysis: {e}")
            return {
                "date": date,
                "action": "HOLD",
                "reason": f"Error: {str(e)}",
                "error": str(e)
            }
    
    async def run_backtest(
        self, 
        start_date: str, 
        end_date: str,
        shares_per_trade: int = 10,
        verbose: bool = True
    ) -> Dict[str, Any]:
        """
        Run backtest over a date range.
        
        Args:
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            shares_per_trade: Number of shares to buy/sell per trade
            verbose: Whether to print progress
            
        Returns:
            Backtest results dictionary
        """
        if verbose:
            print("\n" + "=" * 80)
            print(f"🚀 STARTING BACKTEST: {self.symbol}")
            print("=" * 80)
            print(f"Period: {start_date} to {end_date}")
            print(f"Initial Capital: ${self.portfolio.initial_capital:,.2f}")
            print(f"Shares per trade: {shares_per_trade}")
            print("=" * 80)
        
        # Generate date range (trading days only - Mon-Fri)
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")
        
        current = start
        trading_days = []
        while current <= end:
            # Skip weekends (5=Saturday, 6=Sunday)
            if current.weekday() < 5:
                trading_days.append(current.strftime("%Y-%m-%d"))
            current += timedelta(days=1)
        
        if verbose:
            print(f"\nTotal trading days: {len(trading_days)}")
        
        # Run analysis for each day
        for day_num, date in enumerate(trading_days, 1):
            day_result = await self.run_single_day(date, verbose)
            
            # Get current price (from trace or use a default)
            # In real scenario, we'd fetch actual price data
            # For demo, we'll use a simple simulation
            current_price = self._get_price_for_date(date)
            
            # Execute trade based on decision
            action = day_result["action"]
            reason = day_result["reason"]
            
            if action == "BUY":
                if self.portfolio.can_buy(current_price, shares_per_trade):
                    success = self.portfolio.buy(current_price, shares_per_trade, date, reason)
                    if verbose and success:
                        print(f"   ✅ EXECUTED: Bought {shares_per_trade} shares @ ${current_price:.2f}")
                else:
                    if verbose:
                        print(f"   ⚠️ SKIPPED: Not enough cash to buy")
                    self.portfolio.hold(current_price, date, "Insufficient cash")
                    
            elif action == "SELL":
                if self.portfolio.can_sell():
                    success = self.portfolio.sell(current_price, shares_per_trade, date, reason)
                    if verbose and success:
                        print(f"   ✅ EXECUTED: Sold {self.portfolio.history[-1]['shares']} shares @ ${current_price:.2f}")
                else:
                    if verbose:
                        print(f"   ⚠️ SKIPPED: No shares to sell")
                    self.portfolio.hold(current_price, date, "No shares to sell")
                    
            else:  # HOLD
                self.portfolio.hold(current_price, date, reason)
                if verbose:
                    print(f"   ⏸️ HELD: Portfolio value ${self.portfolio.get_value(current_price):,.2f}")
            
            # Log daily state
            self.daily_log.append({
                "day": day_num,
                "date": date,
                "price": current_price,
                "decision": action,
                "portfolio_value": self.portfolio.get_value(current_price),
                "cash": self.portfolio.cash,
                "shares": self.portfolio.shares
            })
        
        # Generate final summary
        summary = self.portfolio.get_summary()
        
        if verbose:
            print("\n" + "=" * 80)
            print("📊 BACKTEST COMPLETED")
            print("=" * 80)
            print(f"Initial Capital: ${summary['initial_capital']:,.2f}")
            print(f"Final Value: ${summary['final_value']:,.2f}")
            print(f"Total Return: {summary['total_return_pct']:.2f}%")
            print(f"Total Trades: {summary['total_trades']}")
            print(f"  - Buys: {summary['buy_trades']}")
            print(f"  - Sells: {summary['sell_trades']}")
            print(f"  - Holds: {summary['hold_decisions']}")
            print("=" * 80)
        
        return {
            "symbol": self.symbol,
            "start_date": start_date,
            "end_date": end_date,
            "trading_days": len(trading_days),
            "summary": summary,
            "trade_history": self.portfolio.history,
            "daily_log": self.daily_log
        }
    
    def _get_price_for_date(self, date: str) -> float:
        """
        Get stock price for a given date.
        
        In a real implementation, this would fetch actual historical prices.
        For demo purposes, we'll use a simple simulation around a base price.
        """
        # Simple price simulation (in real scenario, fetch from yfinance)
        import random
        base_price = 140.0  # Approximate NVDA price in Nov 2024
        # Add some random variation (-5% to +5%)
        variation = random.uniform(-0.05, 0.05)
        return base_price * (1 + variation)
    
    def save_results(self, output_dir: str, mode: str = ""):
        """
        Save backtest results to files.
        
        Args:
            output_dir: Directory to save results
            mode: Mode identifier (e.g., "direct", "mcp")
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        prefix = f"{mode}_" if mode else ""
        
        # Save trade history
        trade_file = output_path / f"{prefix}trades_{timestamp}.csv"
        with open(trade_file, 'w', newline='') as f:
            if self.portfolio.history:
                writer = csv.DictWriter(f, fieldnames=self.portfolio.history[0].keys())
                writer.writeheader()
                writer.writerows(self.portfolio.history)
        
        # Save daily log
        log_file = output_path / f"{prefix}daily_log_{timestamp}.csv"
        with open(log_file, 'w', newline='') as f:
            if self.daily_log:
                writer = csv.DictWriter(f, fieldnames=self.daily_log[0].keys())
                writer.writeheader()
                writer.writerows(self.daily_log)
        
        # Save summary
        summary_file = output_path / f"{prefix}summary_{timestamp}.txt"
        summary = self.portfolio.get_summary()
        with open(summary_file, 'w') as f:
            f.write(f"Backtest Summary - {mode.upper()} Mode\n")
            f.write("=" * 50 + "\n\n")
            f.write(f"Symbol: {self.symbol}\n")
            f.write(f"Trading Days: {len(self.daily_log)}\n\n")
            for key, value in summary.items():
                f.write(f"{key}: {value}\n")
        
        print(f"\n💾 Results saved to {output_path}/")
        print(f"   - {trade_file.name}")
        print(f"   - {log_file.name}")
        print(f"   - {summary_file.name}")
        
        return {
            "trade_file": str(trade_file),
            "log_file": str(log_file),
            "summary_file": str(summary_file)
        }

