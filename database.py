import sqlite3

add_usr_link = "INSERT INTO users (name, tg_id) VALUES (?, ?);"
add_buy_link = "INSERT INTO buy (product, count, list) VALUES (?, ?, ?);"
add_buylist_link = "INSERT INTO buylist (title, data) VALUES (?, CURRENT_DATE);"

del_buylist_link = "DELETE FROM buylist WHERE id = (?);"

check_user_link = "SELECT name FROM users WHERE tg_id = (?);"
check_buylist_link = "SELECT id FROM buy WHERE list = (?)"

view_buylist_link = "SELECT id, title FROM buylist;"
view_buy_link = "SELECT product, count FROM buy WHERE list = (?);"

def create_user_table(cursor):
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        tg_id INTEGER UNIQUE
    );

    ''')

def create_buylist_table(cursor):
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS buylist (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        data DATE NOT NULL DEFAULT CURRENT_DATE
    );

    ''')

def create_buy_table(cursor):
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS buy (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        product TEXT NOT NULL,
        count INTEGER,
        list INTEGER REFERENCES buylist(id) ON DELETE CASCADE
    );
                   
    ''')