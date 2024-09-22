import unittest
from app.trading_bot import execute_trade

class TestTradingBot(unittest.TestCase):
    def test_execute_trade_buy(self):
        # Mock strategy and price data here
        decision, amount, price = execute_trade('buy_low_sell_high')
        self.assertEqual(decision, 'buy')

    def test_execute_trade_sell(self):
        # Test for sell scenario
        decision, amount, price = execute_trade('buy_low_sell_high')
        self.assertEqual(decision, 'sell')

if __name__ == '__main__':
    unittest.main()