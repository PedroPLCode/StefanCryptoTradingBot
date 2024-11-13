from .. import db

class TradesHistory(db.Model):
    __tablename__ = 'trades_history'
    id = db.Column(db.Integer, primary_key=True)
    strategy = db.Column(db.String(16), default="undefined")
    amount = db.Column(db.Float, default=0)
    buy_price = db.Column(db.Float, default=0)
    sell_price = db.Column(db.Float, default=0)
    stablecoin_balance = db.Column(db.Float, default=0)
    timestamp = db.Column(db.DateTime, default=db.func.current_timestamp())
    
    bot_id = db.Column(db.Integer, db.ForeignKey('bot_settings.id'), nullable=False)
    
    def __repr__(self):
        return (
            f'id: {self.id}, amount: {self.amount}\n'
            f'buy_price: {self.buy_price}, sell_price: {self.sell_price}\n'
            f'timestamp: {self.timestamp}, bot_id: {self.bot_id}>'
        )