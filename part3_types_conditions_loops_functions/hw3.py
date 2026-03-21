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

DAYS_IN_MONTH = (31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31)

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
    if not normalized or not normalized.isdigit():
        return None
    return float(normalized)


def _date_leq(
        date1: tuple[int, int, int],
        date2: tuple[int, int, int],
) -> bool:
    return (date1[2], date1[1], date1[0]) <= (date2[2], date2[1], date2[0])


def _is_valid_transaction(t: dict[str, Any]) -> bool:
    t_date = t.get("date")
    return (
            isinstance(t_date, tuple)
            and len(t_date) == DATE_PARTS_COUNT
            and all(isinstance(p, int) for p in t_date)
            and isinstance(t.get("amount"), (int, float))
    )


def _is_same_month(
        date: tuple[int, int, int],
        report_date: tuple[int, int, int],
) -> bool:
    return date[1] == report_date[1] and date[2] == report_date[2]


def _update_category(
        categories: dict[str, float],
        category: str,
        amount: float,
) -> None:
    categories[category] = categories.get(category, 0.0) + amount


def make_up_statistics(
        report_date: tuple[int, int, int],
) -> tuple[float, float, float, dict[str, float]]:
    total_capital: float = 0.0
    month_income: float = 0.0
    month_expenses: float = 0.0
    categories: dict[str, float] = {}

    for transaction in financial_transactions_storage:
        if not transaction or not _is_valid_transaction(transaction):
            continue

        t_date = transaction["date"]
        if not _date_leq(t_date, report_date):
            continue

        amount = float(transaction["amount"])
        is_cost = "category" in transaction

        total_capital += -amount if is_cost else amount

        if _is_same_month(t_date, report_date):
            if is_cost:
                month_expenses += amount
                category = transaction.get("category")
                if isinstance(category, str):
                    _update_category(categories, category, amount)
            else:
                month_income += amount

    return total_capital, month_income, month_expenses, categories


def _format_categories(categories: dict[str, float]) -> list[str]:
    result: list[str] = []
    sorted_items = sorted(categories.items(), key=lambda item: item[0])

    for index, (category, amount) in enumerate(sorted_items, start=1):
        result.append(f"{index}. {category}: {int(amount)}")

    return result


def format_stats(
        report_date_raw: str,
        stats: tuple[float, float, float, dict[str, float]],
) -> str:
    total_capital, month_income, month_expenses, categories = stats

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
    return "\n".join(lines)


def is_leap_year(year: int) -> bool:
    """
    Для заданного года определяет: високосный (True) или невисокосный (False).

    :param int year: Проверяемый год
    :return: Значение високосности.
    :rtype: bool
    """
    is_div_400 = year % 400 == 0
    is_div_4 = year % 4 == 0
    is_not_div_100 = year % 100 != 0
    return is_div_400 or (is_div_4 and is_not_div_100)


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

    financial_transactions_storage.append(
        {"amount": amount, "date": parsed_date},
    )
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

    if (
            common_category not in EXPENSE_CATEGORIES
            or direct_category not in EXPENSE_CATEGORIES[common_category]
    ):
        financial_transactions_storage.append({})
        return NOT_EXISTS_CATEGORY

    financial_transactions_storage.append(
        {
            "category": category_name,
            "amount": amount,
            "date": parsed_date,
        },
    )
    return OP_SUCCESS_MSG


def cost_categories_handler() -> str:
    result = [
        f"{common}::{sub}"
        for common, subcategories in EXPENSE_CATEGORIES.items()
        for sub in subcategories
    ]
    return "\n".join(result)



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
