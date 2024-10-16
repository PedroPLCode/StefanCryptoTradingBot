from .. import db

class BotCurrentTrade(db.Model):
    __tablename__ = 'bot_current_trade'
    id = db.Column(db.Integer, primary_key=True)
    is_active = db.Column(db.Boolean, nullable=False, default=False)
    type = db.Column(db.String(16), default="undefined", nullable=True)
    amount = db.Column(db.Float, default=0, nullable=True)
    buy_price = db.Column(db.Float, default=0, nullable=True)
    price = db.Column(db.Float, default=0, nullable=True)
    previous_price = db.Column(db.Float, default=0, nullable=True)
    trailing_stop_loss = db.Column(db.Float, default=0, nullable=True)
    
    bot_settings_id = db.Column(db.Integer, db.ForeignKey('bot_settings.id'), nullable=False)
    bot_settings = db.relationship(
        'BotSettings',
        back_populates='bot_current_trade',
        overlaps="bot_current_trade"
    )
    
    def __repr__(self):
        return (f'{self.id} {self.type}')