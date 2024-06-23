# Built-in modules
import unittest

# External modules
from bot import KlineFetcher, RsiCalculator


class TestKlineFetcher(unittest.IsolatedAsyncioTestCase):

    async def test_fetch_klines_success(self):
        fetcher = KlineFetcher(symbol="SOLUSDT", interval="60")
        klines = fetcher.fetch_klines()
        self.assertIsNotNone(klines)

    async def test_fetch_klines_failure(self):
        fetcher = KlineFetcher(symbol="INVALID", interval="60")
        klines = fetcher.fetch_klines()
        self.assertDictEqual(klines, {})


class TestRsiCalculator(unittest.TestCase):

    def test_calculate_rsi_success(self):
        klines = {
            "list": [
                {
                    "timestamp": "2024-06-23T12:00:00Z",
                    "open": "100",
                    "high": "110",
                    "low": "90",
                    "close": "105",
                },
                {
                    "timestamp": "2024-06-23T13:00:00Z",
                    "open": "105",
                    "high": "115",
                    "low": "95",
                    "close": "110",
                },
            ]
        }
        calculator = RsiCalculator()
        rsi = calculator.calculate_rsi(klines)
        self.assertIsNotNone(rsi)

    def test_calculate_rsi_empty_klines(self):
        klines = {"list": []}
        calculator = RsiCalculator()
        rsi = calculator.calculate_rsi(klines)
        self.assertIsNone(rsi)


if __name__ == "__main__":
    unittest.main()
