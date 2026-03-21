#!/usr/bin/env python

from typing import Any

Date = tuple[int, int, int]
State = tuple[float, float, float]
Stats = tuple[float, float, float, dict[str, float]]
MonthlyState = tuple[float, float]

KEY_DATE = "date"
KEY_AMOUNT = "amount"
KEY_CATEGORY = "category"
ZERO = 0

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

DAYS_IN_MONTH = (
    31,
    28,
    31,
    30,
    31,
    30,
    31,
    31,
    30,
    31,
    30,
    31,
)

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
    normalized = raw_amount.replace(",", ".")
    if not normalized.isdigit():
        return None
    return float(normalized)


def _date_key(date: Date) -> tuple[int, int, int]:
    day, month, year = date
    return year, month, day


def _date_leq(date1: Date, date2: Date) -> bool:
    return _date_key(date1) <= _date_key(date2)


def _is_valid_transaction(t: dict[str, Any]) -> bool:
    t_date = t.get(KEY_DATE)
    return (
        isinstance(t_date, tuple)
        and len(t_date) == DATE_PARTS_COUNT
        and all(isinstance(p, int) for p in t_date)
        and isinstance(t.get(KEY_AMOUNT), (int, float))
    )


def _is_same_month(date: Date, report_date: Date) -> bool:
    month, year = date[1], date[2]
    return month == report_date[1] and year == report_date[2]


def _update_category(categories: dict[str, float], category: str, amount: float) -> None:
    categories[category] = categories.get(category, ZERO) + amount


def _apply_monthly(
    t: dict[str, Any],
    amount: float,
    monthly_state: MonthlyState,
    categories: dict[str, float],
    report_date: Date,
) -> MonthlyState:
    month_income, month_expenses = monthly_state
    if not _is_same_month(t[KEY_DATE], report_date):
        return month_income, month_expenses
    if KEY_CATEGORY in t:
        month_expenses += amount
        cat = t.get(KEY_CATEGORY)
        if isinstance(cat, str):
            _update_category(categories, cat, amount)
    else:
        month_income += amount
    return month_income, month_expenses


def _process_transaction(
    t: dict[str, Any],
    report_date: Date,
    state: State,
    categories: dict[str, float],
) -> State:
    total_capital, month_income, month_expenses = state
    amount = float(t[KEY_AMOUNT])
    is_cost = KEY_CATEGORY in t

    if is_cost:
        total_capital -= amount
    else:
        total_capital += amount

    month_income, month_expenses = _apply_monthly(
        t,
        amount,
        (month_income, month_expenses),
        categories,
        report_date,
    )

    return total_capital, month_income, month_expenses


def make_up_statistics(report_date: Date) -> Stats:
    total_capital: float = ZERO
    month_income: float = ZERO
    month_expenses: float = ZERO
    categories: dict[str, float] = {}

    for t in financial_transactions_storage:
        if not t or not _is_valid_transaction(t):
            continue
        if not _date_leq(t[KEY_DATE], report_date):
            continue
        total_capital, month_income, month_expenses = _process_transaction(
            t, report_date, (total_capital, month_income, month_expenses), categories
        )

    return total_capital, month_income, month_expenses, categories


def _format_categories(categories: dict[str, float]) -> list[str]:
    sorted_items = sorted(categories.items(), key=lambda item: item[0])
    lines: list[str] = []
    for index, (cat, amt) in enumerate(sorted_items, 1):
        lines.append(f"{index}. {cat}: {int(amt)}")
    return lines


def _build_stats_lines(
    report_date_raw: str,
    total_capital: float,
    month_income: float,
    month_expenses: float,
    categories: dict[str, float],
) -> list[str]:
    delta = month_income - month_expenses
    profit_or_loss = "profit" if delta >= 0 else "loss"
    lines = [
        f"Your statistics as of {report_date_raw}:",
        f"Total capital: {total_capital:.2f} rubles",
        f"This month, the {profit_or_loss} amounted to {abs(delta):.2f} rubles.",
        f"Income: {month_income:.2f} rubles",
        f"Expenses: {month_expenses:.2f} rubles",
        "",
        "Details (category: amount):",
    ]
    lines.extend(_format_categories(categories))
    return lines


def format_stats(report_date_raw: str, stats: Stats) -> str:
    total_capital, month_income, month_expenses, categories = stats
    return "\n".join(
        _build_stats_lines(report_date_raw, total_capital, month_income, month_expenses, categories)
    )


def is_leap_year(year: int) -> bool:
    divisible_by_four_hundred = year % 400 == 0
    divisible_by_four = year % 4 == 0
    not_divisible_by_hundred = year % 100 != 0
    return divisible_by_four_hundred or (divisible_by_four and not_divisible_by_hundred)


def extract_date(maybe_dt: str) -> Date | None:
    parts = maybe_dt.split("-")
    if len(parts) != DATE_PARTS_COUNT:
        return None
    if not all(part.isdigit() for part in parts):
        return None

    day, month, year = map(int, parts)
    if not (1 <= month <= MONTHS_IN_YEAR):
        return None

    max_day = DAYS_IN_MONTH[month - 1]
    if month == FEBRUARY and is_leap_year(year):
        max_day = 29

    if not (1 <= day <= max_day):
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

    financial_transactions_storage.append({KEY_AMOUNT: amount, KEY_DATE: parsed_date})
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

    financial_transactions_storage.append(
        {KEY_CATEGORY: category_name, KEY_AMOUNT: amount, KEY_DATE: parsed_date}
    )
    return OP_SUCCESS_MSG


def cost_categories_handler() -> str:
    return "\n".join(
        f"{common}::{sub}" for common, subs in EXPENSE_CATEGORIES.items() for sub in subs
    )


def stats_handler(report_date: str) -> str:
    parsed = extract_date(report_date)
    if parsed is None:
        return INCORRECT_DATE_MSG
    return format_stats(report_date, make_up_statistics(parsed))


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


def _parse_cost_parts(parts: list[str]) -> tuple[str, str, str]:
    return parts[1], parts[2], parts[3]


def _handle_cost(parts: list[str]) -> None:
    if len(parts) == CMD_COST_CATEGORIES_PARTS and parts[1] == "categories":
        print(cost_categories_handler())
        return

    if len(parts) != CMD_COST_PARTS:
        _print_unknown_command()
        return

    category, amount_raw, date_raw = _parse_cost_parts(parts)
    if not category or (" " in category) or not category.isalpha():
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
    elif cmd == "cost":
        _handle_cost(parts)
    elif cmd == "stats":
        _handle_stats(parts)
    else:
        _print_unknown_command()


if __name__ == "__main__":
    main()
