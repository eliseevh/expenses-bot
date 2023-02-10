def show_money(cost: int) -> str:
    higher = str(cost // 100)
    lower = str(cost % 100)
    if len(lower) == 1:
        lower = "0" + lower
    return higher + "." + lower
