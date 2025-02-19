from .. import db


class BacktestResult(db.Model):
    """
    Represents the result of a backtest run for a trading bot.

    This class stores data related to the outcome of a backtest, including 
    the bot's performance, trading strategy, and trade log. It is used to 
    store and retrieve backtest results from the database.

    Attributes:
        id (int): The unique identifier for the backtest result.
        bot_id (int): The ID of the bot associated with the backtest (nullable).
        symbol (str): The trading symbol (e.g., 'BTCUSDC') used in the backtest (nullable).
        strategy (str): The strategy used for the backtest (nullable).
        start_date (str): The start date of the backtest in string format (nullable).
        end_date (str): The end date of the backtest in string format (nullable).
        initial_balance (float): The initial balance of the bot before starting the backtest (nullable).
        final_balance (float): The final balance of the bot after completing the backtest (nullable).
        profit (float): The profit or loss from the backtest (nullable).
        trade_log (str): The log of trades made during the backtest (nullable).
    """

    __tablename__ = 'backtest_results'

    id = db.Column(db.Integer, primary_key=True)
    bot_id = db.Column(db.Integer, nullable=True)
    symbol = db.Column(db.String(16), nullable=True)
    strategy = db.Column(db.String(16), nullable=True)
    start_date = db.Column(db.String(16), nullable=True)
    end_date = db.Column(db.String(16), nullable=True)
    initial_balance = db.Column(db.Float, nullable=True)
    final_balance = db.Column(db.Float, nullable=True)
    profit = db.Column(db.Float, nullable=True)
    trade_log = db.Column(db.Text, nullable=True)
