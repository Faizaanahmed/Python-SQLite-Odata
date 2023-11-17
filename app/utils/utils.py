
def construct_get_query(tablename, query_params):
    if not validate_table_name(tablename, known_tables):
        raise ValueError('Invalid table name')
    base_query = f'SELECT * FROM {tablename}'
    where_clauses = []
    params = []

    # Handling OData $filter query option
    filter_param = query_params.get('$filter')
    if filter_param:
        # Basic implementation, needs to be adapted for complex filters
        # Parameterized approach for filter parameters
        filter_value = query_params.get('filter_value')
        where_clauses.append('column_name = ?')
        params.append(filter_value)
    
    # Constructing the WHERE clause
    if where_clauses:
        where_statement = ' WHERE ' + ' AND '.join(where_clauses)
        base_query += where_statement

    # Add more query options as needed (e.g., $select, $orderby)

    return base_query, params
