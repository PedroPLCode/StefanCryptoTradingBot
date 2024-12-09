from decimal import Decimal

def round_down_to_step_size(amount, step_size):
    if step_size > 0:
        amount_decimal = Decimal(str(amount))
        step_size_decimal = Decimal(str(step_size))
        rounded_amount = (amount_decimal // step_size_decimal) * step_size_decimal
        return float(rounded_amount)
    return float(amount)

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