import sqlite3

# Creating The Database Table
connection = sqlite3.connect("AppData.db")
cursor = connection.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS AppData(
id INTEGER PRIMARY KEY,
username VARCHAR(255) NOT NULL,
password VARCHAR(255) NOT NULL,
salted_password VARCHAR(255) NOT NULL
)
""")

connection.commit()
connection.close()

