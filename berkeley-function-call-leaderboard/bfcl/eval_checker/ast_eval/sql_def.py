import json
from typing import List, Optional, Dict

def select(
    table_name: str,
    columns: Optional[List[str]] = None,
    conditions: Optional[List[Dict[str, str]]] = None,
    order_by: Optional[List[str]] = None,
    limit: Optional[int] = None
) -> str:
    """
    Generate a SQL SELECT query.

    Args:
        table_name (str): The name of the table to query.
        columns (List[str], optional): A list of column names to select. Defaults to ['*'] for all columns.
        conditions (List[Dict[str, str]], optional): A list of conditions in the form:
            [{'operator': 'AND', 'left': 'column_name', 'sign': '=', 'right': 'value'}].
        order_by (List[str], optional): A list of columns to order the result by.
        limit (int, optional): The maximum number of rows to return.

    Returns:
        str: The constructed SQL SELECT query.
    """
    cols_str = ", ".join(columns) if columns else "*"
    where_clause = ""
    if conditions:
        condition_strings = [
            f"{cond['left']} {cond['sign']} '{cond['right']}'" for cond in conditions
        ]
        where_clause = " WHERE " + f" {conditions[0]['operator']} ".join(condition_strings)
    order_clause = f" ORDER BY {', '.join(order_by)}" if order_by else ""
    limit_clause = f" LIMIT {limit}" if limit else ""
    return f"SELECT {cols_str} FROM {table_name}{where_clause}{order_clause}{limit_clause};"


def insert(
    table_name: str,
    columns: List[str],
    values: List[List[str]]
) -> str:
    """
    Generate a SQL INSERT query.

    Args:
        table_name (str): The name of the table to insert into.
        columns (List[str]): A list of column names for the INSERT operation.
        values (List[List[str]]): A list of rows, where each row is a list of values to insert.

    Returns:
        str: The constructed SQL INSERT query.
    """
    cols_str = f"({', '.join(columns)})"
    values_str = ", ".join([f"({', '.join([f'\'{val}\'' for val in row])})" for row in values])
    return f"INSERT INTO {table_name} {cols_str} VALUES {values_str};"


def update(
    table_name: str,
    columns: List[str],
    values: List[str],
    conditions: Optional[List[Dict[str, str]]] = None
) -> str:
    """
    Generate a SQL UPDATE query.

    Args:
        table_name (str): The name of the table to update.
        columns (List[str]): A list of column names to update.
        values (List[str]): A list of corresponding values to update.
        conditions (List[Dict[str, str]], optional): A list of conditions in the form:
            [{'operator': 'AND', 'left': 'column_name', 'sign': '=', 'right': 'value'}].

    Returns:
        str: The constructed SQL UPDATE query.
    """
    set_clause = ", ".join([f"{col} = '{val}'" for col, val in zip(columns, values)])
    where_clause = ""
    if conditions:
        condition_strings = [
            f"{cond['left']} {cond['sign']} '{cond['right']}'" for cond in conditions
        ]
        where_clause = " WHERE " + f" {conditions[0]['operator']} ".join(condition_strings)
    return f"UPDATE {table_name} SET {set_clause}{where_clause};"


def delete(
    table_name: str,
    conditions: Optional[List[Dict[str, str]]] = None
) -> str:
    """
    Generate a SQL DELETE query.

    Args:
        table_name (str): The name of the table to delete from.
        conditions (List[Dict[str, str]], optional): A list of conditions in the form:
            [{'operator': 'AND', 'left': 'column_name', 'sign': '=', 'right': 'value'}].

    Returns:
        str: The constructed SQL DELETE query.
    """
    where_clause = ""
    if conditions:
        condition_strings = [
            f"{cond['left']} {cond['sign']} '{cond['right']}'" for cond in conditions
        ]
        where_clause = " WHERE " + f" {conditions[0]['operator']} ".join(condition_strings)
    return f"DELETE FROM {table_name}{where_clause};"


def create(
    table_name: str,
    columns: List[str]
) -> str:
    """
    Generate a SQL CREATE query.

    Args:
        table_name (str): The name of the table to create.
        columns (List[str]): A list of column definitions, e.g., ['id INT PRIMARY KEY', 'name VARCHAR(255)'].

    Returns:
        str: The constructed SQL CREATE query.
    """
    columns_str = ", ".join(columns)
    return f"CREATE TABLE {table_name} ({columns_str});"