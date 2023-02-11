def show_money(cost: int) -> str:
    if cost < 0:
        sign = "-"
        cost = -cost
    else:
        sign = ""
    higher = str(cost // 100)
    lower = str(cost % 100)
    if len(lower) == 1:
        lower = "0" + lower
    return sign + higher + "." + lower
