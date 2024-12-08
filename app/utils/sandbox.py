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

print(f'initial_amount:\t{initial_amount}\n'
      f'step_size:\t{step_size:.8f}\n'
      f'rounded_result:\t{rounded_result}\n'
      f'rest_amount:\t{rest_amount:.8f}')