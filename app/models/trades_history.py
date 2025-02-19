from .. import db


class TradesHistory(db.Model):
    """
    Represents a historical trade record in the system.

    Attributes:
        id (int): The unique identifier for the trade record.
        trade_id (int, optional): The identifier of the trade (default: 0).
        strategy (str, optional): The trading strategy used (default: "undefined").
        amount (float, optional): The amount of the asset traded (default: 0).
        buy_price (float, optional): The price at which the asset was bought (default: 0).
        sell_price (float, optional): The price at which the asset was sold (default: 0).
        stablecoin_balance (float, optional): The balance of stablecoin after the trade (default: 0).
        stop_loss_price (float, optional): The stop-loss price set for the trade (default: 0).
        take_profit_price (float, optional): The take-profit price set for the trade (default: 0).
        price_rises_counter (int, optional): The number of price increases tracked (default: 0).
        stop_loss_activated (bool): Indicates if the stop-loss was triggered (default: False).
        take_profit_activated (bool): Indicates if the take-profit was triggered (default: False).
        trailing_take_profit_activated (bool): Indicates if the trailing take-profit was triggered (default: False).
        buy_timestamp (datetime, optional): The timestamp when the asset was bought (default: current timestamp).
        sell_timestamp (datetime, optional): The timestamp when the asset was sold (default: current timestamp).
        bot_id (int): The foreign key referencing the bot settings.

    Methods:
        __repr__(): Returns a string representation of the trade history object.
    """

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
    take_profit_activated = db.Column(
        db.Boolean, default=False, nullable=False)
    trailing_take_profit_activated = db.Column(
        db.Boolean, default=False, nullable=False)
    buy_timestamp = db.Column(
        db.DateTime, default=db.func.current_timestamp(), nullable=True)
    sell_timestamp = db.Column(
        db.DateTime, default=db.func.current_timestamp(), nullable=True)

    bot_id = db.Column(db.Integer, db.ForeignKey(
        'bot_settings.id'), nullable=False)

    def __repr__(self):
        """Returns a string representation of the trade history object."""
        return (
            f'id: {self.id}, amount: {self.amount}\n'
            f'buy_price: {self.buy_price}, sell_price: {self.sell_price}\n'
            f'buy_timestamp: {self.buy_timestamp}, '
            f'sell_timestamp: {self.sell_timestamp}, '
            f'bot_id: {self.bot_id}>'
        )
