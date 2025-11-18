import os
import mysql.connector

def get_db():
    return mysql.connector.connect(
        host=os.environ.get("DB_HOST", "localhost"),
        user=os.environ.get("DB_USER", "root"),
        password=os.environ.get("DB_PASSWORD", "Phanvietvy107@"),
        database=os.environ.get("DB_NAME", "librarymanagementsystem"),
        port=int(os.environ.get("DB_PORT", 3306)),
    )
