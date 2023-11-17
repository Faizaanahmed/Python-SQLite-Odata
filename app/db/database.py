
import sqlite3

def execute_query(query, params=None):
    with sqlite3.connect('chinook.db') as conn:
        cur = conn.cursor()
        if params:
            cur.execute(query, params)
        else:
            cur.execute(query)
        return cur.fetchall()

def execute_insert(query, params):
    with sqlite3.connect('chinook.db') as conn:
        cur = conn.cursor()
        cur.execute(query, params)
        conn.commit()
        return cur.lastrowid

def execute_update(query, params):
    with sqlite3.connect('chinook.db') as conn:
        cur = conn.cursor()
        cur.execute(query, params)
        conn.commit()
        return cur.rowcount

def execute_delete(query, params):
    with sqlite3.connect('chinook.db') as conn:
        cur = conn.cursor()
        cur.execute(query, params)
        conn.commit()
        return cur.rowcount
