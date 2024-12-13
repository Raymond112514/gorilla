import json
import sys
import re

def build_conditions(conditions):
    if not conditions:
        return ""
    cond_strs = []
    for col, op, val in conditions:
        val = f"'{val}'"
        cond_strs.append(f"{col} {op} {val}")
    return " WHERE " + " AND ".join(cond_strs) if cond_strs else ""

def select(table_name, columns=None, conditions=None):
    """
    SELECT
    """
    cols_str = ", ".join(columns) if columns else "*"
    where_clause = build_conditions(conditions or [])
    return f"SELECT {cols_str} FROM {table_name}{where_clause};"

def insert(table_name, columns, insert_values):
    """
    INSERT
    """
    cols_str = f"({', '.join(columns)})"
    values_rows = []
    for row in insert_values:
        quoted = [f"'{v}'" for v in row]
        values_rows.append("(" + ", ".join(quoted) + ")")
    values_str = ", ".join(values_rows)
    return f"INSERT INTO {table_name} {cols_str} VALUES {values_str};"

def update(table_name, columns, update_values, conditions):
    """
    UPDATE
    """
    filtered_cols = []
    filtered_vals = []
    for c, v in zip(columns, update_values):
        if c.lower() != table_name.lower():
            v = v.rstrip('.')
            filtered_cols.append(c)
            filtered_vals.append(v)
    set_str = ", ".join([f"{c} = '{v}'" for c,v in zip(filtered_cols, filtered_vals)])
    where_clause = build_conditions(conditions or [])
    return f"UPDATE {table_name} SET {set_str}{where_clause};"

def delete(table_name, conditions):
    """
    DELETE
    """
    where_clause = build_conditions(conditions or [])
    return f"DELETE FROM {table_name}{where_clause};"

def create(table_name, columns):
    """
    CREATE
    """
    defs = [f"{c} VARCHAR(255)" for c in columns]
    return f"CREATE TABLE {table_name} ({', '.join(defs)});"

def detect_operation(question):
    ql = question.lower()
    if ("create" in ql or "generate" in ql) and "table" in ql:
        return "CREATE"
    if "change" in ql or "modify" in ql:
        return "UPDATE"
    if "remove" in ql or "erase" in ql or "delete" in ql:
        return "DELETE"
    if "add" in ql or "insert" in ql or "record" in ql or "store" in ql:
        return "INSERT"
    return "SELECT"

def extract_table_name(question):
    patterns = [
        r"table named ['\"]([\w_]+)['\"]",
        r"named ['\"]([\w_]+)['\"]",
        r"in the ['\"]([\w_]+)['\"] table",
        r"[\"']([\w_]+)[\"'] table",
        r"from the ['\"]([\w_]+)['\"] table"
    ]
    for pat in patterns:
        m = re.search(pat, question, re.IGNORECASE)
        if m:
            return m.group(1)
    m = re.search(r"['\"]([\w_]+)['\"] table", question, re.IGNORECASE)
    if m:
        return m.group(1)
    return None

def extract_conditions(question):
    conditions = []
    c_m = re.search(r"the condition ['\"](\w+)\s*=\s*(\w+)['\"]", question, re.IGNORECASE)
    if c_m:
        col, val = c_m.groups()
        conditions.append([col, "=", val])

    with_id = re.search(r"with the id\s+(\d+)", question, re.IGNORECASE)
    if with_id and not any(c[0]=="id" for c in conditions):
        conditions.append(["id", "=", with_id.group(1)])
    else:
        gen_id = re.search(r"\bID\s+(\d+)\b", question)
        if gen_id and not any(c[0]=="id" for c in conditions):
            conditions.append(["id", "=", gen_id.group(1)])

    cond_custom = re.search(r"with\s+['\"]?(\w+)['\"]?\s+(\d+)", question, re.IGNORECASE)
    if cond_custom:
        ccol, cval = cond_custom.groups()
        if not any(c[0].lower()==ccol.lower() for c in conditions):
            conditions.append([ccol, "=", cval])

    lt = re.search(r"(\w+)\s+(less than|<)\s+(\d+(\.\d+)?)", question, re.IGNORECASE)
    if lt:
        col, _, val, _ = lt
        conditions.append([col, "<", val])

    gt = re.search(r"(\w+)\s+(above|greater than|>)\s+(\d+(\.\d+)?)", question, re.IGNORECASE)
    if gt:
        col, _, val, _ = gt
        conditions.append([col, ">", val])

    return conditions

def extract_create_columns(question, table_name):
    all_quoted = re.findall(r"[\"'](\w+)[\"']", question)
    return [w for w in all_quoted if w.lower() != table_name.lower()]

def extract_select_columns(question, table_name):
    col_pattern = re.search(r"the columns\s+(.+?)(\?|$)", question, re.IGNORECASE)
    if col_pattern:
        segment = col_pattern.group(1)
        c_list = re.findall(r"[\"'](\w+)[\"']", segment)
        c_list = [c for c in c_list if c.lower() != table_name.lower() and not c.isdigit()]
        if c_list:
            return c_list
    all_quoted = re.findall(r"[\"']([^\"']+)[\"']", question)
    filtered = []
    for w in all_quoted:
        if w.lower() != table_name.lower() and not re.match(r"^\d+(\.\d+)?$", w):
            filtered.append(w)
    return filtered

