from decimal import Decimal

def round_down_to_step_size(amount, step_size):
    if step_size > 0:
        amount_decimal = Decimal(str(amount))
        step_size_decimal = Decimal(str(step_size))
        rounded_amount = (amount_decimal // step_size_decimal) * step_size_decimal
        return float(rounded_amount)
    return float(amount)

amount = 0.0001299
step_size = 1e-05
result = round_down_to_step_size(amount, step_size)

print(result)