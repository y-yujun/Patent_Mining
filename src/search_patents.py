import sqlite3
import pathlib
import random
import string

# get connection to database
def get_database(dp_path: str) -> sqlite3.Connection:
    path_to_lib = pathlib.Path(dp_path).absolute().as_uri()
    connection = None
    try:
        connection = sqlite3.connect(f"{path_to_lib}?mode=rw", uri=True)
    except sqlite3.OperationalError:
        print("Error: Database not found")
        exit(1)
    return connection

def create_faculty_database(college):
    connection = get_database("database/patents.db")
    db_cursor = connection.cursor()
    dbname = college.replace(' ', '').lower() + ''.join(random.choices(string.ascii_uppercase + string.digits, k=3))
    sql = """CREATE TABLE IF NOT EXISTS {name} (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            first_name TEXT,
            surname TEXT
            )"""
    db_cursor.execute(sql.format(name=dbname))
    connection.commit()
    connection.close()
    return dbname

def populate_faculty_database(dbname, clean_name_list):
    connection = get_database("database/patents.db")
    db_cursor = connection.cursor()
    sql = """INSERT INTO {name} (first_name, surname) VALUES (?, ?)"""
    db_cursor.executemany(sql.format(name=dbname), clean_name_list)
    connection.commit()
    connection.close() 

def read_query(connection, query):
    cursor = connection.cursor()
    result = None
    try:
        cursor.execute(query)
        result = cursor.fetchall()
    except sqlite3.OperationalError:
        print("Error: Invalid query")
    return result

def search_patents(dbname, college):
    connection = get_database("database/patents.db")
    sql = """
        SELECT i.first_name, f.first_name, f.surname, i.city, i.state, g.name, p.document_number, p.document_date, p.title_of_invention
        FROM {dbname} f
        LEFT JOIN inventors i ON f.surname = i.surname AND i.first_name LIKE '%' || f.first_name || '%'
        INNER JOIN grantees g ON i.document_number = g.document_number
        INNER JOIN patents p ON g.document_number = p.document_number
        WHERE g.name LIKE '%{c}%'
        GROUP BY p.title_of_invention, f.surname
        ORDER BY f.surname ASC;
        """
    results = read_query(connection, sql.format(dbname=dbname, c=college))
    connection.commit()
    connection.close() 
    return results 

def remove_temp_table(dbname):
    connection = get_database("database/patents.db")
    db_cursor = connection.cursor()
    sql = """DROP TABLE {name}"""
    db_cursor.execute(sql.format(name=dbname))
    connection.commit()
    connection.close() 