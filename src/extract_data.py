from connection import connect_to_db, close_conn
from pprint import pprint
import csv

def extract_lambda():
    conn = connect_to_db()
    result =  conn.run("SELECT * FROM sales_order;")
    keys = conn.run("SELECT column_name FROM information_schema.columns WHERE table_name = 'sales_order';")
    close_conn(conn)

    new_keys = [i for key in keys for i in key]
    print(keys)
    with open('output.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(new_keys)
        writer.writerows(result)

    
extract_lambda()