def dict_factory(cursor, row):
    """Used to extract results from a sqlite3 row by name"""
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d
