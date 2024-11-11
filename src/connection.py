from pg8000.native import Connection
from dotenv import load_dotenv
import os

load_dotenv(override=True)

def connect_to_db():
    return Connection(
        user=os.getenv("USER"),
        password=os.getenv("PASSWORD"),
        database=os.getenv("DATABASE"),
        host=os.getenv("HOST"),
        port=int(os.getenv("PORT"))
    )

def close_conn(conn):
    conn.close()