Rule-Based Crypto Trading Bot
This repository documents the implementation and evaluation of a rule-based cryptocurrency trading framework developed in Python using the Binance API. The project applies engineering economics principles to optimize Return on Investment (ROI) and risk management.

1. Scope
The evaluation is divided into three distinct phases:

Test Case 1 (Grid Search): A comprehensive scan of historical data to optimize entry and exit rule combinations.

Test Case 2 (Custom Strategy): Design and backtesting of a hybrid strategy combining the Ichimoku Cloud with Market Structure (Trend) analysis.

Test Case 3 (Forward Test): Applying the best-performing rules to recent market data (Oct–Nov 2025) to evaluate real-world viability.

Objective: To identify a trading model that maximizes ROI while minimizing risk through systematic backtesting and optimization.

2. Data and Methodology
2.1 Data Source & Parameters
Source: Binance Historical Data (OHLCV).

Assets: Bitcoin (BTC/USDT) and Ethereum (ETH/USDT).

Timeframes: 1-Hour (1h), 4-Hour (4h), 1-Day (1d).

Backtest Period: January 1, 2022 – November 2025 (Covers the 2022 Bear Market and 2024-2025 Bull Run).

Forward Test Period: October 1, 2025 – November 30, 2025.

Initial Capital: $10,000 (Paper Trading).

Transaction Cost: 0.1% per trade.

2.2 Strategy Logic
The bot operates on a "Long-Only" basis.

Grid Search Phase (Case 1): Utilizes a "Hold-Until-Profit" logic.

Execution: Positions are not closed at a loss; they are held until the price recovers or a specific profitable exit signal is triggered.
