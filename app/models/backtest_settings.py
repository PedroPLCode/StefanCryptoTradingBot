from .. import db


class BacktestSettings(db.Model):
    """
    Represents the configuration settings for a backtest run.

    This class stores the settings for a backtest, such as the start and end dates,
    initial balance, the file path for historical data, and the bot associated with 
    the backtest. It is used to manage and retrieve the settings for backtesting 
    a trading strategy.

    Attributes:
        id (int): The unique identifier for the backtest settings.
        bot_id (int): The ID of the bot for which the backtest settings are configured.
        start_date (str): The start date of the backtest in string format.
        end_date (str): The end date of the backtest in string format.
        csv_file_path (str): The file path to the CSV file containing historical data for the backtest.
        initial_balance (float): The initial balance to use at the start of the backtest.
        crypto_balance (float): The cryptocurrency balance to use at the start of the backtest (nullable).
    """

    __tablename__ = 'backtest_settings'

    id = db.Column(db.Integer, primary_key=True)
    bot_id = db.Column(db.Integer, default=1, nullable=False)
    start_date = db.Column(db.String(16), default="1 Jan 2023", nullable=False)
    end_date = db.Column(db.String(16), default="31 Jan 2023", nullable=False)
    csv_file_path = db.Column(
        db.String(64), default="backtest_historical_data.csv", nullable=False)
    initial_balance = db.Column(db.Float, default=10.0, nullable=False)
    crypto_balance = db.Column(db.Float, default=0.0, nullable=True)
