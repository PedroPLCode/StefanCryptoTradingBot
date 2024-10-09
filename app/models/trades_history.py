from .. import db

class TradesHistory(db.Model):
    __tablename__ = 'trades_history'
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(16), default="undefined")
    amount = db.Column(db.Float, default=0)
    price = db.Column(db.Float, default=0)
    timestamp = db.Column(db.DateTime, default=db.func.current_timestamp())
    
    def __repr__(self):
        return (
            f'<TradesHistory:\n'
            f'id: {self.id}\n'
            f'type: {self.type}\n'
            f'amount: {self.amount}\n'
            f'price: {self.price}>'
            f'timestamp: {self.timestamp}>'
        )