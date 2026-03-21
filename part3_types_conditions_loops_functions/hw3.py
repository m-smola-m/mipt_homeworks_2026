#!/usr/bin/env python

from typing import Any

UNKNOWN_COMMAND_MSG = "Unknown command!"
NONPOSITIVE_VALUE_MSG = "Value must be grater than zero!"
INCORRECT_DATE_MSG = "Invalid date!"
NOT_EXISTS_CATEGORY = "Category not exists!"
OP_SUCCESS_MSG = "Added"

DATE_PARTS_COUNT = 3
MONTHS_IN_YEAR = 12
FEBRUARY = 2

CMD_INCOME_PARTS = 3
CMD_COST_CATEGORIES_PARTS = 2
CMD_COST_PARTS = 4
CMD_STATS_PARTS = 2


EXPENSE_CATEGORIES = {
    "Food": ("Supermarket", "Restaurants", "FastFood", "Coffee", "Delivery"),
    "Transport": ("Taxi", "Public transport", "Gas", "Car service"),
    "Housing": ("Rent", "Utilities", "Repairs", "Furniture"),
    "Health": ("Pharmacy", "Doctors", "Dentist", "Lab tests"),
    "Entertainment": ("Movies", "Concerts", "Games", "Subscriptions"),
    "Clothing": ("Outerwear", "Casual", "Shoes", "Accessories"),
    "Education": ("Courses", "Books", "Tutors"),
    "Communications": ("Mobile", "Internet", "Subscriptions"),
    "Other": ("Other",),
}


financial_transactions_storage: list[dict[str, Any]] = []


def parse_amount(raw_amount: str) -> float | None:
    """Парсит число"""
    normalized = raw_amount.replace(",", ".")
    if not normalized or not normalized.isdigit():
        return None

    return float(normalized)


def _date_leq(a: tuple[int, int, int], b: tuple[int, int, int]) -> bool:
    """True если дата a <= b"""
    ad, am, ay = a
    bd, bm, by = b
    if ay != by:
        return ay < by
    if am != bm:
        return am < bm
    return ad <= bd


def make_up_statistics(report_date: tuple[int, int, int]) -> tuple[float, float, float, dict[str, float]]:
    """Считает капитал на дату, доходы/расходы текущего месяца и детализацию по категориям."""
    _r_day, r_month, r_year = report_date

    total_capital = 0.0
    month_income = 0.0
    month_expenses = 0.0
    categories: dict[str, float] = {}

    for t in financial_transactions_storage:
        if not t:
            continue

        t_date_any = t.get("date")
        if not (
            isinstance(t_date_any, tuple)
            and len(t_date_any) == DATE_PARTS_COUNT
            and all(isinstance(p, int) for p in t_date_any)
        ):
            continue
        t_date = (t_date_any[0], t_date_any[1], t_date_any[2])

        if not _date_leq(t_date, report_date):
            continue

        amount = t.get("amount")
        if not isinstance(amount, (int, float)):
            continue

        is_cost = "category" in t
        if is_cost:
            total_capital -= float(amount)
        else:
            total_capital += float(amount)

        _d, m, y = t_date
        if m == r_month and y == r_year:
            if is_cost:
                month_expenses += float(amount)
                category = t.get("category")
                if isinstance(category, str):
                    categories[category] = categories.get(category, 0.0) + float(amount)
            else:
                month_income += float(amount)

    return total_capital, month_income, month_expenses, categories


def format_stats(report_date_raw: str, stats: tuple[float, float, float, dict[str, float]]) -> str:
    total_capital, month_income, month_expenses, categories = stats
    delta = month_income - month_expenses
    profit_or_loss = "profit" if delta >= 0 else "loss"
    delta_abs = abs(delta)

    lines = []
    lines.append(f"Your statistics as of {report_date_raw}:")
    lines.append(f"Total capital: {total_capital:.2f} rubles")
    lines.append(f"This month, the {profit_or_loss} amounted to {delta_abs:.2f} rubles.")
    lines.append(f"Income: {month_income:.2f} rubles")
    lines.append(f"Expenses: {month_expenses:.2f} rubles")
    lines.append("")
    lines.append("Details (category: amount):")

    if categories:
        for idx, (cat, amt) in enumerate(sorted(categories.items(), key=lambda kv: kv[0]), 1):
            lines.append(f"{idx}. {cat}: {int(amt)}")

    return "\n".join(lines)


def is_leap_year(year: int) -> bool:
    """
    Для заданного года определяет: високосный (True) или невисокосный (False).

    :param int year: Проверяемый год
    :return: Значение високосности.
    :rtype: bool
    """
    return year % 400 == 0 or (year % 4 == 0 and year % 100 != 0)


