from .. import db

class BotCurrentTrade(db.Model):
    """
    Represents the current trade being executed by the trading bot.

    This class stores details about the active trade, such as the amount, buy price, 
    current price, stop loss and take profit levels, and whether trailing take profit 
    is activated. It tracks the status of the trade, including whether it is active, 
    and maintains relevant trade data like price fluctuations and timestamps.

    Attributes:
        id (int): The unique identifier for the current trade.
        is_active (bool): A flag indicating whether the trade is currently active.
        amount (float): The amount of the asset being traded.
        buy_price (float): The price at which the asset was bought.
        current_price (float): The current market price of the asset.
        previous_price (float): The previous market price of the asset.
        stop_loss_price (float): The price at which to trigger a stop loss.
        take_profit_price (float): The price at which to take profit.
        use_take_profit (bool): A flag indicating whether take profit is enabled.
        trailing_take_profit_activated (bool): A flag indicating whether trailing take profit is activated.
        price_rises_counter (int): A counter tracking the number of price increases.
        buy_timestamp (datetime): The timestamp of when the asset was bought.
        bot_settings_id (int): The foreign key to the `BotSettings` table, linking the trade to specific bot settings.
        bot_settings (BotSettings): The `BotSettings` object associated with this trade.
    """
    
    __tablename__ = 'bot_current_trade'
    
    id = db.Column(db.Integer, primary_key=True)
    is_active = db.Column(db.Boolean, nullable=False, default=False)
    amount = db.Column(db.Float, default=0, nullable=True)
    buy_price = db.Column(db.Float, default=0, nullable=True)
    current_price = db.Column(db.Float, default=0, nullable=True)
    previous_price = db.Column(db.Float, default=0, nullable=True)
    stop_loss_price = db.Column(db.Float, default=0, nullable=True)
    take_profit_price = db.Column(db.Float, default=0, nullable=True)
    use_take_profit = db.Column(db.Boolean, nullable=False, default=False)
    trailing_take_profit_activated = db.Column(db.Boolean, nullable=False, default=False)
    price_rises_counter = db.Column(db.Integer, default=0, nullable=True)
    buy_timestamp = db.Column(db.DateTime, default=db.func.current_timestamp(), nullable=True)
    
    bot_settings_id = db.Column(db.Integer, db.ForeignKey('bot_settings.id'), nullable=False)
    bot_settings = db.relationship(
        'BotSettings',
        back_populates='bot_current_trade',
        overlaps="bot_current_trade"
    )
    
    def __repr__(self):
        """Return a string representation of the object."""
        return (f'{self.id}')