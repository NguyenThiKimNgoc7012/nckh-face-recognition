import sqlite3
import os

DB_PATH = "faceid.db"

def connectdatabase():
    try:
        con = sqlite3.connect(DB_PATH)
        return con
    except sqlite3.Error as err:
        print(f"Lỗi kết nối SQLite: {err}")
        return None

def create_table():
    con = connectdatabase()
    if con is None:
        return
    
    cursor = con.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS people (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            total_in_count INTEGER DEFAULT 0
        )
    ''')
    con.commit()
    con.close()

def insertOrUpdate(id, name):
    con = connectdatabase()
    if con is None:
        return None  # Trả về None nếu không kết nối được cơ sở dữ liệu

    cursor = con.cursor()
    query = "SELECT * FROM people WHERE id = ?"
    cursor.execute(query, (id,))
    record = cursor.fetchone()

    if record is None:
        query = "INSERT INTO people (id, name, total_in_count) VALUES (?, ?, ?)"
        cursor.execute(query, (id, name, 1))  # Thiết lập số lần nhận diện ban đầu là 1
    else:
        query = "UPDATE people SET name = ?, total_in_count = total_in_count + 1 WHERE id = ?"
        cursor.execute(query, (name, id))  # Cập nhật số lần nhận diện (tăng lên mỗi lần nhận diện)

    con.commit()
    con.close()
    return True  # Trả về True khi cập nhật thành công


def getProfile(id):
    conn = connectdatabase()
    if conn is None:
        return None
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM people WHERE id = ?", (id,))
    record = cursor.fetchone()
    conn.close()
    return record

def get_level(total_in_count):
    if total_in_count >= 20:
        return '- Gold'
    elif total_in_count >= 10:
        return '- Silver'
    else:
        return '- Copper'


create_table()
