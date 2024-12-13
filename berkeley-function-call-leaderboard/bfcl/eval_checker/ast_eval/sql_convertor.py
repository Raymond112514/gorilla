from typing import List, Optional, Dict, Union

def build_conditions(conditions):
    if not conditions:
        return ""
    cond_strs = []
    for col, op, val in conditions:
        val = f"'{val}'"
        cond_strs.append(f"{col} {op} {val}")
    return " WHERE " + " AND ".join(cond_strs) if cond_strs else ""

def select(table_name: str, columns: List[str], conditions: List[dict] = None, order_by: str = None, top: int = None, join: dict = None, group_by: str = None):
    """
    Select some columns from a table given conditions.

    Args:
        table_name (str): The name of the table to select from.
        columns (List[str]): The columns to select. If * is given, all columns are selected.
        conditions (List[dict]): A list of conditions to filter the rows by. Each condition is a dictionary with keys 'column', 'operator', and 'value'.
        order_by (str): The column to order the results by.
        top (int): The number of rows to return.
        join (dict): A dictionary with keys 'table', 'on', and 'type' to specify a join.
        group_by (str): The column to group the results by.
    """
    cols_str = ", ".join(columns) if columns else "*"
    where_clause = build_conditions(conditions or [])
    sql =  f"SELECT {cols_str} FROM {table_name}{where_clause}"
    if order_by:
        sql += f" ORDER BY {order_by}"
    if top:
        sql += f" LIMIT {top}"
    if join:
        sql += f" {join['type']} JOIN {join['table']} ON {join['on']}"
    if group_by:
        sql += f" GROUP BY {group_by}"
    return sql

def insert(
    table_name: str,
    columns: List[str],
    values: List[List[str]],
    returning: Optional[str] = None
) -> str:
    """
    Insert rows of data into a table with specified columns.

    Args:
        table_name (str): The name of the table to insert into.
        columns (List[str]): A list of column names for the INSERT operation.
        values (List[List[str]]): A list of rows, where each row is a list of values to insert.
        returning (str, optional): A column or set of columns to return after the insertion.

    Returns:
        str: The constructed SQL INSERT query.
    """
    cols_str = f"({', '.join(columns)})"
    values_str = ", ".join([f"({', '.join([f'\'{val}\'' for val in row])})" for row in values])
    sql = f"INSERT INTO {table_name} {cols_str} VALUES {values_str}"
    
    if returning:
        sql += f" RETURNING {returning}"
    
    return sql + ";"

def update(
    table_name: str,
    updates: List[Dict[str, str]],
    conditions: Optional[List[Dict[str, str]]] = None,
    returning: Optional[str] = None,
    limit: Optional[int] = None
) -> str:
    """
    Update values in specific columns of a table based on given conditions.

    Args:
        table_name (str): The name of the table to update.
        updates (List[Dict[str, str]]): A list of updates, each defined as {'column': 'col_name', 'value': 'new_value'}.
        conditions (List[Dict[str, str]], optional): A list of conditions, each defined as:
            {'operator': 'AND', 'left': 'column_name', 'sign': '=', 'right': 'value'}.
        returning (str, optional): A column or set of columns to return after the update.
        limit (int, optional): The maximum number of rows to update.

    Returns:
        str: The constructed SQL UPDATE query.
    """
    set_clause = ", ".join([f"{update['column']} = '{update['value']}'" for update in updates])
    where_clause = ""
    if conditions:
        condition_strings = [
            f"{cond['left']} {cond['sign']} '{cond['right']}'" for cond in conditions
        ]
        where_clause = " WHERE " + f" {conditions[0]['operator']} ".join(condition_strings)
    
    sql = f"UPDATE {table_name} SET {set_clause}{where_clause}"
    
    if returning:
        sql += f" RETURNING {returning}"
    
    if limit:
        sql += f" LIMIT {limit}"
    
    return sql + ";"


def delete(
    table_name: str,
    conditions: Optional[List[Dict[str, str]]] = None,
    returning: Optional[str] = None,
    limit: Optional[int] = None
) -> str:
    """
    Delete rows from a table that match given conditions.

    Args:
        table_name (str): The name of the table to delete from.
        conditions (List[Dict[str, str]], optional): A list of conditions, each defined as:
            {'operator': 'AND', 'left': 'column_name', 'sign': '=', 'right': 'value'}.
        returning (str, optional): A column or set of columns to return after the deletion.
        limit (int, optional): The maximum number of rows to delete.

    Returns:
        str: The constructed SQL DELETE query.
    """
    where_clause = ""
    if conditions:
        condition_strings = [
            f"{cond['left']} {cond['sign']} '{cond['right']}'" for cond in conditions
        ]
        where_clause = " WHERE " + f" {conditions[0]['operator']} ".join(condition_strings)
    
    sql = f"DELETE FROM {table_name}{where_clause}"
    
    if returning:
        sql += f" RETURNING {returning}"
    
    if limit:
        sql += f" LIMIT {limit}"
    
    return sql + ";"


def create(
    table_name: str,
    columns: List[Dict[str, str]],
    primary_key: Optional[str] = None,
    foreign_keys: Optional[List[Dict[str, str]]] = None,
    if_not_exists: bool = False,
    indexes: Optional[List[Dict[str, Union[str, bool]]]] = None,
    temporary: bool = False
) -> str:
    """
    Create a new table with specified columns and constraints.

    Args:
        table_name (str): The name of the table to create.
        columns (List[Dict[str, str]]): A list of column definitions, each defined as {'name': 'col_name', 'type': 'col_type', 'constraints': 'constraints'}.
        primary_key (str, optional): The column to use as the primary key.
        foreign_keys (List[Dict[str, str]], optional): A list of foreign key constraints, each defined as:
            {'column': 'col_name', 'references': 'ref_table(ref_col)', 'on_delete': 'action', 'on_update': 'action'}.
        if_not_exists (bool, optional): Whether to include the IF NOT EXISTS clause.
        indexes (List[Dict[str, Union[str, bool]]], optional): A list of indexes, each defined as {'name': 'index_name', 'columns': ['col1', 'col2'], 'unique': True/False}.
        temporary (bool, optional): Whether to create a temporary table.

    Returns:
        str: The constructed SQL CREATE TABLE query.
    """
    col_definitions = ", ".join([f"{col['name']} {col['type']} {col.get('constraints', '')}" for col in columns])
    
    sql = f"CREATE {'TEMPORARY ' if temporary else ''}TABLE {'IF NOT EXISTS ' if if_not_exists else ''}{table_name} ({col_definitions}"
    
    if primary_key:
        sql += f", PRIMARY KEY ({primary_key})"
    
    if foreign_keys:
        fk_clauses = [
            f", FOREIGN KEY ({fk['column']}) REFERENCES {fk['references']} ON DELETE {fk.get('on_delete', 'NO ACTION')} ON UPDATE {fk.get('on_update', 'NO ACTION')}"
            for fk in foreign_keys
        ]
        sql += "".join(fk_clauses)
    
    sql += ")"
    
    if indexes:
        for index in indexes:
            unique = "UNIQUE" if index.get('unique', False) else ""
            index_name = index['name']
            index_columns = ", ".join(index['columns'])
            sql += f"; CREATE {unique} INDEX {index_name} ON {table_name} ({index_columns})"
    
    return sql + ";"