def extract_date(maybe_dt: str) -> tuple[int, int, int] | None:
    """
    Парсит дату формата DD-MM-YYYY из строки.

    :param str maybe_dt: Проверяемая строка
    :return: tuple формата (день, месяц, год) или None, если дата неправильная.
    :rtype: tuple[int, int, int] | None
    """
    parts = maybe_dt.split("-")
    if len(parts) != DATE_PARTS_COUNT:
        return None

    day_s, month_s, year_s = parts
    if not (day_s.isdigit() and month_s.isdigit() and year_s.isdigit()):
        return None

    day = int(day_s)
    month = int(month_s)
    year = int(year_s)

    if month < 1 or month > MONTHS_IN_YEAR:
        return None

    days_in_month = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    max_day = days_in_month[month - 1]
    if month == FEBRUARY and is_leap_year(year):
        max_day = 29

    if day < 1 or day > max_day:
        return None

    return day, month, year


def income_handler(amount: float, income_date: str) -> str:
    if amount <= 0:
        financial_transactions_storage.append({})
        return NONPOSITIVE_VALUE_MSG

    parsed_date = extract_date(income_date)
    if parsed_date is None:
        financial_transactions_storage.append({})
        return INCORRECT_DATE_MSG

    financial_transactions_storage.append({"amount": amount, "date": parsed_date})
    return OP_SUCCESS_MSG


def cost_handler(category_name: str, amount: float, income_date: str) -> str:
    if amount <= 0:
        financial_transactions_storage.append({})
        return NONPOSITIVE_VALUE_MSG

    parsed_date = extract_date(income_date)
    if parsed_date is None:
        financial_transactions_storage.append({})
        return INCORRECT_DATE_MSG

    if "::" not in category_name:
        financial_transactions_storage.append({})
        return NOT_EXISTS_CATEGORY

    common_category, direct_category = category_name.split("::", 1)
    if common_category not in EXPENSE_CATEGORIES or direct_category not in EXPENSE_CATEGORIES[common_category]:
        financial_transactions_storage.append({})
        return NOT_EXISTS_CATEGORY

    financial_transactions_storage.append({"category": category_name, "amount": amount, "date": parsed_date})
    return OP_SUCCESS_MSG


def cost_categories_handler() -> str:
    return "\n".join(f"{k}::{v}" for k, kv in EXPENSE_CATEGORIES.items() for v in kv)


def stats_handler(report_date: str) -> str:
    parsed = extract_date(report_date)
    if parsed is None:
        return INCORRECT_DATE_MSG

    stats = make_up_statistics(parsed)
    return format_stats(report_date, stats)


def _print_unknown_command() -> None:
    print(UNKNOWN_COMMAND_MSG)


def _handle_income(parts: list[str]) -> None:
    if len(parts) != CMD_INCOME_PARTS:
        _print_unknown_command()
        return

    amount_str, date_str = parts[1], parts[2]
    amount = parse_amount(amount_str)
    if amount is None:
        _print_unknown_command()
        return

    print(income_handler(amount, date_str))


def _handle_cost(parts: list[str]) -> None:
    if len(parts) == CMD_COST_CATEGORIES_PARTS and parts[1] == "categories":
        print(cost_categories_handler())
        return

    if len(parts) != CMD_COST_PARTS:
        _print_unknown_command()
        return

    category, amount_raw, date_raw = parts[1], parts[2], parts[3]

    if (not category) or (" " in category) or not category.isalpha():
        _print_unknown_command()
        return

    amount = parse_amount(amount_raw)
    if amount is None:
        _print_unknown_command()
        return

    result = cost_handler(category, amount, date_raw)
    if result == NOT_EXISTS_CATEGORY:
        print(NOT_EXISTS_CATEGORY)
        print(cost_categories_handler())
        return

    print(result)


def _handle_stats(parts: list[str]) -> None:
    if len(parts) != CMD_STATS_PARTS:
        _print_unknown_command()
        return

    print(stats_handler(parts[1]))


def main() -> None:
    command = input().strip()
    if not command:
        _print_unknown_command()
        return

    parts = command.split()
    if not parts:
        _print_unknown_command()
        return

    cmd = parts[0]
    if cmd == "income":
        _handle_income(parts)
        return

    if cmd == "cost":
        _handle_cost(parts)
        return

    if cmd == "stats":
        _handle_stats(parts)
        return

    _print_unknown_command()


if __name__ == "__main__":
    main()
