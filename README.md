# Market Monitoring Bot

A Python-based bot to monitor the Nifty Index (^NSEI) and generate BUY/SELL signals using the 21-period Exponential Moving Average (EMA) crossover strategy.

## Features
- Fetches real-time market data using `yfinance`.
- Calculates the 21-period EMA.
- Generates BUY/SELL signals based on EMA crossover.
- Sends signals to AlgoTest for execution.
- Logs all activities for debugging and analysis.

## Requirements
- Python 3.8+
- Libraries: `yfinance`, `pandas`, `numpy`, `requests`, `pytz`

## Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/SKULLNIN/market-monitoring-bot.git
