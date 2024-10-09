from .. import db

class CurrentTrade(db.Model):
    __tablename__ = 'current_trade'
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(16), default="undefined")
    amount = db.Column(db.Float, default=0)
    price = db.Column(db.Float, default=0)
    trailing_stop_loss = db.Column(db.Float, nullable=True)
    
    def __repr__(self):
        return (
            f'<CurrentTrade:\n'
            f'type: {self.type}\n'
            f'amount: {self.amount}\n'
            f'price: {self.price}\n'
            f'trailing_stop_loss: {self.trailing_stop_loss}>'
        )