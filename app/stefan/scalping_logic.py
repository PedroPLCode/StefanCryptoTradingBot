import talib

def check_scalping_buy_signal(df, bot_settings):
    latest_data = df.iloc[-1]
    mfi = talib.MFI(df['high'], df['low'], df['close'], df['volume'], timeperiod=bot_settings.timeperiod)

    if (latest_data['rsi'] < bot_settings.rsi_buy and
        latest_data['macd'] < latest_data['macd_signal'] and
        latest_data['cci'] < bot_settings.cci_buy and
        mfi.iloc[-1] < bot_settings.mfi_buy and
        latest_data['close'] < latest_data['lower_band']):
        return True
    return False


def check_scalping_sell_signal(df, bot_settings):
    latest_data = df.iloc[-1]
    mfi = talib.MFI(df['high'], df['low'], df['close'], df['volume'], timeperiod=bot_settings.timeperiod)

    if (latest_data['rsi'] > bot_settings.rsi_sell and
        latest_data['macd'] > latest_data['macd_signal'] and
        latest_data['cci'] > bot_settings.cci_sell and
        mfi.iloc[-1] > bot_settings.mfi_sell and
        latest_data['close'] > latest_data['upper_band']):
        return True
    return False