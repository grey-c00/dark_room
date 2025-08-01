def get_total_base_and_perf(final_cash):
    bonsu_fraction = bonus_percent/ 100
    base = int(final_cash / ( 1 + bonsu_fraction))
    bonus = final_cash - base

    return base, bonus


def get_per_month_pf_and_basic_and_hra(base_pay):
    base_to_basic_fraction = base_to_basic_percent/100
    pf_fraction = pf_percent/100

    cash_base_pay = (base_pay/(1+ base_to_basic_fraction * pf_fraction))

    per_month_pay = cash_base_pay//12
    basic_pay = int(per_month_pay * base_to_basic_fraction)
    hra = int(basic_pay * 0.4)
    pf = int(basic_pay * pf_fraction)

    special_allowance = per_month_pay - (basic_pay + hra)

    return per_month_pay, basic_pay, hra, pf, special_allowance


def get_components(final_cash):
    base, bonus = get_total_base_and_perf(final_cash)

    print(f"base: {base}, bonus: {bonus}")

    per_month_pay, basic_pay, hra, pf, special_allowance = get_per_month_pf_and_basic_and_hra(base)

    lta = 3750

    special_allowance = special_allowance - lta

    # adjusted_bonus = bonus + (base - (basic_pay + hra + 2*pf + special_allowance + lta)*12)

    return {
        "total": final_cash,
        "base": base,
        "direct_paid_base": per_month_pay*12,
        "bonus": bonus,
        "per_month_pay": per_month_pay,
        "basic_pay": basic_pay,
        "hra": hra,
        "pf": pf,
        "special_allowance": special_allowance,
        "lta": lta
    }


bonus_percent = 10
base_to_basic_percent = 50.6
pf_percent = 12

final_cash = 3455885

val = get_components(final_cash)

print("Res: ")
print(val)