# StefanCryptoTradingBot

StefanCryptoTradingBot is an automated trading bot built for trading in cryptocurrency market on the Binance exchange, designed to operate using scalping, swing and day trading strategies. The bot integrates advanced technical indicators, real-time performance monitoring, and dynamic parameter adjustments to improve trading efficiency. 

The bot utilizes machine learning through the [MariolaMLCryptoTradingUtils](https://github.com/PedroPLCode/MariolaMLCryptoTradingUtils) module to improve the prediction of future prices, providing a significant edge in the market.

The bot provides an easy-to-use interface for starting and stopping the bot, real-time trade and balance monitoring, technical analysis panel, daily report emails and backtesting features. User can access a control panel to manage bot operations, and an admin panel for modifying key settings and strategies.

## Features

- Many independent bots with different currencies and strategies.
- Automated Trading: Executes trades on Binance based on predefined strategies, including machine learning models (RandomForestRegressor, XGBoostRegressor and LSTM) for improved predictions.
- Binance API Integration: Fetches real-time data and executes trades.
- Real-Time Monitoring: Displays current trade results, account balances, current technical analysis and historical data.
- Control & Admin Panel: Includes user access to a control panel for starting/stopping the bot, and an admin panel for changing settings, configurations and strategies.
- Email Reporting: Sends daily logs and performance reports summarizing the bot's activities over the past 24 hours / 7 days.
- Backtesting features to allow users to test their strategies against historical data.

## Installation

To install and set up the bot locally, follow these steps:

1. Clone the repository:
```bash
git clone https://github.com/yourusername/StefanCryptoTradingBot.git
cd StefanCryptoTradingBot
```

2. Set up a Python virtual environment and activate it:
```bash
python3 -m venv venv
source venv/bin/activate or . venv/bin/activate
```

3. Install the required dependencies:
```bash
pip install -r requirements.txt
```

4. Configure your environment variables by creating a .env file with your Binance API credentials, database URL, and email configuration.
```bash
APP_SECRET_KEY = 'your_turbo_secret_key'
CSRF_SECRET_KEY = 'your_total_secret_key'
GMAIL_USERNAME = 'gmail@username.com'
GMAIL_APP_PASSWORD="gmail_app_password"
RECAPTCHA_PUBLIC_KEY = "recaptcha_public_key"
RECAPTCHA_PRIVATE_KEY = "recaptcha_private_key"
BINANCE_GENERAL_API_KEY='binance_general_api_key'
BINANCE_GENERAL_API_SECRET='binance_general_api_secret'
BINANCE_BOT1_API_KEY='binance_bot1_api_key'
BINANCE_BOT1_API_SECRET='binance_bot1_api_secret'
BINANCE_BOT2_API_KEY='binance_bot2_api_key'
BINANCE_BOT2_API_SECRET='binance_bot2_api_secret'
BINANCE_BOT3_API_KEY='binance_bot3_api_key'
BINANCE_BOT3_API_SECRET='binance_bot3_api_secret'
etc
```

5. Set up the database:
```bash
flask db init
flask db migrate
flask db upgrade
```

6. Copy the previously prepared ML models to the app/mariola/models/ directory.

7. Run tests:
```bash
pytest
```

8. Run the Flask application:
```bash
flask run -h 0.0.0.0 -p 8000
```
or
```bash
gunicorn -c gunicorn_config.py wsgi:app
```

9. Tweak, pimp, improve and have fun.

## Usage

### Once the bot is running, you can access the web interface to:
- Start and Stop the Bot: Control the bot’s operation via the control panel.
- Monitor Trading: View live data, including account balances, technical analysis indicators and trade performance.
- Adjust parameters, settings and strategy via admin panel.
- Receive Reports: Check daily logs and performance reports sent to your email.
- Backtest your strategy and algorithms on historical data.

### Example Commands:
- To start seleted bot, access the control panel and click "Start Bot."
- To stop seleted bot, access the control panel and click "Stop Bot."
- You can start or stop all bots in same time, using "Start/Stop All Bots."

### Testing
- The project includes a test suite that can be executed using pytest. To run the tests, simply use:
pytest

## Technologies Used
- **Python**: The primary language used for development.
- **Flask**: A web framework used for building the application interface.
- **Flask-SQLAlchemy**: ORM used to manage the database.
- **Flask-JWT-Extended**: JWT-based authentication for securing user access.
- **Flask-Mail**: For sending email reports.
- **Binance API**: For fetching market data and executing trades.
- **NumPy, Pandas and TALib**: Libraries used for implementing trading algorithms and data processing.
- **Scikit-Learn, XGBoost and Keras**: A machine learning frameworks used for predictions and forecasting market trends.

## Current Status
**Ongoing Development**

## Future Plans
- Strategy Optimization: Enhancing strategies and trading logic.
- Machine Learning: Incorporating machine learning to improve trade predictions and make the bot more adaptive. That's how [MariolaMLCryptoTradingUtils](https://github.com/PedroPLCode/MariolaMLCryptoTradingUtils) was just born. All my effort is now directed toward her development.

## Important! 
Familiarize yourself thoroughly with the source code. Understand its operation. Only then will you be able to customize and adjust scripts to your own needs, preferences, and requirements. Only then will you be able to use it correctly and avoid potential issues. Knowledge of the underlying code is essential for making informed decisions and ensuring the successful implementation of the bot for your specific use case. Make sure to review all components and dependencies before running the scripts.

Code created by me, with no small contribution from Dr. Google and Mr. ChatGPT.
Any comments welcome.

StefanCryptoTradingBot Project is under GNU General Public License Version 3, 29 June 2007