import pandas as pd
import numpy as np
import yfinance as yf
import datetime
import time
import requests
import os
from datetime import timedelta
import pytz

# AlgoTest API details
API_URL = "https://algotest.in/api/webhook/custom/execution/start/6799d59c299cc899758a5451"
ACCESS_TOKEN = "uyR9l9rU3qExV5coGgutq7JK2zCrs6Fl"
ALERT_NAME = "test"


# Convert UTC to IST
def utc_to_ist(utc_time):
    ist_offset = timedelta(hours=5, minutes=30)
    ist_time = utc_time + ist_offset
    return ist_time


# Log function to write to the log file and print to the console
def log_message(message):
    folder_path = os.path.expanduser("~/Desktop/AlogTest")
    os.makedirs(folder_path, exist_ok=True)

    log_file_name = f"AlogTestLog_{datetime.datetime.now().strftime('%Y-%m-%d')}.txt"
    log_file_path = os.path.join(folder_path, log_file_name)

    utc_time = datetime.datetime.now(pytz.utc)
    ist_time = utc_to_ist(utc_time)
    timestamp = ist_time.strftime('%Y-%m-%d %H:%M:%S IST')

    log_entry = f"[{timestamp}] {message}"
    print(log_entry)
    with open(log_file_path, "a") as log_file:
        log_file.write(log_entry + "\n")


# Calculate EMA
def calculate_ema(data, period=21):
    ema = data['Close'].ewm(span=period, adjust=False).mean()
    log_message(f"Calculated EMA for period {period}. Latest EMA: {ema.iloc[-1]}")
    return ema


# Send signal to AlgoTest
def send_signal(signal, price):
    payload = {
        "access_token": ACCESS_TOKEN,
        "alert_name": ALERT_NAME,
        "signal": signal,
        "price": price,
        "time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    try:
        response = requests.post(API_URL, json=payload, timeout=10)
        response.raise_for_status()
        log_message(f"Signal sent: {signal} at price {price}. Response: {response.status_code}, {response.text}")
        return response.status_code, response.text
    except requests.exceptions.RequestException as e:
        log_message(f"Error sending signal: {e}")
        return None, str(e)


# Main function
def monitor_market():
    ticker = "^NSEI"  # Nifty index
    interval = "5m"  # 5-minute candles
    start_time = datetime.time(9, 15)
    end_time = datetime.time(15, 15)

    while True:
        now = datetime.datetime.now()
        if now.time() < start_time or now.time() > end_time:
            log_message("Market is closed. Waiting for the next trading day.")
            time.sleep(60)
            continue

        log_message("Fetching market data...")
        try:
            data = yf.download(ticker, period="5d", interval=interval)
        except Exception as e:
            log_message(f"Error fetching data: {e}")
            time.sleep(60)
            continue

        if data.empty:
            log_message("No data fetched. Retrying...")
            time.sleep(60)
            continue

        log_message(f"Fetched data (last 5 rows):\n{data.tail(5)}")

        if len(data) < 21:
            log_message("Not enough data to calculate EMA. Retrying...")
            time.sleep(60)
            continue

        log_message("Calculating EMA...")
        ema_21 = calculate_ema(data)

        data.columns = ['_'.join(col) if isinstance(col, tuple) else col for col in data.columns]
        data['EMA_21'] = ema_21
        data = data.dropna(subset=["EMA_21"])

        if len(data) < 2:
            log_message("Not enough data for analysis after dropping NaN values. Retrying...")
            time.sleep(60)
            continue

        previous_data = data.iloc[-2]
        current_data = data.iloc[-1]
        previous_close = previous_data["Close_^NSEI"]
        previous_ema_21 = previous_data["EMA_21"]
        current_close = current_data["Close_^NSEI"]
        current_ema_21 = current_data["EMA_21"]

        log_message(f"Previous Candle Data: {previous_data.to_dict()}")
        log_message(f"Current Candle Data: {current_data.to_dict()}")

        if previous_close > previous_ema_21 and current_close < current_ema_21:
            log_message("Signal generated: Previous candle crossed below EMA_21")
            send_signal("SELL CALL", current_close)
        elif previous_close < previous_ema_21 and current_close > current_ema_21:
            log_message("Signal generated: Previous candle crossed above EMA_21")
            send_signal("BUY CALL", current_close)

        time.sleep(300 - now.second - now.microsecond / 1e6)


if __name__ == "__main__":
    try:
        monitor_market()
    except KeyboardInterrupt:
        log_message("Script stopped by user.")