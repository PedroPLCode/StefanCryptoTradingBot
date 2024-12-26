from .. import db

class TradesHistory(db.Model):
    __tablename__ = 'trades_history'
    id = db.Column(db.Integer, primary_key=True)
    trade_id = db.Column(db.Integer, default=0, nullable=True)
    strategy = db.Column(db.String(16), default="undefined", nullable=True)
    amount = db.Column(db.Float, default=0, nullable=True)
    buy_price = db.Column(db.Float, default=0, nullable=True)
    sell_price = db.Column(db.Float, default=0, nullable=True)
    stablecoin_balance = db.Column(db.Float, default=0, nullable=True)
    stop_loss_price = db.Column(db.Float, default=0, nullable=True)
    take_profit_price = db.Column(db.Float, default=0, nullable=True)
    price_rises_counter = db.Column(db.Integer, default=0, nullable=True)
    stop_loss_activated = db.Column(db.Boolean, default=False, nullable=False)
    take_profit_activated = db.Column(db.Boolean, default=False, nullable=False)
    trailing_take_profit_activated = db.Column(db.Boolean, default=False, nullable=False)
    buy_timestamp = db.Column(db.DateTime, default=db.func.current_timestamp(), nullable=True)
    sell_timestamp = db.Column(db.DateTime, default=db.func.current_timestamp(), nullable=True)
    
    bot_id = db.Column(db.Integer, db.ForeignKey('bot_settings.id'), nullable=False)
    
    def __repr__(self):
        return (
            f'id: {self.id}, amount: {self.amount}\n'
            f'buy_price: {self.buy_price}, sell_price: {self.sell_price}\n'
            f'buy_timestamp: {self.buy_timestamp}, '
            f'sell_timestamp: {self.sell_timestamp}, '
            f'bot_id: {self.bot_id}>'
        )