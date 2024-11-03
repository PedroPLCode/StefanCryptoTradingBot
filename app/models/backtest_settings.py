from .. import db

class BacktestSettings(db.Model):
    __tablename__ = 'backtest_settings'
    id = db.Column(db.Integer, primary_key=True)
    bot_id = db.Column(db.Integer, default=1, nullable=False)
    start_date = db.Column(db.String(16), default="1 Jan 2023", nullable=False)
    end_date = db.Column(db.String(16), default="31 Jan 2023", nullable=False)
    csv_file_path = db.Column(db.String(64), default="backtest_historical_data.csv", nullable=False)
    initial_balance = db.Column(db.Float, default=10.0, nullable=False)
    crypto_balance = db.Column(db.Float, default=0.0, nullable=True)