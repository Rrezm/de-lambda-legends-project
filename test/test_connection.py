from src.EXTRACT.connection import connect_to_db, close_conn
import pytest

def test_connect_to_db_does_not_fail():
    try:
        conn = connect_to_db()
        close_conn(conn)
    except:
        pytest.fail("Unexpected connection error")

