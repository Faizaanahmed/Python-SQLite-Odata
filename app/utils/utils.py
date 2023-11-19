
def validate_table_name(table_name, db_path):
    # Connect to the SQLite database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Retrieve the list of tables in the database
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()

    # Close the database connection
    conn.close()

    # Extract table names and check if the provided name is among them
    table_names = [table[0] for table in tables]
    return table_name in table_names

def construct_get_query(tablename, query_params, top=None, skip=None, filter_option=None, select_option=None, orderby_option=None):
    # Base query
    query = f"SELECT {select_option if select_option else '*'} FROM {tablename}"

    # Adding a filter clause
    if filter_option:
        query += f" WHERE {filter_option}"

    # Adding ordering
    if orderby_option:
        query += f" ORDER BY {orderby_option}"

    # Adding limit and offset
    if top:
        query += f" LIMIT {top}"
    if skip:
        query += f" OFFSET {skip}"

    return query
