from .. import db

class BacktestResult(db.Model):
    __tablename__ = 'backtest_results'
    id = db.Column(db.Integer, primary_key=True)
    bot_id = db.Column(db.Integer, nullable=True)
    start_date = db.Column(db.String(16), nullable=True)
    end_date = db.Column(db.String(16), nullable=True)
    initial_balance = db.Column(db.Float, nullable=True)
    final_balance = db.Column(db.Float, nullable=True)
    profit = db.Column(db.Float, nullable=True)
    trade_log = db.Column(db.Text, nullable=True)