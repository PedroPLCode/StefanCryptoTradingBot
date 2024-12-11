from decimal import Decimal

def round_down_to_step_size(amount, step_size):
    if step_size > 0:
        amount_decimal = Decimal(str(amount))
        step_size_decimal = Decimal(str(step_size))
        rounded_amount = (amount_decimal // step_size_decimal) * step_size_decimal
        return float(rounded_amount)
    return float(amount)


def calculate_take_profit(current_price, take_profit_pct):
    current_price = float(current_price)
    take_profit_price = current_price + (current_price * (take_profit_pct))
    return take_profit_price


def calculate_atr_take_profit(current_price, atr, take_profit_atr_calc):
    take_profit_price = current_price + (atr * take_profit_atr_calc)
    return take_profit_price


initial_amount = 0.01234838
step_size = 1e-05
rounded_result = round_down_to_step_size(initial_amount, step_size)
rest_amount = initial_amount - rounded_result
print(f'\ninitial_amount:\t{initial_amount}\n'
      f'step_size:\t{step_size:.8f}\n'
      f'rounded_result:\t{rounded_result}\n'
      f'rest_amount:\t{rest_amount:.8f}')


stablecoin_balance = 11.12
price = 102346.8
step_size = 1e-05
affordable_amount = (stablecoin_balance * 0.95) / price
amount_to_buy = float(round_down_to_step_size(affordable_amount, step_size))
print(f'\nstablecoin_balance:\t{stablecoin_balance}\n'
      f'price:\t{price}\n'
      f'step_size:\t{step_size:.8f}\n'
      f'affordable_amount:\t{affordable_amount}\n'
      f'amount_to_buy:\t{amount_to_buy}\n')


take_profit_price = calculate_take_profit(100, 0.33)
atr_take_profit_price = calculate_atr_take_profit(100, 2, 0.5)
print(f'take_profit_price: {take_profit_price}')
print(f'atr_take_profit_price: {atr_take_profit_price}')