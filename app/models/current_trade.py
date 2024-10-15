from .. import db

class CurrentTrade(db.Model):
    __tablename__ = 'current_trade'
    id = db.Column(db.Integer, primary_key=True)
    is_active = db.Column(db.Boolean, nullable=False, default=False)
    type = db.Column(db.String(16), default="undefined", nullable=True)
    amount = db.Column(db.Float, default=0, nullable=True)
    price = db.Column(db.Float, default=0, nullable=True)
    previous_price = db.Column(db.Float, default=0, nullable=True)
    trailing_stop_loss = db.Column(db.Float, default=0, nullable=True)
    
    def __repr__(self):
        return (
            f'<CurrentTrade:\n'
            f'type: {self.type}\n'
            f'amount: {self.amount}\n'
            f'price: {self.price}\n'
            f'trailing_stop_loss: {self.trailing_stop_loss}>'
        )