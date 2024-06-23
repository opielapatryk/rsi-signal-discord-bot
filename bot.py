# Built-in modules
import os
import time
from abc import ABC, abstractmethod
import asyncio

# External modules
import discord
import requests
import pandas as pd
from dotenv import load_dotenv
from stockstats import StockDataFrame as Sdf
from apscheduler.schedulers.asyncio import AsyncIOScheduler


class AbstractKlineFetcher(ABC):
    @abstractmethod
    def fetch_klines(self):
        """Abstract method for fetching Kline data."""
        pass


class AbstractRsiCalculator(ABC):
    @abstractmethod
    def calculate_rsi(self, klines):
        """Abstract method for calculating RSI."""
        pass


class AbstractNotifier(ABC):
    @abstractmethod
    async def send_rsi_alert(self, message: str):
        """Abstract method for sending RSI alerts."""
        pass


class AbstractDiscordBot(ABC, discord.Client):
    def __init__(
        self,
        fetcher: AbstractKlineFetcher,
        calculator: AbstractRsiCalculator,
        notifier: AbstractNotifier,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.fetcher = fetcher
        self.calculator = calculator
        self.notifier = notifier

    @abstractmethod
    async def on_ready(self):
        """Abstract method called when the bot is ready."""
        pass

    @abstractmethod
    async def check_rsi_and_notify(self):
        """Abstract method for checking RSI and sending alerts."""
        pass

    @abstractmethod
    async def periodic_rsi_check(self):
        """Abstract method for scheduling periodic RSI checks."""
        pass


class KlineFetcher(AbstractKlineFetcher):
    def __init__(self, symbol="SOLUSDT", interval="60", max_retries=3, retry_after_seconds=60):
        self.symbol = symbol
        self.interval = interval
        self.max_retries = max_retries
        self.retry_after_seconds = retry_after_seconds

    def fetch_klines(self):
        """Fetches Kline data from an API."""
        retries = 0
        while retries < self.max_retries:
            try:
                url = f"https://api-testnet.bybit.com/v5/market/mark-price-kline?category=linear&symbol={self.symbol}&interval={self.interval}"
                response = requests.get(url)
                response.raise_for_status()
                data = response.json()
                return data["result"]
            except requests.exceptions.HTTPError as e:
                if e.response.status_code == 429:
                    print(
                        f"Rate limit exceeded. Retrying after {self.retry_after_seconds} seconds."
                    )
                    time.sleep(self.retry_after_seconds)
                    retries += 1
                else:
                    raise
            except Exception as e:
                print(f"An error occurred: {str(e)}")
                retries += 1
        print("Max retries exceeded. Unable to fetch data.")
        return None


class RsiCalculator(AbstractRsiCalculator):
    def calculate_rsi(self, klines):
        """Calculates RSI (Relative Strength Index) from Kline data."""
        try:
            if "list" in klines:
                klines_list = klines["list"]
                if klines_list:
                    df = pd.DataFrame(
                        klines_list,
                        columns=["timestamp", "open", "high", "low", "close"],
                    )
                    df["close"] = df["close"].astype(float)
                    stock_df = Sdf.retype(df)
                    stock_df.get("rsi_14")
                    rsi_value = stock_df["rsi_14"].iloc[-1]
                    rounded_rsi_value = int(rsi_value)
                    print(f"RSI value: {rounded_rsi_value}", flush=True)

                    return rounded_rsi_value
                else:
                    print("Empty 'list' found in klines")
                    return None
            else:
                print("Invalid klines data format")
                return None
        except Exception as e:
            print(f"An exception occurred in calculate_rsi: {e}")
            return None


class Notifier(AbstractNotifier):
    def __init__(self, client, channel_id):
        self.client = client
        self.channel_id = channel_id

    async def send_rsi_alert(self, message):
        """Sends an RSI alert message to a Discord channel."""
        channel = self.client.get_channel(self.channel_id)
        await channel.send(message)


class DiscordBot(AbstractDiscordBot):
    async def on_ready(self):
        """Called when the Discord bot is ready."""
        print(f"Logged in as {self.user}", flush=True)
        await self.check_rsi_and_notify()
        asyncio.create_task(self.periodic_rsi_check())

    async def check_rsi_and_notify(self):
        """Fetches Kline data, calculates RSI, and sends alerts based on RSI values."""
        klines = self.fetcher.fetch_klines()
        if klines is not None:
            rsi = self.calculator.calculate_rsi(klines)
            if rsi is not None:
                if rsi > 70:
                    await self.notifier.send_rsi_alert(
                        f"RSI is overbought at {rsi}"
                    )
                elif rsi < 30:
                    await self.notifier.send_rsi_alert(
                        f"RSI is oversold at {rsi}"
                    )
            else:
                print("Failed to calculate RSI")
        else:
            print("Failed to fetch klines data")

    async def periodic_rsi_check(self):
        """Sets up a scheduler to periodically check and notify RSI values."""
        scheduler = AsyncIOScheduler()
        scheduler.add_job(self.check_rsi_and_notify, "cron", minute=0)
        scheduler.start()


if __name__ == "__main__":
    # Load environment variables from .env file
    load_dotenv()

    # Initialize instances of fetcher, calculator, notifier, and DiscordBot
    fetcher = KlineFetcher()
    calculator = RsiCalculator()
    intents = discord.Intents.default()
    notifier = Notifier(
        discord.Client(intents=intents), int(os.getenv("CHANNEL_ID"))
    )
    bot = DiscordBot(fetcher, calculator, notifier, intents=intents)

    # Run the Discord bot using the token from environment variables
    bot.run(os.getenv("DISCORD_TOKEN"))