def extract_update_info(question):
    matches = re.findall(r"[\"'](\w+)[\"'].*?\bto\b\s+[\"']?(\w+)[\"']?", question, re.IGNORECASE)
    if matches:
        cols, vals = zip(*matches)
        return list(cols), list(vals)
    return [], []

def extract_insert_info(question, known_columns):
    pattern = r"[\"'](\w+)[\"']\s+is\s+[\"']([^\"']+)[\"']"
    matches = re.findall(pattern, question, re.IGNORECASE)
    if matches:
        if known_columns:
            cols = []
            vals = []
            for c,v in matches:
                if c in known_columns:
                    cols.append(c)
                    vals.append(v)
            if len(cols) == len(known_columns):
                return cols, [vals]
        else:
            cols = [m[0] for m in matches]
            vals = [m[1] for m in matches]
            return cols, [vals]

    values_dict = {}

    name_match = re.search(r"named\s+'([^']+)'", question, re.IGNORECASE)
    if name_match and any(c.lower()=="name" for c in known_columns):
        values_dict["Name"] = name_match.group(1)

    id_match = re.search(r"with\s+(?:id|ID)\s+'([^']+)'", question)
    if id_match:
        val = id_match.group(1)
        cid = None
        for c in known_columns:
            if c.lower()=="studentid":
                cid = c
                break
        if not cid and "ID" in known_columns:
            cid = "ID"
        if cid:
            values_dict[cid] = val

    score_match = re.search(r"scored\s+'([^']+)'", question, re.IGNORECASE)
    if score_match:
        score_val = score_match.group(1)
        for c in known_columns:
            if c.lower()=="testscore":
                values_dict[c] = score_val
                break

    date_match = re.search(r"on\s+'(\d{4}-\d{2}-\d{2})'", question)
    if date_match:
        dt = date_match.group(1)
        for c in known_columns:
            if c.lower()=="testdate":
                values_dict[c] = dt
                break

    for col in known_columns:
        if col not in values_dict:
            pat = rf"\b{col}\b\s+is\s+'([^']+)'"
            m = re.search(pat, question, re.IGNORECASE)
            if m:
                values_dict[col] = m.group(1)

    if len(values_dict) == len(known_columns):
        vals = [values_dict[c] for c in known_columns]
        return known_columns, [vals]

    return [], []

def process_sql_json(json_data):
    question = json_data.get("question", [{}])[0].get("content", "")
    operation = detect_operation(question)
    table_name = extract_table_name(question)
    if not table_name:
        raise ValueError("Could not determine table name")

    conditions = extract_conditions(question)

    if operation == "CREATE":
        columns = extract_create_columns(question, table_name)
        return f"Processed: {json_data['id']}: {create(table_name, columns)}"

    elif operation == "UPDATE":
        cols, vals = extract_update_info(question)
        if not cols or not vals:
            raise ValueError("Could not determine columns/values for UPDATE")
        return f"Processed: {json_data['id']}: {update(table_name, cols, vals, conditions)}"

    elif operation == "DELETE":
        return f"Processed: {json_data['id']}: {delete(table_name, conditions)}"

    elif operation == "INSERT":
        col_mention = re.search(r"(columns?\s+named|with\s+the\s+columns|with\s+columns)", question, re.IGNORECASE)
        if col_mention:
            after_part = question[col_mention.end():]
            all_quoted = re.findall(r"[\"'](\w+)[\"']", after_part)
            known_columns = [c for c in all_quoted if c.lower()!=table_name.lower()]
        else:
            all_quoted = re.findall(r"[\"'](\w+)[\"']", question)
            known_columns = [w for w in all_quoted if w.lower()!=table_name.lower() and not w.isdigit()]

        cols, insert_vals = extract_insert_info(question, known_columns)
        if not cols or not insert_vals:
            raise ValueError("Could not determine columns/values for INSERT")
        return f"Processed: {json_data['id']}: {insert(table_name, cols, insert_vals)}"

    else:
        columns = extract_select_columns(question, table_name)
        return f"Processed: {json_data['id']}: {select(table_name, columns, conditions)}"

def process_file(input_file, output_file):
    with open(input_file, 'r') as infile, open(output_file, 'w') as outfile:
        for line in infile:
            line=line.strip()
            if not line:
                continue
            try:
                data = json.loads(line)
                result = process_sql_json(data)
                outfile.write(result+"\n")
                print(result)
            except json.JSONDecodeError as e:
                print(f"Error parsing JSON line: {e}")
            except Exception as e:
                print(f"Error processing query: {e}")

if __name__ == "__main__":
    if len(sys.argv)!=3:
        print("Usage: python script.py input_file output_file")
        sys.exit(1)
    input_file=sys.argv[1]
    output_file=sys.argv[2]
    process_file(input_file, output_file)
