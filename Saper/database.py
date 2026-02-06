import sqlite3
from config import database


def create_database():
    with sqlite3.connect(database) as conn:
        cursor = conn.cursor()
        cursor.execute('''
                    CREATE TABLE IF NOT EXISTS result (
                    key INTEGER PRIMARY KEY,
                    wins INTEGER,
                    loses INTEGER)
                ''')
        conn.commit()

        if get_wins() == None or get_loses() == None:
            cursor.execute('''
                                INSERT INTO result (wins, loses)
                                VALUES (0, 0) ''', ())
            conn.commit()


def add_win():
    with sqlite3.connect(database) as conn:
        cursor = conn.cursor()
        cursor.execute(f'''
                    UPDATE result
                    SET wins = {get_wins()[0] + 1}''')
        conn.commit()


def add_lose():
    with sqlite3.connect(database) as conn:
        cursor = conn.cursor()
        print(get_loses())
        cursor.execute(f'''
                    UPDATE result
                    SET loses = {get_loses()[0] + 1}''')
        conn.commit()


def get_wins():
    with sqlite3.connect(database) as conn:
        cursor = conn.cursor()
        cursor.execute('''SELECT wins FROM result''')
        wins = cursor.fetchone()
    return wins


def get_loses():
    with sqlite3.connect(database) as conn:
        cursor = conn.cursor()
        cursor.execute('''SELECT loses FROM result''')
        loses = cursor.fetchone()
    return loses


def clear_database():
    with sqlite3.connect(database) as conn:
        cursor = conn.cursor()
        cursor.execute(f'''DELETE FROM result''', ())
        conn.commit()

    create_database()